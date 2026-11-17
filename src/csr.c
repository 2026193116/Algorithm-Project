#include <stdlib.h>

#include "csr.h"


// Dense 행렬을 CSR 형식으로 변환
int dense_to_csr(
    double **A,
    int rows,
    int cols,
    CSRMatrix *csr
) {
    if (A == NULL || csr == NULL || rows <= 0 || cols <= 0) {
        return 0;
    }

    csr->rows = rows;
    csr->cols = cols;
    csr->nnz = 0;
    csr->data = NULL;
    csr->indices = NULL;
    csr->indptr = NULL;

    // 0이 아닌 원소의 개수 계산
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (A[i][j] != 0.0) {
                csr->nnz++;
            }
        }
    }

    // 배열 메모리 할당
    csr->indptr = malloc((rows + 1) * sizeof(int));

    if (csr->indptr == NULL) {
        return 0;
    }

    if (csr->nnz > 0) {
        csr->data = malloc(csr->nnz * sizeof(double));
        csr->indices = malloc(csr->nnz * sizeof(int));

        if (csr->data == NULL || csr->indices == NULL) {
            free_csr(csr);
            return 0;
        }
    }

    // CSR 데이터 저장
    int k = 0;

    for (int i = 0; i < rows; i++) {

        csr->indptr[i] = k;

        for (int j = 0; j < cols; j++) {

            if (A[i][j] != 0.0) {
                csr->data[k] = A[i][j];
                csr->indices[k] = j;
                k++;
            }
        }
    }

    csr->indptr[rows] = k;

    return 1;
}


// CSR 행렬과 벡터의 곱셈
void csr_matvec(
    const CSRMatrix *csr,
    const double *x,
    double *y
) {
    for (int i = 0; i < csr->rows; i++) {

        y[i] = 0.0;

        for (int k = csr->indptr[i];
             k < csr->indptr[i + 1];
             k++) {

            int j = csr->indices[k];

            y[i] += csr->data[k] * x[j];
        }
    }
}


// CSR 메모리 해제
void free_csr(CSRMatrix *csr) {
    if (csr == NULL) {
        return;
    }

    free(csr->data);
    free(csr->indices);
    free(csr->indptr);

    csr->data = NULL;
    csr->indices = NULL;
    csr->indptr = NULL;

    csr->rows = 0;
    csr->cols = 0;
    csr->nnz = 0;
}
