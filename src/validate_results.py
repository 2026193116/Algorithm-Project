
import csv
import math
from pathlib import Path
from collections import defaultdict


# ==================================================
# 1. 파일 경로 및 실험 조건 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "report"

INPUT_FILE = REPORT_DIR / "combined_results.csv"
OUTPUT_FILE = REPORT_DIR / "validation_summary.txt"

EXPECTED_SIZES = [100, 500, 1000, 2000]
EXPECTED_DENSITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

EXPECTED_LANGUAGES = ["C", "Python"]
EXPECTED_ALGORITHMS = ["Dense", "CSR", "CSC"]

EXPECTED_ROWS_PER_LANGUAGE = 60
EXPECTED_TOTAL_ROWS = 120


# ==================================================
# 2. 검사 결과 저장
# ==================================================

errors = []
warnings = []
checks = []


def add_check(message):
    checks.append("[PASS] " + message)


def add_error(message):
    errors.append("[FAIL] " + message)


def add_warning(message):
    warnings.append("[WARN] " + message)


# ==================================================
# 3. CSV 파일 읽기
# ==================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"CSV 파일을 찾을 수 없습니다: {INPUT_FILE}"
    )

required_columns = [
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

data = []

with open(
    INPUT_FILE,
    "r",
    newline="",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)

    if reader.fieldnames is None:
        raise ValueError("CSV 헤더가 없습니다.")

    missing_columns = [
        column
        for column in required_columns
        if column not in reader.fieldnames
    ]

    if missing_columns:
        raise ValueError(
            f"필수 열이 없습니다: {missing_columns}"
        )

    for line_number, row in enumerate(reader, start=2):

        try:
            item = {
                "language": row["language"],
                "algorithm": row["algorithm"],
                "rows": int(row["rows"]),
                "cols": int(row["cols"]),
                "density": float(row["density"]),
                "conversion_ms": float(row["conversion_ms"]),
                "matvec_ms": float(row["matvec_ms"]),
                "memory_bytes": int(row["memory_bytes"]),
                "valid": int(row["valid"])
            }

            data.append(item)

        except (ValueError, TypeError):
            add_error(
                f"{line_number}번째 행의 데이터 형식이 잘못되었습니다."
            )


# ==================================================
# 4. 데이터 개수 검증
# ==================================================

if len(data) == EXPECTED_TOTAL_ROWS:
    add_check(
        f"전체 데이터 행 수가 {EXPECTED_TOTAL_ROWS}개입니다."
    )
else:
    add_error(
        f"전체 데이터 행 수가 {len(data)}개입니다. "
        f"예상: {EXPECTED_TOTAL_ROWS}개"
    )


# ==================================================
# 5. 언어별 데이터 개수 검증
# ==================================================

language_counts = defaultdict(int)

for row in data:
    language_counts[row["language"]] += 1

for language in EXPECTED_LANGUAGES:

    count = language_counts[language]

    if count == EXPECTED_ROWS_PER_LANGUAGE:
        add_check(
            f"{language} 데이터가 {count}개입니다."
        )
    else:
        add_error(
            f"{language} 데이터 개수가 {count}개입니다. "
            f"예상: {EXPECTED_ROWS_PER_LANGUAGE}개"
        )


# ==================================================
# 6. 실험 조건 및 알고리즘 검증
# ==================================================

groups = defaultdict(list)

for row in data:

    key = (
        row["language"],
        row["rows"],
        row["cols"],
        row["density"]
    )

    groups[key].append(row["algorithm"])


expected_conditions = len(EXPECTED_SIZES) * len(EXPECTED_DENSITIES)

for language in EXPECTED_LANGUAGES:

    actual_conditions = set()

    for key, algorithms in groups.items():

        if key[0] != language:
            continue

        condition = (key[1], key[2], key[3])
        actual_conditions.add(condition)

        if sorted(algorithms) != sorted(EXPECTED_ALGORITHMS):
            add_error(
                f"{language}, {condition} 조건의 알고리즘 구성이 "
                f"올바르지 않습니다: {algorithms}"
            )

    if len(actual_conditions) == expected_conditions:
        add_check(
            f"{language}의 실험 조건 {expected_conditions}개가 존재합니다."
        )
    else:
        add_error(
            f"{language}의 실험 조건이 "
            f"{len(actual_conditions)}개입니다."
        )


# ==================================================
# 7. C와 Python의 실험 조건 비교
# ==================================================

language_conditions = {}

for language in EXPECTED_LANGUAGES:

    language_conditions[language] = {
        (row["rows"], row["cols"], row["density"])
        for row in data
        if row["language"] == language
    }

if (
    language_conditions["C"]
    == language_conditions["Python"]
):
    add_check(
        "C와 Python의 행렬 크기 및 목표 Density 조건이 일치합니다."
    )
else:
    add_error(
        "C와 Python의 실험 조건이 서로 다릅니다."
    )


# ==================================================
# 8. 정확성 검증 결과 확인
# ==================================================

invalid_rows = [
    row for row in data
    if row["valid"] != 1
]

if not invalid_rows:
    add_check(
        "모든 실험에서 valid=1입니다."
    )
else:
    add_error(
        f"정확성 검증에 실패한 데이터가 "
        f"{len(invalid_rows)}개 있습니다."
    )


# ==================================================
# 9. 수치 데이터 검증
# ==================================================

invalid_measurements = []

for row in data:

    values = [
        row["density"],
        row["conversion_ms"],
        row["matvec_ms"],
        row["memory_bytes"]
    ]

    if not all(math.isfinite(value) for value in values):
        invalid_measurements.append(row)
        continue

    if (
        row["rows"] <= 0
        or row["cols"] <= 0
        or row["density"] < 0
        or row["density"] > 1
        or row["conversion_ms"] < 0
        or row["matvec_ms"] <= 0
        or row["memory_bytes"] <= 0
    ):
        invalid_measurements.append(row)

if not invalid_measurements:
    add_check(
        "실행 시간, Density, 메모리 값이 유효한 범위에 있습니다."
    )
else:
    add_error(
        f"수치 데이터가 비정상적인 행이 "
        f"{len(invalid_measurements)}개 있습니다."
    )


# ==================================================
# 10. 중복 데이터 검증
# ==================================================

unique_keys = set()
duplicates = []

for row in data:

    key = (
        row["language"],
        row["algorithm"],
        row["rows"],
        row["cols"],
        row["density"]
    )

    if key in unique_keys:
        duplicates.append(key)
    else:
        unique_keys.add(key)

if not duplicates:
    add_check("중복된 실험 데이터가 없습니다.")
else:
    add_error(
        f"중복된 실험 데이터가 {len(duplicates)}개 있습니다."
    )


# ==================================================
# 11. 추가 검증이 필요한 사항
# ==================================================

header = set(required_columns)

if "actual_density" not in header:
    add_warning(
        "CSV에 actual_density가 없습니다. "
        "현재 density는 목표 Density로 취급해야 합니다."
    )

if "nnz" not in header:
    add_warning(
        "CSV에 nnz가 없습니다. "
        "실제 비제로 원소 개수를 직접 확인할 수 없습니다."
    )

add_warning(
    "현재 CSV만으로 C와 Python이 동일한 입력 행렬을 "
    "사용했는지는 확인할 수 없습니다."
)

add_warning(
    "C와 Python의 memory_bytes 측정 기준이 다를 수 있으므로 "
    "메모리 수치의 직접 비교에 주의해야 합니다."
)


# ==================================================
# 12. 검증 결과 출력 및 저장
# ==================================================

summary = []

summary.append("======================================")
summary.append("     EXPERIMENT DATA VALIDATION")
summary.append("======================================")

summary.append("")
summary.append("[검증 통과 항목]")

summary.extend(checks if checks else ["없음"])

summary.append("")
summary.append("[오류 항목]")

summary.extend(errors if errors else ["없음"])

summary.append("")
summary.append("[추가 확인 필요 항목]")

summary.extend(warnings if warnings else ["없음"])

summary.append("")
summary.append("======================================")

if errors:
    summary.append("최종 결과: 검증 실패")
else:
    summary.append("최종 결과: 기본 데이터 검증 통과")

summary.append("======================================")


result_text = "\n".join(summary)

print(result_text)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:
    file.write(result_text)

print(f"\n검증 결과 저장 위치: {OUTPUT_FILE}")
