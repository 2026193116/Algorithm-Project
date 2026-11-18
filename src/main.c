
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>

#include "data_generator.h"
#include "benchmark.h"


// 행렬 구조 이름 반환
static const char *get_structure_name(
    MatrixStructure structure
) {
    switch (structure) {
        case MATRIX_RANDOM:
            return "Random";

        case MATRIX_BANDED:
            return "Banded";

        case MATRIX_ROW:
            return "Row";

        case MATRIX_BLOCK:
            return "Block";

        default:
            return "Unknown";
    }
}


// 하나의 실험 조건 실행 및 CSV 기록
static void run_test(
    FILE *fp,
    int rows,
    int cols,
    double density,
    MatrixStructure structure
) {
    int nnz = 0;

    // 1. 행렬 생성
    double **A = generate_matrix_by_structure(
        rows,
        cols,
        density,
        structure,
        &nnz
    );

    if (A == NULL) {
        printf("Matrix generation failed.\n");
        return;
    }

    // 2. 실제 Density 계산
    double actual_density =
        (double)nnz / ((double)rows * cols);

    // 3. 벡터 생성
    double *x = malloc((size_t)cols * sizeof(double));

    if (x == NULL) {
        printf("Vector allocation failed.\n");
        free_matrix(A, rows);
        return;
    }

    for (int i = 0; i < cols; i++) {
        x[i] = (double)(rand() % 10 + 1);
    }

    // 4. 벤치마크 실행
    BenchmarkResult result = {0};

    int valid = benchmark_matvec(
        A,
        x,
        rows,
        cols,
        nnz,
        &result
    );

    const char *structure_name =
        get_structure_name(structure);

    // 5. Dense 결과 기록
    fprintf(
        fp,
        "C,%s,Dense,%d,%d,%.4f,%d,%.6f,%.8f,%.8f,%zu,%d\n",
        structure_name,
        rows,
        cols,
        density,
        nnz,
        actual_density,
        0.0,
        result.dense_matvec_ms,
        result.dense_memory_bytes,
        valid
    );

    // 6. CSR 결과 기록
    fprintf(
        fp,
        "C,%s,CSR,%d,%d,%.4f,%d,%.6f,%.8f,%.8f,%zu,%d\n",
        structure_name,
        rows,
        cols,
        density,
        nnz,
        actual_density,
        result.csr_conversion_ms,
        result.csr_matvec_ms,
        result.csr_memory_bytes,
        valid
    );

    // 7. CSC 결과 기록
    fprintf(
        fp,
        "C,%s,CSC,%d,%d,%.4f,%d,%.6f,%.8f,%.8f,%zu,%d\n",
        structure_name,
        rows,
        cols,
        density,
        nnz,
        actual_density,
        result.csc_conversion_ms,
        result.csc_matvec_ms,
        result.csc_memory_bytes,
        valid
    );

    // 8. 메모리 해제
    free(x);
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

    // Density: 1% ~ 50%, 1% 간격
    double densities[50];

    for (int i = 0; i < 50; i++) {
        densities[i] = (double)(i + 1) / 100.0;
    }

    // 행렬 구조
    MatrixStructure structures[] = {
        MATRIX_RANDOM,
        MATRIX_BANDED,
        MATRIX_ROW,
        MATRIX_BLOCK
    };

    int size_count =
        sizeof(matrix_sizes) / sizeof(matrix_sizes[0]);

    int density_count =
        sizeof(densities) / sizeof(densities[0]);

    int structure_count =
        sizeof(structures) / sizeof(structures[0]);

    // CSV 파일 생성
    FILE *fp = fopen(
        "report/c_density_results.csv",
        "w"
    );

    if (fp == NULL) {
        printf("CSV file creation failed.\n");
        return EXIT_FAILURE;
    }

    // CSV 헤더
    fprintf(
        fp,
        "language,structure,algorithm,rows,cols,density,"
        "nnz,actual_density,"
        "conversion_ms,matvec_ms,memory_bytes,valid\n"
    );

    int total_tests =
        size_count * density_count * structure_count;

    int current_test = 0;

    printf("Starting C density benchmark...\n");
    printf("Density range: 1%% ~ 50%%\n");
    printf("Density interval: 1%%\n");
    printf("Total experiment conditions: %d\n", total_tests);

    // 전체 실험 실행
    for (int i = 0; i < size_count; i++) {

        for (int j = 0; j < density_count; j++) {

            for (int k = 0; k < structure_count; k++) {

                current_test++;

                printf(
                    "\n[Test %d/%d]\n",
                    current_test,
                    total_tests
                );

                run_test(
                    fp,
                    matrix_sizes[i],
                    matrix_sizes[i],
                    densities[j],
                    structures[k]
                );
            }
        }
    }

    fclose(fp);

    printf("\n====================================\n");
    printf("All C density benchmark tests completed!\n");
    printf("Total experiment conditions: %d\n", total_tests);
    printf("Expected data rows: %d\n", total_tests * 3);
    printf("Results saved to report/c_density_results.csv\n");

    return EXIT_SUCCESS;
}
