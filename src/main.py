from dense import dense_matvec
from csr import dense_to_csr, csr_matvec
from csc import dense_to_csc, csc_matvec
from data_generator import generate_matrix
from benchmark import benchmark_matvec

def run_test(rows, cols, density):
    # 행렬 생성
    A = generate_matrix(rows, cols, density)

    # 벡터 생성
    x = [1] * cols

    # 실제 0이 아닌 원소의 개수 확인
    nnz = sum(
        1 for row in A for value in row if value != 0
    )

    # Dense
    dense_result = dense_matvec(A, x)

    # CSR
    data, indices, indptr = dense_to_csr(A)
    csr_result = csr_matvec(data, indices, indptr, x)

    # CSC
    data, indices, indptr = dense_to_csc(A)
    csc_result = csc_matvec(data, indices, indptr, x, rows)

    # 결과 검증
    assert dense_result == csr_result
    assert dense_result == csc_result

    print(f"\nMatrix size: {rows} x {cols}")
    print(f"Target density: {density:.0%}")
    print(f"Actual density: {nnz / (rows * cols):.2%}")
    print(f"Non-zero elements: {nnz}")
    print("All algorithms produced the same result.")
    
    # 성능 측정
    results = benchmark_matvec(A, x)

    print("\n[Performance Results]")

    for algorithm, result in results.items():
        print(f"\n{algorithm}")
        print(f"Execution time: {result['time_ms']:.6f} ms")
        print(f"Memory usage: {result['memory_bytes']} bytes")


def main():
    test_cases = [
        (3, 3, 0.5),
        (5, 8, 0.2),
        (100, 100, 0.05),
        (500, 500, 0.01),
    ]

    for rows, cols, density in test_cases:
        run_test(rows, cols, density)

    print("\nAll correctness tests passed!")


if __name__ == "__main__":
    main()
