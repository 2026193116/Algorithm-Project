def dense_matvec(A, x):
    m = len(A)
    n = len(A[0])

    y = [0.0] * m

    for i in range(m):
        for j in range(n):
            y[i] += A[i][j] * x[j]

    return y
