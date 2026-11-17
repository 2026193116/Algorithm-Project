
import random
import math


def generate_matrix(
    rows,
    cols,
    density,
    seed=42,
    structure="random"
):
    # 입력값 검증
    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and columns must be positive.")

    if not 0 <= density <= 1:
        raise ValueError("Density must be between 0 and 1.")

    valid_structures = [
        "random",
        "banded",
        "row",
        "block"
    ]

    if structure not in valid_structures:
        raise ValueError(
            f"Invalid structure: {structure}"
        )

    rng = random.Random(seed)

    # 모든 원소를 0으로 초기화
    A = [[0 for _ in range(cols)] for _ in range(rows)]

    # C와 동일한 반올림 규칙 사용
    total_elements = rows * cols
    nnz = math.floor(total_elements * density + 0.5)

    if nnz == 0:
        return A

    # 1. Random
    if structure == "random":
        candidates = list(range(total_elements))

    # 2. Banded
    elif structure == "banded":

        def count_banded_positions(bandwidth):
            count = 0

            for i in range(rows):
                start = max(0, i - bandwidth)
                end = min(cols - 1, i + bandwidth)

                if start <= end:
                    count += end - start + 1

            return count

        low = 0
        high = max(rows, cols)

        # 목표 nnz를 수용할 수 있는 최소 bandwidth 탐색
        while low < high:
            mid = (low + high) // 2

            if count_banded_positions(mid) >= nnz:
                high = mid
            else:
                low = mid + 1

        bandwidth = low

        candidates = []

        for i in range(rows):
            start = max(0, i - bandwidth)
            end = min(cols - 1, i + bandwidth)

            for j in range(start, end + 1):
                candidates.append(i * cols + j)

    # 3. Row-concentrated
    elif structure == "row":
        selected_rows = math.ceil(nnz / cols)

        candidates = [
            i * cols + j
            for i in range(selected_rows)
            for j in range(cols)
        ]

    # 4. Block
    elif structure == "block":
        block_rows = 1

        while block_rows * block_rows < nnz and block_rows < rows:
            block_rows += 1

        block_cols = math.ceil(nnz / block_rows)

        if block_cols > cols:
            block_cols = cols
            block_rows = math.ceil(nnz / block_cols)

        candidates = [
            i * cols + j
            for i in range(block_rows)
            for j in range(block_cols)
        ]

    # 후보 위치 중 정확히 nnz개 선택
    positions = rng.sample(candidates, nnz)

    # 선택된 위치에 0이 아닌 값 배치
    for position in positions:
        i = position // cols
        j = position % cols

        A[i][j] = rng.randint(1, 10)

    return A
