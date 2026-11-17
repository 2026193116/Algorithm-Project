#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "dense.h"
#include "data_generator.h"


// 정답 검증을 위한 기준 연산
void reference_matvec(
    double **A,
    const double *x,
    double *y,
    int rows,
    int cols
) {
    for (int i = 0; i < rows; i++) {
        double sum = 0.0;

        for (int j = 0; j < cols; j++) {
            sum += A[i][j] * x[j];
        }

        y[i] = sum;
    }
}


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

    // 벡터 및 결과 배열 할당
    double *x = malloc(cols * sizeof(double));
    double *result = malloc(rows * sizeof(double));
    double *expected = malloc(rows * sizeof(double));

    if (x == NULL || result == NULL || expected == NULL) {
        printf("Memory allocation failed.\n");

        free(x);
        free(result);
        free(expected);
        free_matrix(A, rows);

        exit(EXIT_FAILURE);
    }

    // 입력 벡터 생성
    for (int j = 0; j < cols; j++) {
        x[j] = (double)(j % 5 + 1);
    }

    // Dense 알고리즘 실행
    dense_matvec(A, x, result, rows, cols);

    // 기준 결과 계산
    reference_matvec(A, x, expected, rows, cols);

    // 결과 검증
    int valid = compare_results(
        result,
        expected,
        rows
    );

    // 실험 결과 출력
    printf("\n====================================\n");
    printf("Matrix size: %d x %d\n", rows, cols);
    printf("Target density: %.2f%%\n", density * 100.0);
    printf("Actual density: %.2f%%\n",
           (double)nnz / (rows * cols) * 100.0);
    printf("Non-zero elements: %d\n", nnz);

    if (valid) {
        printf("Dense correctness: PASS\n");
    }
    else {
        printf("Dense correctness: FAIL\n");
    }

    // 메모리 해제
    free(x);
    free(result);
    free(expected);
    free_matrix(A, rows);

    if (!valid) {
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

    int num_tests = sizeof(test_cases) / sizeof(test_cases[0]);

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
