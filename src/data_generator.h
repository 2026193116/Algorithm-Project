#ifndef DATA_GENERATOR_H
#define DATA_GENERATOR_H

double **generate_matrix(
    int rows,
    int cols,
    double density,
    int *nnz
);

void free_matrix(double **A, int rows);

#endif
