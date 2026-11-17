def dense_to_csc(A):
    m = len(A)

    if m == 0 or len(A[0]) == 0:
        raise ValueError("Matrix must not be empty.")

    n = len(A[0])

    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be rectangular.")

    data = []
    indices = []
    indptr = [0]

    for j in range(n):
        for i in range(m):
            if A[i][j] != 0:
                data.append(A[i][j])
                indices.append(i)

        indptr.append(len(data))

    return data, indices, indptr


def csc_matvec(data, indices, indptr, x, m):
    n = len(indptr) - 1

    if len(x) != n:
        raise ValueError("Matrix and vector dimensions do not match.")

    y = [0.0] * m

    for j in range(n):
        for k in range(indptr[j], indptr[j + 1]):
            i = indices[k]
            y[i] += data[k] * x[j]

    return y
