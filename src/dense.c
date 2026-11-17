#include "dense.h"

void dense_matvec(
    double **A,
    const double *x,
    double *y,
    int rows,
    int cols
) {
    for (int i = 0; i < rows; i++) {
        y[i] = 0.0;

        for (int j = 0; j < cols; j++) {
            y[i] += A[i][j] * x[j];
        }
    }
}
