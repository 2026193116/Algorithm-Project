def dense_matvec(A, x):
    m = len(A)

    if m == 0:
        raise ValueError("Matrix must not be empty.")

    n = len(A[0])

    if n == 0 or len(x) != n:
        raise ValueError("Matrix and vector dimensions do not match.")

    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be rectangular.")

    y = [0.0] * m

    for i in range(m):
        for j in range(n):
            y[i] += A[i][j] * x[j]

    return y
