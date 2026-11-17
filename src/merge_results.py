
import csv
from pathlib import Path


# 프로젝트 최상위 폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "report"

# 입력 파일
C_FILE = REPORT_DIR / "c_results.csv"
PYTHON_FILE = REPORT_DIR / "python_results.csv"

# 출력 파일
OUTPUT_FILE = REPORT_DIR / "combined_results.csv"


# 통합 CSV의 열 구성
FIELDNAMES = [
    "language",
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


# CSV 파일 통합
input_files = [C_FILE, PYTHON_FILE]
all_rows = []

for file_path in input_files:

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

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
        for row in reader:

            # 필수 데이터 누락 확인
            if any(
                row.get(field) in (None, "")
                for field in FIELDNAMES
            ):
                raise ValueError(
                    f"{file_path}에 누락된 데이터가 있습니다: {row}"
                )

            # 필요한 열만 추출하여 저장
            all_rows.append({
                field: row[field]
                for field in FIELDNAMES
            })


# 통합 데이터 확인
if not all_rows:
    raise ValueError("통합할 데이터가 없습니다.")


# 결과 저장
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


print("CSV 통합 완료!")
print(f"저장 위치: {OUTPUT_FILE}")
print(f"총 데이터 행 수: {len(all_rows)}")

# 언어별 데이터 개수 출력
c_count = sum(
    1 for row in all_rows
    if row["language"] == "C"
)

python_count = sum(
    1 for row in all_rows
    if row["language"] == "Python"
)

print(f"C 데이터 행 수: {c_count}")
print(f"Python 데이터 행 수: {python_count}")
