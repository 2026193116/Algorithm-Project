
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

# CSV 파일 통합
input_files = [C_FILE, PYTHON_FILE]
all_rows = []

for file_path in input_files:
    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"CSV 헤더가 없습니다: {file_path}")

        for row in reader:
            all_rows.append(row)

# 결과 저장
if not all_rows:
    raise ValueError("통합할 데이터가 없습니다.")

fieldnames = [
    "language",
    "algorithm",
    "rows",
    "cols",
    "density",
    "conversion_ms",
    "matvec_ms",
    "memory_bytes",
    "valid"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print("CSV 통합 완료!")
print(f"저장 위치: {OUTPUT_FILE}")
print(f"총 데이터 행 수: {len(all_rows)}")
