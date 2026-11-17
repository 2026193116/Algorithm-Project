#ifndef DATA_GENERATOR_H
#define DATA_GENERATOR_H

typedef enum {
    MATRIX_RANDOM,
    MATRIX_BANDED,
    MATRIX_ROW,
    MATRIX_BLOCK
} MatrixStructure;

// 기존 Random 행렬 생성 함수
double **generate_matrix(
    int rows,
    int cols,
    double density,
    int *nnz
);

// 구조를 지정하여 행렬 생성하는 함수
double **generate_matrix_by_structure(
    int rows,
    int cols,
    double density,
    MatrixStructure structure,
    int *nnz
);

// 행렬 메모리 해제
void free_matrix(double **A, int rows);

#endif
