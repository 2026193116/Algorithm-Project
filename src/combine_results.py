
import csv
from pathlib import Path

# 프로젝트 최상위 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

# 입력 및 출력 파일 경로
REPORT_DIR = BASE_DIR / "report"

C_FILE = REPORT_DIR / "c_results.csv"
PYTHON_FILE = REPORT_DIR / "python_results.csv"
OUTPUT_FILE = REPORT_DIR / "combined_results.csv"

# CSV 열 구성
EXPECTED_COLUMNS = [
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


def read_results(file_path):
    """CSV 파일을 읽고 실험 결과를 반환한다."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"{file_path.name}의 CSV 열 구성이 올바르지 않습니다."
            )

        return list(reader)


def main():
    # C와 Python 결과 읽기
    c_results = read_results(C_FILE)
    python_results = read_results(PYTHON_FILE)

    # 결과 통합
    all_results = c_results + python_results

    # 정렬: 행렬 크기 → Density → 알고리즘 → 언어
    algorithm_order = {
        "Dense": 0,
        "CSR": 1,
        "CSC": 2
    }

    all_results.sort(
        key=lambda row: (
            int(row["rows"]),
            int(row["cols"]),
            float(row["density"]),
            algorithm_order.get(row["algorithm"], 99),
            row["language"]
        )
    )

    # 통합 CSV 저장
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=EXPECTED_COLUMNS
        )

        writer.writeheader()
        writer.writerows(all_results)

    # 결과 확인
    print("===== 결과 통합 완료 =====")
    print(f"C 결과: {len(c_results)}개")
    print(f"Python 결과: {len(python_results)}개")
    print(f"전체 결과: {len(all_results)}개")

    print("\n===== 알고리즘별 결과 개수 =====")

    for language in ["C", "Python"]:
        for algorithm in ["Dense", "CSR", "CSC"]:
            count = sum(
                1 for row in all_results
                if row["language"] == language
                and row["algorithm"] == algorithm
            )

            print(f"{language} - {algorithm}: {count}개")

    # 정확성 검사 결과
    invalid_results = [
        row for row in all_results
        if row["valid"] != "1"
    ]

    if invalid_results:
        print(f"\n주의: 정확성 검증 실패 결과 {len(invalid_results)}개")
    else:
        print("\n모든 결과의 정확성 검증 통과!")

    print(f"\n저장 위치: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
