
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "benchmark.h"
#include "dense.h"
#include "csr.h"
#include "csc.h"


#define SAMPLE_COUNT 7
#define TARGET_OPERATIONS 1000000LL

// 컴파일러가 계산 결과를 불필요한 연산으로 판단하지 않도록 사용
static volatile double benchmark_sink = 0.0;


// 현재 시각을 초 단위로 반환
static double get_time(void) {
    struct timespec ts;

    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return -1.0;
    }

    return (double)ts.tv_sec +
           (double)ts.tv_nsec / 1000000000.0;
}


// 측정값 정렬에 사용할 비교 함수
static int compare_double(const void *a, const void *b) {
    double x = *(const double *)a;
    double y = *(const double *)b;

    if (x < y) return -1;
    if (x > y) return 1;

    return 0;
}


// 중앙값 계산
static double median(double *values, int count) {
    qsort(
        values,
        count,
        sizeof(double),
        compare_double
    );

    if (count % 2 == 1) {
        return values[count / 2];
    }

    return (values[count / 2 - 1] +
            values[count / 2]) / 2.0;
}


// 행렬 크기에 따라 반복 횟수 결정
static int get_repetitions(int rows, int cols) {
    long long total_elements =
        (long long)rows * cols;

    long long repetitions =
        TARGET_OPERATIONS / total_elements;

    if (repetitions < 1) {
        repetitions = 1;
    }

    if (repetitions > 1000) {
        repetitions = 1000;
    }

    return (int)repetitions;
}


// Dense 행렬-벡터 곱셈 시간 측정
static double measure_dense(
    double **A,
    const double *x,
    double *y,
    int rows,
    int cols,
    int repetitions
) {
    double times[SAMPLE_COUNT];

    // 워밍업
    dense_matvec(A, x, y, rows, cols);

    for (int s = 0; s < SAMPLE_COUNT; s++) {

        double start = get_time();

        if (start < 0.0) {
            return -1.0;
        }

        for (int r = 0; r < repetitions; r++) {
            dense_matvec(A, x, y, rows, cols);
        }

        double end = get_time();

        if (end < 0.0) {
            return -1.0;
        }

        benchmark_sink = benchmark_sink + y[0];

        times[s] =
            (end - start) * 1000.0 / repetitions;
    }

    return median(times, SAMPLE_COUNT);
}


// CSR 행렬-벡터 곱셈 시간 측정
static double measure_csr(
    const CSRMatrix *csr,
    const double *x,
    double *y,
    int repetitions
) {
    double times[SAMPLE_COUNT];

    // 워밍업
    csr_matvec(csr, x, y);

    for (int s = 0; s < SAMPLE_COUNT; s++) {

        double start = get_time();

        if (start < 0.0) {
            return -1.0;
        }

        for (int r = 0; r < repetitions; r++) {
            csr_matvec(csr, x, y);
        }

        double end = get_time();

        if (end < 0.0) {
            return -1.0;
        }

        benchmark_sink = benchmark_sink + y[0];

        times[s] =
            (end - start) * 1000.0 / repetitions;
    }

    return median(times, SAMPLE_COUNT);
}


// CSC 행렬-벡터 곱셈 시간 측정
static double measure_csc(
    const CSCMatrix *csc,
    const double *x,
    double *y,
    int repetitions
) {
    double times[SAMPLE_COUNT];

    // 워밍업
    csc_matvec(csc, x, y);

    for (int s = 0; s < SAMPLE_COUNT; s++) {

        double start = get_time();

        if (start < 0.0) {
            return -1.0;
        }

        for (int r = 0; r < repetitions; r++) {
            csc_matvec(csc, x, y);
        }

        double end = get_time();

        if (end < 0.0) {
            return -1.0;
        }

        benchmark_sink = benchmark_sink + y[0];

        times[s] =
            (end - start) * 1000.0 / repetitions;
    }

    return median(times, SAMPLE_COUNT);
}


// Dense -> CSR 변환 시간 측정
static double measure_csr_conversion(
    double **A,
    int rows,
    int cols
) {
    double times[SAMPLE_COUNT];

    for (int s = 0; s < SAMPLE_COUNT; s++) {

        CSRMatrix temp = {0};

        double start = get_time();

        if (start < 0.0) {
            return -1.0;
        }

        int success = dense_to_csr(
            A,
            rows,
            cols,
            &temp
        );

        double end = get_time();

        if (!success) {
            free_csr(&temp);
            return -1.0;
        }

        if (end < 0.0) {
            free_csr(&temp);
            return -1.0;
        }

        times[s] = (end - start) * 1000.0;

        free_csr(&temp);
    }

    return median(times, SAMPLE_COUNT);
}


// Dense -> CSC 변환 시간 측정
static double measure_csc_conversion(
    double **A,
    int rows,
    int cols
) {
    double times[SAMPLE_COUNT];

    for (int s = 0; s < SAMPLE_COUNT; s++) {

        CSCMatrix temp = {0};

        double start = get_time();

        if (start < 0.0) {
            return -1.0;
        }

        int success = dense_to_csc(
            A,
            rows,
            cols,
            &temp
        );

        double end = get_time();

        if (!success) {
            free_csc(&temp);
            return -1.0;
        }

        if (end < 0.0) {
            free_csc(&temp);
            return -1.0;
        }

        times[s] = (end - start) * 1000.0;

        free_csc(&temp);
    }

    return median(times, SAMPLE_COUNT);
}


// 전체 벤치마크 실행
int benchmark_matvec(
    double **A,
    const double *x,
    int rows,
    int cols,
    int nnz,
    BenchmarkResult *result
) {
    if (A == NULL || x == NULL ||
        result == NULL ||
        rows <= 0 || cols <= 0 ||
        nnz < 0 || nnz > rows * (long long)cols) {
        return 0;
    }

    double *y = malloc(rows * sizeof(double));

    if (y == NULL) {
        return 0;
    }

    CSRMatrix csr = {0};
    CSCMatrix csc = {0};

    int repetitions = get_repetitions(rows, cols);

    // 1. Dense 곱셈 시간
    result->dense_matvec_ms = measure_dense(
        A, x, y, rows, cols, repetitions
    );

    // 2. CSR 변환 시간
    result->csr_conversion_ms =
        measure_csr_conversion(A, rows, cols);

    // 3. 실제 CSR 행렬 생성
    if (!dense_to_csr(A, rows, cols, &csr)) {
        free(y);
        return 0;
    }

    // 4. CSR 곱셈 시간
    result->csr_matvec_ms = measure_csr(
        &csr, x, y, repetitions
    );

    // 5. CSC 변환 시간
    result->csc_conversion_ms =
        measure_csc_conversion(A, rows, cols);

    // 6. 실제 CSC 행렬 생성
    if (!dense_to_csc(A, rows, cols, &csc)) {
        free_csr(&csr);
        free(y);
        return 0;
    }

    // 7. CSC 곱셈 시간
    result->csc_matvec_ms = measure_csc(
        &csc, x, y, repetitions
    );

    // 8. 메모리 사용량 계산
    result->dense_memory_bytes =
        (size_t)rows * cols * sizeof(double) +
        (size_t)rows * sizeof(double *);

    result->csr_memory_bytes =
        (size_t)nnz *
        (sizeof(double) + sizeof(int)) +
        (size_t)(rows + 1) * sizeof(int);

    result->csc_memory_bytes =
        (size_t)nnz *
        (sizeof(double) + sizeof(int)) +
        (size_t)(cols + 1) * sizeof(int);

    // 측정 오류 확인
    int valid =
        result->dense_matvec_ms >= 0.0 &&
        result->csr_conversion_ms >= 0.0 &&
        result->csr_matvec_ms >= 0.0 &&
        result->csc_conversion_ms >= 0.0 &&
        result->csc_matvec_ms >= 0.0;

    free_csr(&csr);
    free_csc(&csc);
    free(y);

    return valid;
}
