#ifndef DENSE_H
#define DENSE_H

void dense_matvec(
    double **A,
    const double *x,
    double *y,
    int rows,
    int cols
);

#endif
