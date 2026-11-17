
import csv
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt


# ==================================================
# 1. 파일 경로 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# 실험 결과 CSV 파일
REPORT_DIR = BASE_DIR / "report"
INPUT_FILE = REPORT_DIR / "combined_results.csv"

# 그래프 저장 폴더
FIGURE_DIR = BASE_DIR / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. CSV 데이터 읽기
# ==================================================

data = []

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"실험 결과 파일을 찾을 수 없습니다: {INPUT_FILE}"
    )

with open(INPUT_FILE, "r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    required_columns = {
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
        "valid",
    }

    if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
        raise ValueError(
            "CSV 파일의 열 구성이 올바르지 않습니다."
        )

    for row in reader:

        # 정확성 검증을 통과한 데이터만 사용
        if row["valid"] != "1":
            continue

        data.append({
            "language": row["language"],
            "algorithm": row["algorithm"],
            "rows": int(row["rows"]),
            "cols": int(row["cols"]),
            "density": float(row["density"]),
            "nnz": int(row["nnz"]),
            "actual_density": float(row["actual_density"]),
            "conversion_ms": float(row["conversion_ms"]),
            "matvec_ms": float(row["matvec_ms"]),
            "memory_bytes": int(row["memory_bytes"]),
        })


if not data:
    raise ValueError("분석할 데이터가 없습니다.")

print(f"분석 데이터 수: {len(data)}")


# ==================================================
# 3. 공통 설정
# ==================================================

languages = ["C", "Python"]
algorithms = ["Dense", "CSR", "CSC"]


def calculate_average(rows, value_key, group_keys):
    """
    지정한 기준으로 데이터를 그룹화하고 평균을 계산한다.
    """

    groups = defaultdict(list)

    for row in rows:
        key = tuple(row[k] for k in group_keys)
        groups[key].append(row[value_key])

    result = {}

    for key, values in groups.items():
        result[key] = sum(values) / len(values)

    return result


def save_plot(filename):
    """
    그래프를 PNG 파일로 저장한다.
    """

    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    print(f"그래프 생성 완료: {filename}")


# ==================================================
# 4. 행렬 크기에 따른 실행 시간 비교
# ==================================================

size_time = calculate_average(
    data,
    "matvec_ms",
    ["language", "algorithm", "rows"]
)

plt.figure(figsize=(10, 6))

for language in languages:
    for algorithm in algorithms:

        x_values = sorted({
            key[2]
            for key in size_time
            if key[0] == language and key[1] == algorithm
        })

        y_values = [
            size_time[(language, algorithm, size)]
            for size in x_values
        ]

        if x_values:
            plt.plot(
                x_values,
                y_values,
                marker="o",
                label=f"{language} - {algorithm}"
            )

plt.xlabel("Matrix Size (rows)")
plt.ylabel("MatVec Time (ms)")
plt.title("MatVec Time by Matrix Size")
plt.legend()
plt.grid(True)

save_plot("time_by_size.png")


# ==================================================
# 5. Density에 따른 실행 시간 비교
# ==================================================

density_time = calculate_average(
    data,
    "matvec_ms",
    ["language", "algorithm", "density"]
)

plt.figure(figsize=(10, 6))

for language in languages:
    for algorithm in algorithms:

        x_values = sorted({
            key[2]
            for key in density_time
            if key[0] == language and key[1] == algorithm
        })

        y_values = [
            density_time[(language, algorithm, density)]
            for density in x_values
        ]

        if x_values:
            plt.plot(
                x_values,
                y_values,
                marker="o",
                label=f"{language} - {algorithm}"
            )

plt.xlabel("Density")
plt.ylabel("MatVec Time (ms)")
plt.title("MatVec Time by Density")
plt.legend()
plt.grid(True)

save_plot("time_by_density.png")


# ==================================================
# 6. 행렬 크기에 따른 메모리 사용량 비교
# ==================================================

size_memory = calculate_average(
    data,
    "memory_bytes",
    ["language", "algorithm", "rows"]
)

plt.figure(figsize=(10, 6))

for language in languages:
    for algorithm in algorithms:

        x_values = sorted({
            key[2]
            for key in size_memory
            if key[0] == language and key[1] == algorithm
        })

        y_values = [
            size_memory[(language, algorithm, size)] / (1024 * 1024)
            for size in x_values
        ]

        if x_values:
            plt.plot(
                x_values,
                y_values,
                marker="o",
                label=f"{language} - {algorithm}"
            )

plt.xlabel("Matrix Size (rows)")
plt.ylabel("Memory Usage (MB)")
plt.title("Memory Usage by Matrix Size")
plt.legend()
plt.grid(True)

save_plot("memory_by_size.png")


# ==================================================
# 7. Density에 따른 메모리 사용량 비교
# ==================================================

density_memory = calculate_average(
    data,
    "memory_bytes",
    ["language", "algorithm", "density"]
)

plt.figure(figsize=(10, 6))

for language in languages:
    for algorithm in algorithms:

        x_values = sorted({
            key[2]
            for key in density_memory
            if key[0] == language and key[1] == algorithm
        })

        y_values = [
            density_memory[(language, algorithm, density)] / (1024 * 1024)
            for density in x_values
        ]

        if x_values:
            plt.plot(
                x_values,
                y_values,
                marker="o",
                label=f"{language} - {algorithm}"
            )

plt.xlabel("Density")
plt.ylabel("Memory Usage (MB)")
plt.title("Memory Usage by Density")
plt.legend()
plt.grid(True)

save_plot("memory_by_density.png")


# ==================================================
# 8. C와 Python의 실행 시간 비교
# ==================================================

language_time = calculate_average(
    data,
    "matvec_ms",
    ["language", "algorithm", "rows"]
)

plt.figure(figsize=(10, 6))

for algorithm in algorithms:

    sizes = sorted({
        key[2]
        for key in language_time
        if key[1] == algorithm
    })

    ratios = []

    for size in sizes:

        c_time = language_time.get(("C", algorithm, size))
        python_time = language_time.get(("Python", algorithm, size))

        if (
            c_time is not None
            and python_time is not None
            and c_time > 0
        ):
            ratios.append(python_time / c_time)
        else:
            ratios.append(float("nan"))

    if sizes:
        plt.plot(
            sizes,
            ratios,
            marker="o",
            label=algorithm
        )

plt.axhline(
    y=1,
    linestyle="--",
    label="Same Execution Time"
)

plt.xlabel("Matrix Size (rows)")
plt.ylabel("Python / C Execution Time")
plt.title("Python vs C Performance Ratio")
plt.legend()
plt.grid(True)

save_plot("language_comparison.png")


# ==================================================
# 9. 최종 결과 출력
# ==================================================

print("\n================================")
print("모든 그래프 생성이 완료되었습니다.")
print(f"저장 위치: {FIGURE_DIR}")
print("================================")
