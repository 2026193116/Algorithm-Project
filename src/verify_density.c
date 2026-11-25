#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "csc.h"
#include "csr.h"
#include "data_generator.h"
#include "dense.h"

static const char *structure_name(MatrixStructure s) {
    switch (s) {
        case MATRIX_RANDOM: return "Random";
        case MATRIX_BANDED: return "Banded";
        case MATRIX_ROW:    return "Row";
        case MATRIX_BLOCK:  return "Block";
        default:            return "Unknown";
    }
}

static int same(const double *a, const double *b, int n) {
    for (int i = 0; i < n; i++) {
        if (fabs(a[i] - b[i]) > 1e-9) return 0;
    }
    return 1;
}

int main(void) {
    const char *csv_path = "report/c_density_results.csv";
    FILE *csv = fopen(csv_path, "r");
    char line[512];

    if (csv == NULL) {
        printf("cannot open %s\n", csv_path);
        return EXIT_FAILURE;
    }
    if (fgets(line, sizeof line, csv) == NULL) {
        fclose(csv);
        return EXIT_FAILURE;
    }

    srand(42);                                      

    const int sizes[] = {100, 500, 1000, 2000};
    const MatrixStructure structures[] = {
        MATRIX_RANDOM, MATRIX_BANDED, MATRIX_ROW, MATRIX_BLOCK
    };

    int conditions = 0, failures = 0, csv_mismatch = 0;

    for (int si = 0; si < 4; si++) {
        int n = sizes[si];
        for (int di = 0; di < 50; di++) {
            double density = (double)(di + 1) / 100.0;
            for (int k = 0; k < 4; k++) {
                int nnz = 0;
                double **A = generate_matrix_by_structure(n, n, density, structures[k], &nnz);
                if (A == NULL) { printf("generation failed\n"); fclose(csv); return EXIT_FAILURE; }

                double *x  = malloc((size_t)n * sizeof(double));
                double *yd = malloc((size_t)n * sizeof(double));
                double *yr = malloc((size_t)n * sizeof(double));
                double *yc = malloc((size_t)n * sizeof(double));
                if (!x || !yd || !yr || !yc) { printf("alloc failed\n"); return EXIT_FAILURE; }

                for (int i = 0; i < n; i++) x[i] = (double)(rand() % 10 + 1);  

                CSRMatrix csr = {0};
                CSCMatrix csc = {0};
                dense_matvec(A, x, yd, n, n);
                if (!dense_to_csr(A, n, n, &csr) || !dense_to_csc(A, n, n, &csc)) {
                    printf("conversion failed\n"); return EXIT_FAILURE;
                }
                csr_matvec(&csr, x, yr);
                csc_matvec(&csc, x, yc);

                int ok = same(yr, yd, n) && same(yc, yd, n);
                if (!ok) {
                    failures++;
                    printf("MISMATCH n=%d density=%.2f structure=%s\n", n, density, structure_name(structures[k]));
                }

                for (int r = 0; r < 3; r++) {
                    char lang[16], st[16], alg[16];
                    int rows, cols, csv_nnz;
                    double dens;
                    if (fgets(line, sizeof line, csv) == NULL ||
                        sscanf(line, "%15[^,],%15[^,],%15[^,],%d,%d,%lf,%d",
                               lang, st, alg, &rows, &cols, &dens, &csv_nnz) != 7 ||
                        rows != n || cols != n || strcmp(st, structure_name(structures[k])) != 0 ||
                        fabs(dens - density) > 1e-9 || csv_nnz != nnz) {
                        csv_mismatch++;
                    }
                }

                conditions++;
                free_csr(&csr); free_csc(&csc);
                free(x); free(yd); free(yr); free(yc);
                free_matrix(A, n);
            }
        }
    }
    fclose(csv);

    printf("checked conditions : %d\n", conditions);
    printf("result mismatches  : %d\n", failures);
    printf("CSV row mismatches : %d\n", csv_mismatch);
    printf("%s\n", (failures == 0 && csv_mismatch == 0) ? "PASS" : "FAIL");
    return (failures == 0 && csv_mismatch == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
