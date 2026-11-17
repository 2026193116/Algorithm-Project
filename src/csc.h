#ifndef CSC_H
#define CSC_H

typedef struct {
    int rows;
    int cols;
    int nnz;

    double *data;
    int *indices;
    int *indptr;

} CSCMatrix;


// Dense 행렬을 CSC 형식으로 변환
int dense_to_csc(
    double **A,
    int rows,
    int cols,
    CSCMatrix *csc
);


// CSC 행렬과 벡터의 곱셈
void csc_matvec(
    const CSCMatrix *csc,
    const double *x,
    double *y
);


// CSC 메모리 해제
void free_csc(CSCMatrix *csc);

#endif
