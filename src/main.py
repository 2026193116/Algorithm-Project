from dense import dense_matvec
from csr import dense_to_csr, csr_matvec
from csc import dense_to_csc, csc_matvec


def main():
    A = [
        [1, 0, 2],
        [0, 3, 0],
        [4, 0, 5]
    ]

    x = [1, 2, 3]

    expected = [7, 6, 19]

    # Dense
    dense_result = dense_matvec(A, x)

    # CSR
    data, indices, indptr = dense_to_csr(A)
    csr_result = csr_matvec(data, indices, indptr, x)

    # CSC
    data, indices, indptr = dense_to_csc(A)
    csc_result = csc_matvec(data, indices, indptr, x, len(A))

    print("Dense:", dense_result)
    print("CSR:  ", csr_result)
    print("CSC:  ", csc_result)

    assert dense_result == expected
    assert csr_result == expected
    assert csc_result == expected

    print("All correctness tests passed!")


if __name__ == "__main__":
    main()
