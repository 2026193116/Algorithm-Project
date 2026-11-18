
import csv
from pathlib import Path


# ==================================================
# 1. 파일 경로 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "report"

# Density 심화 실험 입력 파일
C_FILE = REPORT_DIR / "c_density_results.csv"
PYTHON_FILE = REPORT_DIR / "python_density_results.csv"

# 통합 결과 파일
OUTPUT_FILE = REPORT_DIR / "combined_density_results.csv"


# ==================================================
# 2. CSV 열 구성
# ==================================================

FIELDNAMES = [
    "language",
    "structure",
    "algorithm",
    "rows",
    "cols",
    "density",
    "nnz",
    "actual_density",
    "conversion_ms",
    "matvec_ms",
    "memory_bytes",
    "valid"
]


# ==================================================
# 3. 예상 실험 조건
# ==================================================

EXPECTED_LANGUAGES = ["C", "Python"]
EXPECTED_STRUCTURES = ["Random", "Banded", "Row", "Block"]
EXPECTED_ALGORITHMS = ["Dense", "CSR", "CSC"]

EXPECTED_SIZES = [100, 500, 1000, 2000]
EXPECTED_DENSITIES = [
    i / 100
    for i in range(1, 51)
]

EXPECTED_ROWS_PER_LANGUAGE = (
    len(EXPECTED_SIZES)
    * len(EXPECTED_DENSITIES)
    * len(EXPECTED_STRUCTURES)
    * len(EXPECTED_ALGORITHMS)
)

EXPECTED_TOTAL_ROWS = (
    EXPECTED_ROWS_PER_LANGUAGE
    * len(EXPECTED_LANGUAGES)
)


# ==================================================
# 4. CSV 파일 읽기 및 통합
# ==================================================

input_files = [
    (C_FILE, "C"),
    (PYTHON_FILE, "Python")
]

all_rows = []

for file_path, expected_language in input_files:

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    file_rows = []

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                f"CSV 헤더가 없습니다: {file_path}"
            )

        # 필수 열 확인
        missing_fields = [
            field
            for field in FIELDNAMES
            if field not in reader.fieldnames
        ]

        if missing_fields:
            raise ValueError(
                f"{file_path}에 필요한 열이 없습니다: "
                f"{missing_fields}"
            )

        # 데이터 읽기
        for line_number, row in enumerate(reader, start=2):

            # 필수 데이터 누락 확인
            if any(
                row.get(field) in (None, "")
                for field in FIELDNAMES
            ):
                raise ValueError(
                    f"{file_path}의 {line_number}번째 행에 "
                    f"누락된 데이터가 있습니다."
                )

            # 입력 파일의 언어 확인
            if row["language"] != expected_language:
                raise ValueError(
                    f"{file_path}의 {line_number}번째 행에서 "
                    f"언어 값이 잘못되었습니다: {row['language']}"
                )

            # 필요한 열만 추출
            file_rows.append({
                field: row[field]
                for field in FIELDNAMES
            })

    if len(file_rows) != EXPECTED_ROWS_PER_LANGUAGE:
        raise ValueError(
            f"{expected_language} 데이터 행 수가 올바르지 않습니다. "
            f"현재: {len(file_rows)}행, "
            f"예상: {EXPECTED_ROWS_PER_LANGUAGE}행"
        )

    print(
        f"{expected_language} 파일 확인 완료: "
        f"{len(file_rows)}행"
    )

    all_rows.extend(file_rows)


# ==================================================
# 5. 전체 데이터 개수 확인
# ==================================================

if not all_rows:
    raise ValueError("통합할 데이터가 없습니다.")

if len(all_rows) != EXPECTED_TOTAL_ROWS:
    raise ValueError(
        f"전체 데이터 행 수가 올바르지 않습니다. "
        f"현재: {len(all_rows)}행, "
        f"예상: {EXPECTED_TOTAL_ROWS}행"
    )


# ==================================================
# 6. 결과 CSV 저장
# ==================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=FIELDNAMES
    )

    writer.writeheader()
    writer.writerows(all_rows)


# ==================================================
# 7. 통합 결과 출력
# ==================================================

print("\n====================================")
print("Density CSV 통합 완료!")
print("====================================")

print(f"저장 위치: {OUTPUT_FILE}")
print(f"전체 데이터 행 수: {len(all_rows)}")


# ==================================================
# 8. 언어별 데이터 개수
# ==================================================

print("\n[언어별 데이터 개수]")

for language in EXPECTED_LANGUAGES:

    count = sum(
        1
        for row in all_rows
        if row["language"] == language
    )

    print(f"{language}: {count}행")


# ==================================================
# 9. 구조별 데이터 개수
# ==================================================

print("\n[구조별 데이터 개수]")

for structure in EXPECTED_STRUCTURES:

    count = sum(
        1
        for row in all_rows
        if row["structure"] == structure
    )

    print(f"{structure}: {count}행")


# ==================================================
# 10. Density 개수 확인
# ==================================================

actual_densities = sorted({
    float(row["density"])
    for row in all_rows
})

print("\n[Density 조건 확인]")

print(f"Density 개수: {len(actual_densities)}")
print(f"최소 Density: {min(actual_densities) * 100:.0f}%")
print(f"최대 Density: {max(actual_densities) * 100:.0f}%")


print("\n====================================")
print("모든 CSV 통합 작업이 완료되었습니다.")
print("====================================")
