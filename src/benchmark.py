import sys
import time
import statistics

from dense import dense_matvec
from csr import dense_to_csr, csr_matvec
from csc import dense_to_csc, csc_matvec


# 중복 객체를 제외하고 메모리 크기 계산
def get_memory_size(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)

    if obj_id in seen:
        return 0

    seen.add(obj_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, (list, tuple)):
        for item in obj:
            size += get_memory_size(item, seen)

    return size


# 실행 시간 측정
def measure_time(func, repeats=20):
    # 최초 실행은 준비 과정으로 사용
    func()

    times = []

    for _ in range(repeats):
        start = time.perf_counter()
        func()
        end = time.perf_counter()

        times.append(end - start)

    return statistics.median(times) * 1000


# 세 알고리즘의 성능 측정
def benchmark_matvec(A, x):
    m = len(A)
    n = len(A[0])

    # CSR, CSC 변환
    csr_data, csr_indices, csr_indptr = dense_to_csr(A)
    csc_data, csc_indices, csc_indptr = dense_to_csc(A)

    # 알고리즘별 실행 함수
    dense_func = lambda: dense_matvec(A, x)
    csr_func = lambda: csr_matvec(
        csr_data, csr_indices, csr_indptr, x
    )
    csc_func = lambda: csc_matvec(
        csc_data, csc_indices, csc_indptr, x, m
    )

    # 실행 시간 측정
    dense_time = measure_time(dense_func)
    csr_time = measure_time(csr_func)
    csc_time = measure_time(csc_func)

    # 메모리 사용량 측정
    dense_memory = get_memory_size(A)

    csr_memory = get_memory_size(
        [csr_data, csr_indices, csr_indptr]
    )

    csc_memory = get_memory_size(
        [csc_data, csc_indices, csc_indptr]
    )

    return {
        "Dense": {
            "time_ms": dense_time,
            "memory_bytes": dense_memory
        },
        "CSR": {
            "time_ms": csr_time,
            "memory_bytes": csr_memory
        },
        "CSC": {
            "time_ms": csc_time,
            "memory_bytes": csc_memory
        }
    }
