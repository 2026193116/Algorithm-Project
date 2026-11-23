#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "csc.h"
#include "csr.h"
#include "data_generator.h"
#include "dense.h"

static int failures = 0;
static int checks = 0;

static void check(int condition, const char *name) {
    checks++;

    if (condition) {
        printf("ok   %s\n", name);
    }
    else {
        printf("FAIL %s\n", name);
        failures++;
    }
}

static int results_match(
    const double *actual,
    const double *expected,
    int size
) {
    for (int i = 0; i < size; i++) {
        if (fabs(actual[i] - expected[i]) > 1e-9) {
            return 0;
        }
    }

    return 1;
}

static void test_matvec_formats(void) {
    double row0[] = {1.0, 0.0, 2.0, 0.0};
    double row1[] = {0.0, 3.0, 0.0, 4.0};
    double row2[] = {5.0, 0.0, 0.0, 6.0};
    double *matrix[] = {row0, row1, row2};
    const double x[] = {2.0, 3.0, 4.0, 5.0};
    const double expected[] = {10.0, 29.0, 40.0};
    double dense_result[3];
    double csr_result[3];
    double csc_result[3];
    CSRMatrix csr = {0};
    CSCMatrix csc = {0};

    dense_matvec(matrix, x, dense_result, 3, 4);

    int csr_ok = dense_to_csr(matrix, 3, 4, &csr);
    int csc_ok = dense_to_csc(matrix, 3, 4, &csc);

    if (csr_ok) {
        csr_matvec(&csr, x, csr_result);
    }

    if (csc_ok) {
        csc_matvec(&csc, x, csc_result);
    }

    check(
        results_match(dense_result, expected, 3),
        "dense matvec on a rectangular matrix"
    );
    check(
        csr_ok && csr.nnz == 6 &&
            results_match(csr_result, expected, 3),
        "CSR conversion and matvec"
    );
    check(
        csc_ok && csc.nnz == 6 &&
            results_match(csc_result, expected, 3),
        "CSC conversion and matvec"
    );

    free_csr(&csr);
    free_csc(&csc);
}

static void test_empty_sparse_formats(void) {
    double row0[] = {0.0, 0.0, 0.0};
    double row1[] = {0.0, 0.0, 0.0};
    double *matrix[] = {row0, row1};
    const double x[] = {1.0, 2.0, 3.0};
    const double expected[] = {0.0, 0.0};
    double csr_result[2];
    double csc_result[2];
    CSRMatrix csr = {0};
    CSCMatrix csc = {0};

    int csr_ok = dense_to_csr(matrix, 2, 3, &csr);
    int csc_ok = dense_to_csc(matrix, 2, 3, &csc);

    if (csr_ok) {
        csr_matvec(&csr, x, csr_result);
    }

    if (csc_ok) {
        csc_matvec(&csc, x, csc_result);
    }

    check(
        csr_ok && csr.nnz == 0 &&
            results_match(csr_result, expected, 2),
        "CSR conversion and matvec for an all-zero matrix"
    );
    check(
        csc_ok && csc.nnz == 0 &&
            results_match(csc_result, expected, 2),
        "CSC conversion and matvec for an all-zero matrix"
    );

    free_csr(&csr);
    free_csc(&csc);
}

static void test_matrix_generator(void) {
    const MatrixStructure structures[] = {
        MATRIX_RANDOM,
        MATRIX_BANDED,
        MATRIX_ROW,
        MATRIX_BLOCK
    };
    const char *names[] = {
        "random matrix generation",
        "banded matrix generation",
        "row matrix generation",
        "block matrix generation"
    };
    const int expected_nnz = 6;

    srand(42);

    for (size_t s = 0; s < sizeof(structures) / sizeof(structures[0]); s++) {
        int nnz = -1;
        int actual_nnz = 0;
        double **matrix = generate_matrix_by_structure(
            3,
            5,
            0.4,
            structures[s],
            &nnz
        );

        if (matrix != NULL) {
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 5; j++) {
                    if (matrix[i][j] != 0.0) {
                        actual_nnz++;
                    }
                }
            }
        }

        check(
            matrix != NULL &&
                nnz == expected_nnz &&
                actual_nnz == expected_nnz,
            names[s]
        );
        free_matrix(matrix, 3);
    }

    int nnz = 0;
    check(
        generate_matrix_by_structure(
            0, 5, 0.4, MATRIX_RANDOM, &nnz
        ) == NULL,
        "matrix generator rejects invalid dimensions"
    );
}

int main(void) {
    test_matvec_formats();
    test_empty_sparse_formats();
    test_matrix_generator();

    printf("\n%d checks, %d failures\n", checks, failures);
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
