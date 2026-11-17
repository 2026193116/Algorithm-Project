def dense_to_csc(A):
    m = len(A)
    n = len(A[0])

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
    y = [0.0] * m

    for j in range(n):
        for k in range(indptr[j], indptr[j + 1]):
            i = indices[k]
            y[i] += data[k] * x[j]

    return y
