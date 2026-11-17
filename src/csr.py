def dense_to_csr(A):
    m = len(A)

    if m == 0 or len(A[0]) == 0:
        raise ValueError("Matrix must not be empty.")

    n = len(A[0])

    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be rectangular.")

    data = []
    indices = []
    indptr = [0]

    for i in range(m):
        for j in range(n):
            if A[i][j] != 0:
                data.append(A[i][j])
                indices.append(j)

        indptr.append(len(data))

    return data, indices, indptr


def csr_matvec(data, indices, indptr, x):
    m = len(indptr) - 1

    y = [0.0] * m

    for i in range(m):
        for k in range(indptr[i], indptr[i + 1]):
            j = indices[k]
            y[i] += data[k] * x[j]

    return y
