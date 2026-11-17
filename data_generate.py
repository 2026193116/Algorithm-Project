import random


def generate_matrix(rows, cols, density, seed=42):
    # 입력값 검증
    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and columns must be positive.")

    if not 0 <= density <= 1:
        raise ValueError("Density must be between 0 and 1.")

    rng = random.Random(seed)

    # 모든 원소를 0으로 초기화
    A = [[0 for _ in range(cols)] for _ in range(rows)]

    # 전체 원소 중 0이 아닌 원소의 개수
    total_elements = rows * cols
    nnz = round(total_elements * density)

    # 0이 아닌 원소를 배치할 위치 선택
    positions = rng.sample(
        range(total_elements),
        nnz
    )

    for position in positions:
        i = position // cols
        j = position % cols

        # 0이 아닌 정수 생성
        value = rng.randint(1, 10)

        A[i][j] = value

    return A
