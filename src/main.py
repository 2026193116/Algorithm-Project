import os
import csv
import time
import statistics

from data_generator import generate_matrix
from dense import dense_matvec
from csr import dense_to_csr, csr_matvec
from csc import dense_to_csc, csc_matvec
from benchmark import benchmark_matvec


# 실험 조건
MATRIX_SIZES = [100, 500, 1000, 2000]

DENSITIES = [
    0.01,
    0.05,
    0.10,
    0.30,
    0.50
]

# 행렬 구조
STRUCTURES = [
    "random",
    "banded",
    "row",
    "block"
]

# 변환 시간 측정 반복 횟수
CONVERSION_REPEATS = 20

OUTPUT_PATH = "report/python_structure_results.csv"


# 변환 시간 중앙값 측정
def measure_conversion(
    conversion_function,
    repeats=CONVERSION_REPEATS
):

    times = []

    # 워밍업
    converted = conversion_function()
    del converted

    for _ in range(repeats):

        start = time.perf_counter()

        converted = conversion_function()

        end = time.perf_counter()

        times.append((end - start) * 1000)

        # 변환 결과 참조 해제
        del converted

    return statistics.median(times)


# 두 결과의 정확성 비교
def compare_results(
    result,
    expected,
    tolerance=1e-9
):

    if len(result) != len(expected):
        return False

    for a, b in zip(result, expected):

        if abs(a - b) > tolerance:
            return False

    return True


# CSV에 저장할 데이터 생성
def make_csv_row(
    structure,
    algorithm,
    rows,
    cols,
    density,
    nnz,
    actual_density,
    conversion_ms,
    matvec_ms,
    memory_bytes,
    valid
):

    return {
        "language": "Python",
        "structure": structure.capitalize(),
        "algorithm": algorithm,
        "rows": rows,
        "cols": cols,
        "density": density,
        "nnz": nnz,
        "actual_density": actual_density,
        "conversion_ms": conversion_ms,
        "matvec_ms": matvec_ms,
        "memory_bytes": memory_bytes,
        "valid": int(valid)
    }


# 하나의 실험 조건 실행
def run_test(rows, cols, density, structure):

    print("\n====================================")

    print(f"Matrix size: {rows} x {cols}")
    print(f"Structure: {structure.capitalize()}")
    print(f"Target density: {density * 100:.2f}%")

    # 1. 지정된 구조의 행렬 생성
    A = generate_matrix(
        rows,
        cols,
        density,
        seed=42,
        structure=structure
    )

    # 2. 실제 비제로 원소 개수 계산
    nnz = sum(
        1
        for row in A
        for value in row
        if value != 0
    )

    # 3. 실제 Density 계산
    actual_density = nnz / (rows * cols)

    print(f"Actual density: {actual_density * 100:.2f}%")
    print(f"Non-zero elements: {nnz}")

    # 4. 입력 벡터 생성
    x = [
        float(j % 5 + 1)
        for j in range(cols)
    ]

    # 5. Dense 계산
    dense_result = dense_matvec(A, x)

    # 6. CSR 변환 시간 측정
    csr_conversion_ms = measure_conversion(
        lambda: dense_to_csr(A)
    )

    # CSR 변환 및 계산
    csr_data, csr_indices, csr_indptr = dense_to_csr(A)

    csr_result = csr_matvec(
        csr_data,
        csr_indices,
        csr_indptr,
        x
    )

    # 7. CSC 변환 시간 측정
    csc_conversion_ms = measure_conversion(
        lambda: dense_to_csc(A)
    )

    # CSC 변환 및 계산
    csc_data, csc_indices, csc_indptr = dense_to_csc(A)

    csc_result = csc_matvec(
        csc_data,
        csc_indices,
        csc_indptr,
        x,
        rows
    )

    # 8. 정확성 검증
    csr_valid = compare_results(
        csr_result,
        dense_result
    )

    csc_valid = compare_results(
        csc_result,
        dense_result
    )

    print("------------------------------------")

    print("Dense correctness: PASS")
    print(f"CSR correctness: {'PASS' if csr_valid else 'FAIL'}")
    print(f"CSC correctness: {'PASS' if csc_valid else 'FAIL'}")

    if not csr_valid or not csc_valid:
        raise RuntimeError("Correctness verification failed.")

    # 9. 기존 benchmark.py를 활용한 성능 측정
    benchmark_results = benchmark_matvec(A, x)

    dense_stats = benchmark_results["Dense"]
    csr_stats = benchmark_results["CSR"]
    csc_stats = benchmark_results["CSC"]

    # 10. 화면 출력
    print("------------------------------------")

    print(
        f"Dense matvec: "
        f"{dense_stats['time_ms']:.8f} ms"
    )

    print(
        f"CSR conversion: "
        f"{csr_conversion_ms:.8f} ms"
    )

    print(
        f"CSR matvec: "
        f"{csr_stats['time_ms']:.8f} ms"
    )

    print(
        f"CSC conversion: "
        f"{csc_conversion_ms:.8f} ms"
    )

    print(
        f"CSC matvec: "
        f"{csc_stats['time_ms']:.8f} ms"
    )

    print("------------------------------------")

    print(
        f"Dense memory: "
        f"{dense_stats['memory_bytes']} bytes"
    )

    print(
        f"CSR memory: "
        f"{csr_stats['memory_bytes']} bytes"
    )

    print(
        f"CSC memory: "
        f"{csc_stats['memory_bytes']} bytes"
    )

    # 11. CSV 데이터 생성
    rows_to_save = [

        make_csv_row(
            structure,
            "Dense",
            rows,
            cols,
            density,
            nnz,
            actual_density,
            0.0,
            dense_stats["time_ms"],
            dense_stats["memory_bytes"],
            True
        ),

        make_csv_row(
            structure,
            "CSR",
            rows,
            cols,
            density,
            nnz,
            actual_density,
            csr_conversion_ms,
            csr_stats["time_ms"],
            csr_stats["memory_bytes"],
            csr_valid
        ),

        make_csv_row(
            structure,
            "CSC",
            rows,
            cols,
            density,
            nnz,
            actual_density,
            csc_conversion_ms,
            csc_stats["time_ms"],
            csc_stats["memory_bytes"],
            csc_valid
        )
    ]

    return rows_to_save


# 전체 실험 실행
def main():

    # report 폴더 생성
    os.makedirs("report", exist_ok=True)

    all_results = []

    total_tests = (
        len(MATRIX_SIZES)
        * len(DENSITIES)
        * len(STRUCTURES)
    )

    current_test = 0

    print("Starting Python structure benchmark...")
    print(f"Total experiment conditions: {total_tests}")

    # 전체 실험 실행
    for size in MATRIX_SIZES:

        for density in DENSITIES:

            for structure in STRUCTURES:

                current_test += 1

                print(
                    f"\n[Test {current_test}/{total_tests}]"
                )

                results = run_test(
                    size,
                    size,
                    density,
                    structure
                )

                all_results.extend(results)

    # CSV 저장
    fieldnames = [
        "language",
        "structure",
        "algorithm",
        "rows",
        "cols",
        "density",
        "nnz",
        "actual_density",
        "conversion_ms",
        "matvec_ms",
        "memory_bytes",
        "valid"
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(all_results)

    print("\n====================================")
    print("All Python structure benchmark tests completed!")
    print(f"Total experiment conditions: {total_tests}")
    print(f"Total data rows: {len(all_results)}")
    print(f"Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
