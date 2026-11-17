
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "dense.h"
#include "csr.h"
#include "csc.h"
#include "data_generator.h"
#include "benchmark.h"


// 두 결과가 같은지 확인
int compare_results(
    const double *result,
    const double *expected,
    int size
) {
    for (int i = 0; i < size; i++) {
        if (fabs(result[i] - expected[i]) > 1e-9) {
            return 0;
        }
    }

    return 1;
}


// CSV에 실험 결과 기록
void write_csv(
    FILE *fp,
    const char *algorithm,
    int rows,
    int cols,
    double density,
    int nnz,
    double actual_density,
    double conversion_ms,
    double matvec_ms,
    size_t memory_bytes,
    int valid
) {
    fprintf(
        fp,
        "C,%s,%d,%d,%.4f,%d,%.8f,%.8f,%.8f,%zu,%d\n",
        algorithm,
        rows,
        cols,
        density,
        nnz,
        actual_density,
        conversion_ms,
        matvec_ms,
        memory_bytes,
        valid
    );
}


// 하나의 실험 조건 실행
void run_test(
    FILE *fp,
    int rows,
    int cols,
    double density
) {
    int nnz = 0;

    // 행렬 생성
    double **A = generate_matrix(
        rows,
        cols,
        density,
        &nnz
    );

    if (A == NULL) {
        printf("Matrix generation failed.\n");
        exit(EXIT_FAILURE);
    }

    // 실제 Density 계산
    double actual_density =
        (double)nnz / ((double)rows * cols);

    // 입력 벡터와 결과 배열 할당
    double *x = malloc(cols * sizeof(double));

    double *dense_result = malloc(rows * sizeof(double));
    double *csr_result = malloc(rows * sizeof(double));
    double *csc_result = malloc(rows * sizeof(double));

    if (x == NULL ||
        dense_result == NULL ||
        csr_result == NULL ||
        csc_result == NULL) {

        printf("Memory allocation failed.\n");

        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);
        free_matrix(A, rows);

        exit(EXIT_FAILURE);
    }

    // 입력 벡터 생성
    for (int j = 0; j < cols; j++) {
        x[j] = (double)(j % 5 + 1);
    }

    // CSR 및 CSC 구조체 초기화
    CSRMatrix csr = {0};
    CSCMatrix csc = {0};

    // Dense 계산
    dense_matvec(
        A,
        x,
        dense_result,
        rows,
        cols
    );

    // CSR 변환 및 계산
    if (!dense_to_csr(A, rows, cols, &csr)) {
        printf("CSR conversion failed.\n");

        free_matrix(A, rows);
        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);

        exit(EXIT_FAILURE);
    }

    csr_matvec(&csr, x, csr_result);

    // CSC 변환 및 계산
    if (!dense_to_csc(A, rows, cols, &csc)) {
        printf("CSC conversion failed.\n");

        free_csr(&csr);
        free_matrix(A, rows);
        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);

        exit(EXIT_FAILURE);
    }

    csc_matvec(&csc, x, csc_result);

    // 정확성 검증
    int csr_valid = compare_results(
        csr_result,
        dense_result,
        rows
    );

    int csc_valid = compare_results(
        csc_result,
        dense_result,
        rows
    );

    int all_valid = csr_valid && csc_valid;

    printf("\n====================================\n");

    printf("Matrix size: %d x %d\n", rows, cols);
    printf("Target density: %.2f%%\n", density * 100.0);
    printf("Actual density: %.2f%%\n", actual_density * 100.0);
    printf("Non-zero elements: %d\n", nnz);

    printf("------------------------------------\n");

    printf("Dense correctness: PASS\n");
    printf("CSR correctness: %s\n", csr_valid ? "PASS" : "FAIL");
    printf("CSC correctness: %s\n", csc_valid ? "PASS" : "FAIL");

    // 정확성 검증이 실패하면 측정하지 않음
    if (!all_valid) {
        free_csr(&csr);
        free_csc(&csc);
        free_matrix(A, rows);

        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);

        exit(EXIT_FAILURE);
    }

    // 벤치마크 결과 구조체
    BenchmarkResult result = {0};

    // 성능 측정
    if (!benchmark_matvec(
        A,
        x,
        rows,
        cols,
        nnz,
        &result
    )) {
        printf("Benchmark failed.\n");

        free_csr(&csr);
        free_csc(&csc);
        free_matrix(A, rows);

        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);

        exit(EXIT_FAILURE);
    }

    // 화면에 성능 측정 결과 출력
    printf("------------------------------------\n");

    printf(
        "Dense matvec: %.8f ms\n",
        result.dense_matvec_ms
    );

    printf(
        "CSR conversion: %.8f ms\n",
        result.csr_conversion_ms
    );

    printf(
        "CSR matvec: %.8f ms\n",
        result.csr_matvec_ms
    );

    printf(
        "CSC conversion: %.8f ms\n",
        result.csc_conversion_ms
    );

    printf(
        "CSC matvec: %.8f ms\n",
        result.csc_matvec_ms
    );

    printf("------------------------------------\n");

    printf(
        "Dense memory: %zu bytes\n",
        result.dense_memory_bytes
    );

    printf(
        "CSR memory: %zu bytes\n",
        result.csr_memory_bytes
    );

    printf(
        "CSC memory: %zu bytes\n",
        result.csc_memory_bytes
    );

    // CSV 저장
    write_csv(
        fp, "Dense",
        rows, cols, density,
        nnz, actual_density,
        0.0,
        result.dense_matvec_ms,
        result.dense_memory_bytes,
        1
    );

    write_csv(
        fp, "CSR",
        rows, cols, density,
        nnz, actual_density,
        result.csr_conversion_ms,
        result.csr_matvec_ms,
        result.csr_memory_bytes,
        csr_valid
    );

    write_csv(
        fp, "CSC",
        rows, cols, density,
        nnz, actual_density,
        result.csc_conversion_ms,
        result.csc_matvec_ms,
        result.csc_memory_bytes,
        csc_valid
    );

    // 메모리 해제
    free_csr(&csr);
    free_csc(&csc);

    free(x);
    free(dense_result);
    free(csr_result);
    free(csc_result);

    free_matrix(A, rows);
}


int main(void) {

    srand(42);

    // 행렬 크기
    int matrix_sizes[] = {
        100,
        500,
        1000,
        2000
    };

    // Density
    double densities[] = {
        0.01,
        0.05,
        0.10,
        0.30,
        0.50
    };

    int size_count =
        sizeof(matrix_sizes) / sizeof(matrix_sizes[0]);

    int density_count =
        sizeof(densities) / sizeof(densities[0]);

    // CSV 파일 생성
    FILE *fp = fopen("report/c_results.csv", "w");

    if (fp == NULL) {
        printf("CSV file creation failed.\n");
        return EXIT_FAILURE;
    }

    // CSV 헤더
    fprintf(
        fp,
        "language,algorithm,rows,cols,density,"
        "nnz,actual_density,"
        "conversion_ms,matvec_ms,memory_bytes,valid\n"
    );

    // 전체 실험 실행
    for (int i = 0; i < size_count; i++) {

        for (int j = 0; j < density_count; j++) {

            run_test(
                fp,
                matrix_sizes[i],
                matrix_sizes[i],
                densities[j]
            );
        }
    }

    fclose(fp);

    printf("\n====================================\n");
    printf("All benchmark tests completed!\n");
    printf("Results saved to report/c_results.csv\n");

    return EXIT_SUCCESS;
}
