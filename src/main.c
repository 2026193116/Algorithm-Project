#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "dense.h"
#include "csr.h"
#include "csc.h"
#include "data_generator.h"


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


// 하나의 실험 조건 실행
void run_test(int rows, int cols, double density) {

    int nnz = 0;

    // Dense 행렬 생성
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

    // 입력 벡터 및 결과 배열 할당
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

    // Dense 행렬-벡터 곱셈
    dense_matvec(
        A,
        x,
        dense_result,
        rows,
        cols
    );

    // Dense -> CSR 변환
    if (!dense_to_csr(A, rows, cols, &csr)) {
        printf("CSR conversion failed.\n");

        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);
        free_matrix(A, rows);

        exit(EXIT_FAILURE);
    }

    // Dense -> CSC 변환
    if (!dense_to_csc(A, rows, cols, &csc)) {
        printf("CSC conversion failed.\n");

        free_csr(&csr);

        free(x);
        free(dense_result);
        free(csr_result);
        free(csc_result);
        free_matrix(A, rows);

        exit(EXIT_FAILURE);
    }

    // CSR 행렬-벡터 곱셈
    csr_matvec(
        &csr,
        x,
        csr_result
    );

    // CSC 행렬-벡터 곱셈
    csc_matvec(
        &csc,
        x,
        csc_result
    );

    // Dense 결과를 기준으로 정확성 검증
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

    // 실험 결과 출력
    printf("\n====================================\n");

    printf("Matrix size: %d x %d\n", rows, cols);

    printf("Target density: %.2f%%\n",
           density * 100.0);

    printf("Actual density: %.2f%%\n",
           (double)nnz / ((double)rows * cols) * 100.0);

    printf("Non-zero elements: %d\n", nnz);

    printf("------------------------------------\n");

    printf("Dense correctness: PASS\n");

    printf("CSR correctness: %s\n",
           csr_valid ? "PASS" : "FAIL");

    printf("CSC correctness: %s\n",
           csc_valid ? "PASS" : "FAIL");

    // 메모리 해제
    free_csr(&csr);
    free_csc(&csc);

    free(x);
    free(dense_result);
    free(csr_result);
    free(csc_result);

    free_matrix(A, rows);

    // 정확성 검증 실패 시 프로그램 종료
    if (!csr_valid || !csc_valid) {
        exit(EXIT_FAILURE);
    }
}


int main(void) {

    // 난수 시드 설정
    srand(42);

    // 실험 조건
    int test_cases[][2] = {
        {100, 100},
        {500, 500},
        {1000, 1000},
        {2000, 2000}
    };

    double densities[] = {
        0.05,
        0.01,
        0.10,
        0.05
    };

    int num_tests =
        sizeof(test_cases) / sizeof(test_cases[0]);

    // 모든 실험 실행
    for (int i = 0; i < num_tests; i++) {

        run_test(
            test_cases[i][0],
            test_cases[i][1],
            densities[i]
        );
    }

    printf("\n====================================\n");
    printf("All correctness tests passed!\n");

    return 0;
}
