
import csv
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt


# ==================================================
# 1. 파일 경로 및 실험 조건 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "report"
INPUT_FILE = REPORT_DIR / "combined_density_results.csv"

FIGURE_DIR = BASE_DIR / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

CROSSOVER_FILE = REPORT_DIR / "density_crossover_summary.csv"

LANGUAGES = ["C", "Python"]
ALGORITHMS = ["Dense", "CSR", "CSC"]
STRUCTURES = ["Random", "Banded", "Row", "Block"]
MATRIX_SIZES = [100, 500, 1000, 2000]

EXPECTED_DENSITIES = [
    i / 100
    for i in range(1, 51)
]

METRICS = {
    "matvec_ms": {
        "filename": "matvec",
        "ylabel": "MatVec Time (ms)",
        "title": "MatVec Execution Time"
    },
    "memory_bytes": {
        "filename": "memory",
        "ylabel": "Memory Usage (MB)",
        "title": "Memory Usage"
    },
    "conversion_ms": {
        "filename": "conversion",
        "ylabel": "Conversion Time (ms)",
        "title": "Conversion Time"
    },
    "total_ms": {
        "filename": "total",
        "ylabel": "Total Time (ms)",
        "title": "Total Execution Time"
    }
}


# ==================================================
# 2. CSV 데이터 읽기
# ==================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"실험 결과 파일을 찾을 수 없습니다: {INPUT_FILE}"
    )

required_columns = {
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
}

data = []

with open(
    INPUT_FILE,
    "r",
    newline="",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)

    if (
        not reader.fieldnames
        or not required_columns.issubset(reader.fieldnames)
    ):
        raise ValueError(
            "CSV 파일의 열 구성이 올바르지 않습니다."
        )

    for line_number, row in enumerate(reader, start=2):

        if row["valid"] != "1":
            continue

        try:
            conversion_ms = float(row["conversion_ms"])
            matvec_ms = float(row["matvec_ms"])

            item = {
                "language": row["language"],
                "structure": row["structure"],
                "algorithm": row["algorithm"],
                "rows": int(row["rows"]),
                "cols": int(row["cols"]),
                "density": float(row["density"]),
                "nnz": int(row["nnz"]),
                "actual_density": float(row["actual_density"]),
                "conversion_ms": conversion_ms,
                "matvec_ms": matvec_ms,
                "memory_bytes": int(row["memory_bytes"]),
                "total_ms": conversion_ms + matvec_ms
            }

            data.append(item)

        except (ValueError, TypeError, KeyError):
            raise ValueError(
                f"{line_number}번째 행의 데이터 형식이 잘못되었습니다."
            )


if not data:
    raise ValueError("분석할 데이터가 없습니다.")

print(f"분석 데이터 수: {len(data)}")


# ==================================================
# 3. 실험 데이터 그룹화
# ==================================================

# 하나의 그룹:
# 언어 + 행렬 구조 + 행렬 크기
#
# 각 그룹 내부에서 Density와 알고리즘을 구분한다.

groups = defaultdict(dict)

for row in data:

    group_key = (
        row["language"],
        row["structure"],
        row["rows"],
        row["cols"]
    )

    algorithm_key = (
        row["algorithm"],
        row["density"]
    )

    if algorithm_key in groups[group_key]:
        raise ValueError(
            f"중복 데이터 발견: {group_key}, {algorithm_key}"
        )

    groups[group_key][algorithm_key] = row


# ==================================================
# 4. 실험 조건 검증
# ==================================================

expected_group_count = (
    len(LANGUAGES)
    * len(STRUCTURES)
    * len(MATRIX_SIZES)
)

if len(groups) != expected_group_count:
    raise ValueError(
        f"실험 그룹 수가 올바르지 않습니다. "
        f"현재: {len(groups)}, 예상: {expected_group_count}"
    )


expected_rows_per_group = (
    len(EXPECTED_DENSITIES)
    * len(ALGORITHMS)
)

for group_key, records in groups.items():

    if len(records) != expected_rows_per_group:
        raise ValueError(
            f"{group_key} 그룹의 데이터 개수가 올바르지 않습니다."
        )

    for algorithm in ALGORITHMS:
        for density in EXPECTED_DENSITIES:

            key = (algorithm, density)

            if key not in records:
                raise ValueError(
                    f"데이터 누락: {group_key}, {key}"
                )

print("모든 실험 조건 확인 완료")


# ==================================================
# 5. 그래프 저장 함수
# ==================================================

def save_plot(filename):

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"그래프 생성 완료: {filename}")


# ==================================================
# 6. 지표별 데이터 추출 함수
# ==================================================

def get_metric_values(records, algorithm, metric):

    values = []

    for density in EXPECTED_DENSITIES:

        row = records[(algorithm, density)]

        value = row[metric]

        # 메모리 단위 변환: Byte -> MB
        if metric == "memory_bytes":
            value /= (1024 * 1024)

        values.append(value)

    return values


# ==================================================
# 7. Density별 그래프 생성
# ==================================================

plot_count = 0

for group_key, records in sorted(groups.items()):

    language, structure, rows, cols = group_key

    for metric, settings in METRICS.items():

        plt.figure(figsize=(10, 6))

        for algorithm in ALGORITHMS:

            y_values = get_metric_values(
                records,
                algorithm,
                metric
            )

            plt.plot(
                EXPECTED_DENSITIES,
                y_values,
                marker="o",
                markersize=3,
                linewidth=1.5,
                label=algorithm
            )

        plt.xlabel("Density")
        plt.ylabel(settings["ylabel"])

        plt.title(
            f"{language} - {structure} - "
            f"{rows}x{cols}: {settings['title']}"
        )

        plt.xticks(
            [i / 100 for i in range(0, 51, 5)]
        )

        plt.grid(True, alpha=0.3)
        plt.legend()

        filename = (
            f"density_{settings['filename']}_"
            f"{language.lower()}_"
            f"{structure.lower()}_"
            f"{rows}.png"
        )

        save_plot(filename)

        plot_count += 1


# ==================================================
# 8. 성능 역전 지점 계산 함수
# ==================================================

def find_crossover(
    dense_values,
    sparse_values,
    densities
):
    """
    Dense와 Sparse의 성능 차이를 비교한다.

    difference = Sparse - Dense

    difference < 0:
        Sparse가 Dense보다 유리

    difference > 0:
        Dense가 Sparse보다 유리

    첫 번째 역전 구간을 탐색하고
    선형 보간으로 추정 Density를 계산한다.
    """

    differences = [
        sparse - dense
        for dense, sparse in zip(
            dense_values,
            sparse_values
        )
    ]

    # 첫 번째 Density부터 Sparse가 Dense보다
    # 느리거나 메모리를 더 사용하는 경우
    if differences[0] >= 0:

        return {
            "status": "처음부터 Dense가 유리",
            "lower_density": "",
            "upper_density": "",
            "estimated_density": ""
        }

    # Sparse가 유리하다가 Dense가 유리해지는 지점 탐색
    for i in range(1, len(differences)):

        previous = differences[i - 1]
        current = differences[i]

        if current >= 0:

            lower = densities[i - 1]
            upper = densities[i]

            if current == 0:

                estimated = upper

            elif previous == current:

                estimated = upper

            else:

                estimated = (
                    lower
                    + (
                        -previous
                        / (current - previous)
                    ) * (upper - lower)
                )

            return {
                "status": "역전 발생",
                "lower_density": lower,
                "upper_density": upper,
                "estimated_density": estimated
            }

    return {
        "status": "관측 범위 내 역전 없음",
        "lower_density": "",
        "upper_density": "",
        "estimated_density": ""
    }


# ==================================================
# 9. 성능 역전 분석
# ==================================================

crossover_results = []

for group_key, records in sorted(groups.items()):

    language, structure, rows, cols = group_key

    dense_matvec = get_metric_values(
        records,
        "Dense",
        "matvec_ms"
    )

    dense_memory = get_metric_values(
        records,
        "Dense",
        "memory_bytes"
    )

    dense_total = get_metric_values(
        records,
        "Dense",
        "total_ms"
    )

    for algorithm in ["CSR", "CSC"]:

        comparisons = {
            "matvec_ms": (
                dense_matvec,
                get_metric_values(
                    records,
                    algorithm,
                    "matvec_ms"
                )
            ),
            "memory_bytes": (
                dense_memory,
                get_metric_values(
                    records,
                    algorithm,
                    "memory_bytes"
                )
            ),
            "total_ms": (
                dense_total,
                get_metric_values(
                    records,
                    algorithm,
                    "total_ms"
                )
            )
        }

        for metric, (dense_values, sparse_values) in comparisons.items():

            result = find_crossover(
                dense_values,
                sparse_values,
                EXPECTED_DENSITIES
            )

            crossover_results.append({
                "language": language,
                "structure": structure,
                "rows": rows,
                "cols": cols,
                "algorithm": algorithm,
                "metric": metric,
                **result
            })


# ==================================================
# 10. 성능 역전 결과 CSV 저장
# ==================================================

crossover_fields = [
    "language",
    "structure",
    "rows",
    "cols",
    "algorithm",
    "metric",
    "status",
    "lower_density",
    "upper_density",
    "estimated_density"
]

with open(
    CROSSOVER_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=crossover_fields
    )

    writer.writeheader()
    writer.writerows(crossover_results)

print(
    f"\n성능 역전 분석 결과 저장 완료: {CROSSOVER_FILE}"
)


# ==================================================
# 11. 최종 결과 출력
# ==================================================

print("\n======================================")
print(" DENSITY EXPERIMENT GRAPH GENERATION")
print("======================================")

print(f"분석 데이터: {len(data)}행")
print(f"실험 그룹: {len(groups)}개")
print(f"생성 그래프: {plot_count}개")
print(f"역전 분석 결과: {len(crossover_results)}개")

print(f"그래프 저장 위치: {FIGURE_DIR}")
print(f"역전 분석 파일: {CROSSOVER_FILE}")

print("======================================")
print("모든 작업이 완료되었습니다.")
print("======================================")
