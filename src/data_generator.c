#include <stdio.h>
#include <stdlib.h>

#include "data_generator.h"


double **generate_matrix(
    int rows,
    int cols,
    double density,
    int *nnz
) {
    if (rows <= 0 || cols <= 0) {
        return NULL;
    }

    if (density < 0.0 || density > 1.0) {
        return NULL;
    }

    // 행 포인터 배열 동적 할당
    double **A = malloc(rows * sizeof(double *));

    if (A == NULL) {
        return NULL;
    }

    // 각 행에 대한 메모리 할당
    for (int i = 0; i < rows; i++) {
        A[i] = malloc(cols * sizeof(double));

        if (A[i] == NULL) {
            for (int k = 0; k < i; k++) {
                free(A[k]);
            }

            free(A);
            return NULL;
        }
    }

    *nnz = 0;

    // 행렬 원소 생성
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {

            double random_value =
                (double)rand() / RAND_MAX;

            if (random_value < density) {
                A[i][j] = (double)(rand() % 10 + 1);
                (*nnz)++;
            }
            else {
                A[i][j] = 0.0;
            }
        }
    }

    return A;
}


// 행렬 메모리 해제
void free_matrix(double **A, int rows) {
    if (A == NULL) {
        return;
    }

    for (int i = 0; i < rows; i++) {
        free(A[i]);
    }

    free(A);
}
