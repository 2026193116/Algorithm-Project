#ifndef CSR_H
#define CSR_H

typedef struct {
    int rows;
    int cols;
    int nnz;

    double *data;
    int *indices;
    int *indptr;

} CSRMatrix;


// Dense 행렬을 CSR 형식으로 변환
int dense_to_csr(
    double **A,
    int rows,
    int cols,
    CSRMatrix *csr
);


// CSR 행렬과 벡터의 곱셈
void csr_matvec(
    const CSRMatrix *csr,
    const double *x,
    double *y
);


// CSR 메모리 해제
void free_csr(CSRMatrix *csr);

#endif
