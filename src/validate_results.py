
import csv
import math
from pathlib import Path
from collections import defaultdict


# ==================================================
# 1. 파일 경로 및 실험 조건 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "report"

INPUT_FILE = REPORT_DIR / "combined_structure_results.csv"
OUTPUT_FILE = REPORT_DIR / "structure_validation_summary.txt"

EXPECTED_SIZES = [100, 500, 1000, 2000]
EXPECTED_DENSITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

EXPECTED_LANGUAGES = ["C", "Python"]
EXPECTED_STRUCTURES = ["Random", "Banded", "Row", "Block"]
EXPECTED_ALGORITHMS = ["Dense", "CSR", "CSC"]

EXPECTED_CONDITIONS_PER_LANGUAGE = (
    len(EXPECTED_SIZES)
    * len(EXPECTED_DENSITIES)
    * len(EXPECTED_STRUCTURES)
)

EXPECTED_ROWS_PER_LANGUAGE = (
    EXPECTED_CONDITIONS_PER_LANGUAGE
    * len(EXPECTED_ALGORITHMS)
)

EXPECTED_TOTAL_ROWS = (
    EXPECTED_ROWS_PER_LANGUAGE
    * len(EXPECTED_LANGUAGES)
)

DENSITY_TOLERANCE = 1e-8


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
                "structure": row["structure"],
                "algorithm": row["algorithm"],
                "rows": int(row["rows"]),
                "cols": int(row["cols"]),
                "density": float(row["density"]),
                "nnz": int(row["nnz"]),
                "actual_density": float(row["actual_density"]),
                "conversion_ms": float(row["conversion_ms"]),
                "matvec_ms": float(row["matvec_ms"]),
                "memory_bytes": int(row["memory_bytes"]),
                "valid": int(row["valid"])
            }

            data.append(item)

        except (ValueError, TypeError, KeyError):
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
# 6. 구조별 데이터 개수 검증
# ==================================================

structure_counts = defaultdict(int)

for row in data:
    structure_counts[row["structure"]] += 1

expected_rows_per_structure = (
    len(EXPECTED_SIZES)
    * len(EXPECTED_DENSITIES)
    * len(EXPECTED_ALGORITHMS)
)

for language in EXPECTED_LANGUAGES:

    for structure in EXPECTED_STRUCTURES:

        count = sum(
            1
            for row in data
            if row["language"] == language
            and row["structure"] == structure
        )

        if count == expected_rows_per_structure:
            add_check(
                f"{language}의 {structure} 구조 데이터가 "
                f"{count}개입니다."
            )
        else:
            add_error(
                f"{language}의 {structure} 구조 데이터가 "
                f"{count}개입니다. "
                f"예상: {expected_rows_per_structure}개"
            )


# ==================================================
# 7. 실험 조건 및 알고리즘 검증
# ==================================================

groups = defaultdict(list)

for row in data:

    key = (
        row["language"],
        row["structure"],
        row["rows"],
        row["cols"],
        row["density"]
    )

    groups[key].append(row["algorithm"])


expected_condition_set = {
    (structure, size, size, density)
    for structure in EXPECTED_STRUCTURES
    for size in EXPECTED_SIZES
    for density in EXPECTED_DENSITIES
}

for language in EXPECTED_LANGUAGES:

    actual_conditions = set()

    for key, algorithms in groups.items():

        if key[0] != language:
            continue

        condition = (
            key[1],
            key[2],
            key[3],
            key[4]
        )

        actual_conditions.add(condition)

        if sorted(algorithms) != sorted(EXPECTED_ALGORITHMS):
            add_error(
                f"{language}, {condition} 조건의 알고리즘 구성이 "
                f"올바르지 않습니다: {algorithms}"
            )

    if len(actual_conditions) == EXPECTED_CONDITIONS_PER_LANGUAGE:
        add_check(
            f"{language}의 실험 조건 "
            f"{EXPECTED_CONDITIONS_PER_LANGUAGE}개가 존재합니다."
        )
    else:
        add_error(
            f"{language}의 실험 조건이 "
            f"{len(actual_conditions)}개입니다. "
            f"예상: {EXPECTED_CONDITIONS_PER_LANGUAGE}개"
        )

    if actual_conditions != expected_condition_set:
        add_error(
            f"{language}의 행렬 크기, Density 또는 구조 조건이 "
            f"설정된 실험 조건과 일치하지 않습니다."
        )


# ==================================================
# 8. C와 Python의 실험 조건 비교
# ==================================================

language_conditions = {}

for language in EXPECTED_LANGUAGES:

    language_conditions[language] = {
        (
            row["structure"],
            row["rows"],
            row["cols"],
            row["density"]
        )
        for row in data
        if row["language"] == language
    }


if (
    language_conditions["C"]
    == language_conditions["Python"]
):
    add_check(
        "C와 Python의 행렬 크기, 목표 Density 및 구조 조건이 일치합니다."
    )
else:
    add_error(
        "C와 Python의 실험 조건이 서로 다릅니다."
    )


# ==================================================
# 9. 정확성 검증 결과 확인
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
# 10. 수치 데이터 검증
# ==================================================

invalid_measurements = []

for row in data:

    values = [
        row["density"],
        row["actual_density"],
        row["conversion_ms"],
        row["matvec_ms"]
    ]

    if not all(math.isfinite(value) for value in values):
        invalid_measurements.append(row)
        continue

    if (
        row["language"] not in EXPECTED_LANGUAGES
        or row["structure"] not in EXPECTED_STRUCTURES
        or row["algorithm"] not in EXPECTED_ALGORITHMS
        or row["rows"] <= 0
        or row["cols"] <= 0
        or row["density"] < 0
        or row["density"] > 1
        or row["actual_density"] < 0
        or row["actual_density"] > 1
        or row["nnz"] < 0
        or row["nnz"] > row["rows"] * row["cols"]
        or row["conversion_ms"] < 0
        or row["matvec_ms"] <= 0
        or row["memory_bytes"] <= 0
        or row["valid"] not in (0, 1)
    ):
        invalid_measurements.append(row)


if not invalid_measurements:
    add_check(
        "실행 시간, Density, nnz 및 메모리 값이 유효한 범위에 있습니다."
    )
else:
    add_error(
        f"수치 데이터가 비정상적인 행이 "
        f"{len(invalid_measurements)}개 있습니다."
    )


# ==================================================
# 11. nnz 및 actual_density 관계 검증
# ==================================================

invalid_density_rows = []

for row in data:

    if row["rows"] <= 0 or row["cols"] <= 0:
        continue

    expected_actual_density = (
        row["nnz"] / (row["rows"] * row["cols"])
    )

    if not math.isclose(
        row["actual_density"],
        expected_actual_density,
        rel_tol=0,
        abs_tol=DENSITY_TOLERANCE
    ):
        invalid_density_rows.append(row)


if not invalid_density_rows:
    add_check(
        "모든 행에서 actual_density = nnz / (rows × cols) 관계가 일치합니다."
    )
else:
    add_error(
        f"nnz와 actual_density가 일치하지 않는 행이 "
        f"{len(invalid_density_rows)}개 있습니다."
    )


# ==================================================
# 12. 목표 Density에 따른 nnz 검증
# ==================================================

invalid_target_nnz = []

for row in data:

    expected_nnz = math.floor(
        row["rows"] * row["cols"] * row["density"] + 0.5
    )

    if row["nnz"] != expected_nnz:
        invalid_target_nnz.append(row)


if not invalid_target_nnz:
    add_check(
        "모든 행의 nnz가 목표 Density에 따른 반올림 계산값과 일치합니다."
    )
else:
    add_error(
        f"목표 Density에 따른 nnz와 일치하지 않는 행이 "
        f"{len(invalid_target_nnz)}개 있습니다."
    )


# ==================================================
# 13. 동일 조건에서 알고리즘 간 nnz 일관성 검증
# ==================================================

inconsistent_groups = []

density_groups = defaultdict(list)

for row in data:

    key = (
        row["language"],
        row["structure"],
        row["rows"],
        row["cols"],
        row["density"]
    )

    density_groups[key].append(row)


for key, rows_in_group in density_groups.items():

    if len(rows_in_group) != len(EXPECTED_ALGORITHMS):
        continue

    nnz_values = {
        row["nnz"]
        for row in rows_in_group
    }

    actual_density_values = {
        row["actual_density"]
        for row in rows_in_group
    }

    if (
        len(nnz_values) != 1
        or len(actual_density_values) != 1
    ):
        inconsistent_groups.append(key)


if not inconsistent_groups:
    add_check(
        "동일한 구조 및 실험 조건에서 Dense, CSR, CSC의 "
        "nnz와 actual_density가 일치합니다."
    )
else:
    add_error(
        f"알고리즘 간 nnz 또는 actual_density가 일치하지 않는 "
        f"실험 조건이 {len(inconsistent_groups)}개 있습니다."
    )


# ==================================================
# 14. C와 Python의 nnz 및 actual_density 비교
# ==================================================

cross_language_groups = defaultdict(dict)

for row in data:

    key = (
        row["structure"],
        row["rows"],
        row["cols"],
        row["density"],
        row["algorithm"]
    )

    cross_language_groups[key][row["language"]] = (
        row["nnz"],
        row["actual_density"]
    )


cross_language_mismatches = []

for key, values in cross_language_groups.items():

    if (
        "C" not in values
        or "Python" not in values
    ):
        continue

    c_nnz, c_actual_density = values["C"]
    py_nnz, py_actual_density = values["Python"]

    if (
        c_nnz != py_nnz
        or not math.isclose(
            c_actual_density,
            py_actual_density,
            rel_tol=0,
            abs_tol=DENSITY_TOLERANCE
        )
    ):
        cross_language_mismatches.append(key)


if not cross_language_mismatches:
    add_check(
        "동일한 실험 조건에서 C와 Python의 nnz 및 actual_density가 일치합니다."
    )
else:
    add_error(
        f"C와 Python의 nnz 또는 actual_density가 일치하지 않는 "
        f"조건이 {len(cross_language_mismatches)}개 있습니다."
    )


# ==================================================
# 15. 중복 데이터 검증
# ==================================================

unique_keys = set()
duplicates = []

for row in data:

    key = (
        row["language"],
        row["structure"],
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
# 16. 추가 확인이 필요한 사항
# ==================================================

add_warning(
    "C와 Python은 서로 다른 난수 생성 방식을 사용하므로 "
    "동일한 nnz라도 원소의 위치와 값은 다를 수 있습니다."
)

add_warning(
    "현재 CSV에는 입력 행렬 자체가 저장되어 있지 않으므로 "
    "C와 Python이 동일한 원소 위치와 값을 사용했는지는 확인할 수 없습니다."
)

add_warning(
    "C와 Python의 memory_bytes 측정 기준이 다를 수 있으므로 "
    "메모리 수치의 직접 비교에 주의해야 합니다."
)


# ==================================================
# 17. 검증 결과 출력 및 저장
# ==================================================

summary = []

summary.append("======================================")
summary.append(" STRUCTURE EXPERIMENT VALIDATION")
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
