#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>

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

    // 새로운 CSV 파일 생성
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
    printf("Total data rows: %d\n", total_tests * 3);
    printf("Results saved to report/c_density_results.csv\n");

    return EXIT_SUCCESS;
}
