
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdint.h>
#include <stddef.h>

#include "data_generator.h"


// 목표 Density에 해당하는 정확한 nnz 계산
static int calculate_nnz(int rows, int cols, double density) {
    long long total = (long long)rows * cols;

    return (int)((double)total * density + 0.5);
}


// 대각선 밴드 영역의 원소 개수 계산
static long long count_banded_positions(
    int rows,
    int cols,
    int bandwidth
) {
    long long count = 0;

    for (int i = 0; i < rows; i++) {
        int start = i - bandwidth;
        int end = i + bandwidth;

        if (start < 0) {
            start = 0;
        }

        if (end >= cols) {
            end = cols - 1;
        }

        if (start <= end) {
            count += (long long)(end - start + 1);
        }
    }

    return count;
}


// 행렬 메모리 할당
static double **allocate_matrix(int rows, int cols) {
    double **A = malloc((size_t)rows * sizeof(double *));

    if (A == NULL) {
        return NULL;
    }

    for (int i = 0; i < rows; i++) {
        A[i] = calloc((size_t)cols, sizeof(double));

        if (A[i] == NULL) {
            for (int k = 0; k < i; k++) {
                free(A[k]);
            }

            free(A);
            return NULL;
        }
    }

    return A;
}


// 후보 위치 중 nnz개를 무작위로 선택하여 행렬에 배치
static void select_positions(
    double **A,
    int cols,
    size_t *positions,
    size_t candidate_count,
    int nnz
) {
    for (int i = 0; i < nnz; i++) {
        size_t remaining = candidate_count - (size_t)i;

        size_t selected =
            (size_t)i + (size_t)rand() % remaining;

        size_t temp = positions[i];
        positions[i] = positions[selected];
        positions[selected] = temp;

        size_t position = positions[i];

        int row = (int)(position / (size_t)cols);
        int col = (int)(position % (size_t)cols);

        A[row][col] = (double)(rand() % 10 + 1);
    }
}


// 구조에 따른 행렬 생성
double **generate_matrix_by_structure(
    int rows,
    int cols,
    double density,
    MatrixStructure structure,
    int *nnz
) {
    if (rows <= 0 || cols <= 0 || nnz == NULL) {
        return NULL;
    }

    if (density < 0.0 || density > 1.0) {
        return NULL;
    }

    if (structure < MATRIX_RANDOM ||
        structure > MATRIX_BLOCK) {
        return NULL;
    }

    if ((long long)rows * cols > INT_MAX) {
        return NULL;
    }

    int target_nnz = calculate_nnz(rows, cols, density);

    double **A = allocate_matrix(rows, cols);

    if (A == NULL) {
        return NULL;
    }

    *nnz = target_nnz;

    // 모든 원소가 0인 경우
    if (target_nnz == 0) {
        return A;
    }

    size_t *positions = NULL;
    size_t candidate_count = 0;

    // 1. Random
    if (structure == MATRIX_RANDOM) {
        candidate_count = (size_t)rows * (size_t)cols;

        positions = malloc(
            candidate_count * sizeof(size_t)
        );

        if (positions == NULL) {
            free_matrix(A, rows);
            return NULL;
        }

        for (size_t i = 0; i < candidate_count; i++) {
            positions[i] = i;
        }
    }

    // 2. Banded
    else if (structure == MATRIX_BANDED) {
        int low = 0;
        int high = rows > cols ? rows : cols;

        // 목표 nnz를 수용할 수 있는 최소 bandwidth 탐색
        while (low < high) {
            int mid = low + (high - low) / 2;

            if (count_banded_positions(rows, cols, mid)
                >= target_nnz) {
                high = mid;
            }
            else {
                low = mid + 1;
            }
        }

        int bandwidth = low;

        candidate_count = (size_t)count_banded_positions(
            rows,
            cols,
            bandwidth
        );

        positions = malloc(
            candidate_count * sizeof(size_t)
        );

        if (positions == NULL) {
            free_matrix(A, rows);
            return NULL;
        }

        size_t index = 0;

        for (int i = 0; i < rows; i++) {
            int start = i - bandwidth;
            int end = i + bandwidth;

            if (start < 0) {
                start = 0;
            }

            if (end >= cols) {
                end = cols - 1;
            }

            for (int j = start; j <= end; j++) {
                positions[index++] =
                    (size_t)i * (size_t)cols + (size_t)j;
            }
        }
    }

    // 3. Row-concentrated
    else if (structure == MATRIX_ROW) {
        size_t selected_rows =
            ((size_t)target_nnz + (size_t)cols - 1)
            / (size_t)cols;

        candidate_count = selected_rows * (size_t)cols;

        positions = malloc(
            candidate_count * sizeof(size_t)
        );

        if (positions == NULL) {
            free_matrix(A, rows);
            return NULL;
        }

        size_t index = 0;

        for (size_t i = 0; i < selected_rows; i++) {
            for (int j = 0; j < cols; j++) {
                positions[index++] =
                    i * (size_t)cols + (size_t)j;
            }
        }
    }

    // 4. Block
    else if (structure == MATRIX_BLOCK) {
        int block_rows = 1;

        while ((long long)block_rows * block_rows < target_nnz
               && block_rows < rows) {
            block_rows++;
        }

        int block_cols =
            (target_nnz - 1) / block_rows + 1;

        if (block_cols > cols) {
            block_cols = cols;

            block_rows =
                (target_nnz - 1) / block_cols + 1;
        }

        candidate_count =
            (size_t)block_rows * (size_t)block_cols;

        positions = malloc(
            candidate_count * sizeof(size_t)
        );

        if (positions == NULL) {
            free_matrix(A, rows);
            return NULL;
        }

        size_t index = 0;

        for (int i = 0; i < block_rows; i++) {
            for (int j = 0; j < block_cols; j++) {
                positions[index++] =
                    (size_t)i * (size_t)cols + (size_t)j;
            }
        }
    }

    // 후보 위치 중 정확히 target_nnz개 선택
    select_positions(
        A,
        cols,
        positions,
        candidate_count,
        target_nnz
    );

    free(positions);

    return A;
}


// 기존 함수: Random 행렬 생성 기능 유지
double **generate_matrix(
    int rows,
    int cols,
    double density,
    int *nnz
) {
    return generate_matrix_by_structure(
        rows,
        cols,
        density,
        MATRIX_RANDOM,
        nnz
    );
}


// 행렬 메모리 해제
void free_matrix(double **A, int rows) {
    if (A == NULL) {
        return;
    }

    for (int i = 0; i < rows; i++) {
        free(A[i]);
    }

    free(A);
}
