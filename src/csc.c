#include <stdlib.h>

#include "csc.h"


// Dense 행렬을 CSC 형식으로 변환
int dense_to_csc(
    double **A,
    int rows,
    int cols,
    CSCMatrix *csc
) {
    if (A == NULL || csc == NULL || rows <= 0 || cols <= 0) {
        return 0;
    }

    csc->rows = rows;
    csc->cols = cols;
    csc->nnz = 0;
    csc->data = NULL;
    csc->indices = NULL;
    csc->indptr = NULL;

    // 0이 아닌 원소의 개수 계산
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (A[i][j] != 0.0) {
                csc->nnz++;
            }
        }
    }

    // 배열 메모리 할당
    csc->indptr = malloc((cols + 1) * sizeof(int));

    if (csc->indptr == NULL) {
        return 0;
    }

    if (csc->nnz > 0) {
        csc->data = malloc(csc->nnz * sizeof(double));
        csc->indices = malloc(csc->nnz * sizeof(int));

        if (csc->data == NULL || csc->indices == NULL) {
            free_csc(csc);
            return 0;
        }
    }

    // CSC 데이터 저장
    int k = 0;

    for (int j = 0; j < cols; j++) {

        csc->indptr[j] = k;

        for (int i = 0; i < rows; i++) {

            if (A[i][j] != 0.0) {
                csc->data[k] = A[i][j];
                csc->indices[k] = i;
                k++;
            }
        }
    }

    csc->indptr[cols] = k;

    return 1;
}


// CSC 행렬과 벡터의 곱셈
void csc_matvec(
    const CSCMatrix *csc,
    const double *x,
    double *y
) {
    // 결과 벡터 초기화
    for (int i = 0; i < csc->rows; i++) {
        y[i] = 0.0;
    }

    // 각 열을 순회
    for (int j = 0; j < csc->cols; j++) {

        for (int k = csc->indptr[j];
             k < csc->indptr[j + 1];
             k++) {

            int i = csc->indices[k];

            y[i] += csc->data[k] * x[j];
        }
    }
}


// CSC 메모리 해제
void free_csc(CSCMatrix *csc) {
    if (csc == NULL) {
        return;
    }

    free(csc->data);
    free(csc->indices);
    free(csc->indptr);

    csc->data = NULL;
    csc->indices = NULL;
    csc->indptr = NULL;

    csc->rows = 0;
    csc->cols = 0;
    csc->nnz = 0;
}
