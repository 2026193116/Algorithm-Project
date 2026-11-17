
#ifndef BENCHMARK_H
#define BENCHMARK_H

#include <stddef.h>

typedef struct {
    double dense_matvec_ms;

    double csr_conversion_ms;
    double csr_matvec_ms;

    double csc_conversion_ms;
    double csc_matvec_ms;

    size_t dense_memory_bytes;
    size_t csr_memory_bytes;
    size_t csc_memory_bytes;

} BenchmarkResult;


// Dense, CSR, CSC의 성능 측정
int benchmark_matvec(
    double **A,
    const double *x,
    int rows,
    int cols,
    int nnz,
    BenchmarkResult *result
);

#endif
