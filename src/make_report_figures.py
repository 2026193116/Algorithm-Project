"""보고서(REPORT.md)에 들어가는 결과 그래프 8개를 통합 CSV에서 만든다.

    python3 src/make_report_figures.py

입력 : report/combined_density_results.csv
출력 : report/*.svg  (보고서가 참조하는 파일명 그대로)

모든 그래프는 같은 규칙을 쓴다.
  - 라벨은 한국어로 통일한다.
  - 행렬 크기 비교는 두 언어 모두 'Random, Density 10%' 조건으로 같다.
  - Density별 그래프에서 같은 시리즈 중앙값의 1.2배를 넘는 Dense 측정값은
    '이상값'으로 표시한다(값은 지우지 않는다).
"""
import csv
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "report" / "combined_density_results.csv"
OUT_DIR = ROOT / "report"

# 한글이 깨지지 않도록 설치된 글꼴 중 첫 번째를 쓴다.
available = {f.name for f in font_manager.fontManager.ttflist}
for name in ["Noto Sans CJK KR", "NanumGothic", "Malgun Gothic", "AppleGothic", "DejaVu Sans"]:
    if name in available:
        plt.rcParams["font.family"] = name
        break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "path"      # 글자를 도형으로 저장해 글꼴이 없는 PC에서도 똑같이 보인다

COLORS = {"Dense": "#475569", "CSR": "#2563eb", "CSC": "#ea580c"}
MARKERS = {"Dense": "o", "CSR": "s", "CSC": "^"}
ALGS = ["Dense", "CSR", "CSC"]
LANG_NAME = {"C": "C", "Python": "Python"}

with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    ROWS = list(csv.DictReader(f))


def select(lang, structure, alg, rows=None, density=None):
    out = [
        r for r in ROWS
        if r["language"] == lang and r["structure"] == structure and r["algorithm"] == alg
        and (rows is None or int(r["rows"]) == rows)
        and (density is None or abs(float(r["density"]) - density) < 1e-9)
    ]
    return sorted(out, key=lambda r: (int(r["rows"]), float(r["density"])))


def finish(ax, title, xlabel, ylabel, fig, name, legend=True):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    if legend:
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / name, format="svg")
    plt.close(fig)


def density_matvec(lang, name):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for alg in ALGS:
        pts = select(lang, "Random", alg, rows=1000)
        x = [float(r["density"]) * 100 for r in pts]
        y = [float(r["matvec_ms"]) for r in pts]
        ax.plot(x, y, marker=MARKERS[alg], ms=3.5, lw=1.4, color=COLORS[alg], label=alg)
        if alg == "Dense":
            med = statistics.median(y)
            for xi, yi in zip(x, y):
                if yi > 1.2 * med:
                    ax.annotate(f"이상값 {yi:.2f} ms", (xi, yi), textcoords="offset points",
                                xytext=(8, -4), fontsize=8.5, color="#b91c1c",
                                arrowprops=dict(arrowstyle="-", color="#b91c1c", lw=0.8))
                    ax.plot([xi], [yi], "o", mfc="none", mec="#b91c1c", ms=9)
            ax.axhline(med, color=COLORS["Dense"], lw=0.8, ls=":")
    finish(ax, f"{lang} · Random · 1000×1000: Density별 행렬-벡터 곱셈 시간",
           "목표 Density (%)", "곱셈 시간 (ms)", fig, name)


def density_memory(lang, name):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for alg in ALGS:
        pts = select(lang, "Random", alg, rows=1000)
        ax.plot([float(r["density"]) * 100 for r in pts],
                [int(r["memory_bytes"]) / 1e6 for r in pts],
                marker=MARKERS[alg], ms=3.5, lw=1.4, color=COLORS[alg], label=alg)
    note = ("C: 자료형 크기×원소 수로 계산한 값" if lang == "C"
            else "Python: sys.getsizeof 재귀 합(중복 객체 제외)")
    finish(ax, f"{lang} · Random · 1000×1000: Density별 메모리 사용량 ({note})",
           "목표 Density (%)", "메모리 (MB)", fig, name)


def size_scaling(lang, name):
    sizes = [100, 500, 1000, 2000]
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for alg in ALGS:
        ys = [float(select(lang, "Random", alg, rows=n, density=0.10)[0]["matvec_ms"]) for n in sizes]
        slope = math.log(ys[-1] / ys[0]) / math.log(sizes[-1] / sizes[0])
        ax.loglog(sizes, ys, marker=MARKERS[alg], lw=1.6, color=COLORS[alg],
                  label=f"{alg} (기울기 {slope:.2f})")
    # 기준선: 100×100 Dense 값에서 시작하는 n² 직선
    base = float(select(lang, "Random", "Dense", rows=100, density=0.10)[0]["matvec_ms"])
    ax.loglog(sizes, [base * (n / 100) ** 2 for n in sizes], "k--", lw=0.9, label="기준선 n² (기울기 2)")
    ax.set_xticks(sizes)
    ax.set_xticklabels([str(n) for n in sizes])
    finish(ax, f"{lang} · Random · Density 10%: 행렬 크기별 곱셈 시간 (로그-로그)",
           "행렬 크기 n (n×n)", "곱셈 시간 (ms)", fig, name)


def structure_bars(lang, name):
    structures = ["Random", "Banded", "Row", "Block"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    width = 0.26
    for k, alg in enumerate(ALGS):
        ys = [float(select(lang, s, alg, rows=1000, density=0.10)[0]["matvec_ms"]) for s in structures]
        ax.bar([i + (k - 1) * width for i in range(4)], ys, width, color=COLORS[alg], label=alg)
    ax.set_xticks(range(4))
    ax.set_xticklabels(structures)
    finish(ax, f"{lang} · 1000×1000 · Density 10%: 분포 구조별 곱셈 시간",
           "원소 분포 구조", "곱셈 시간 (ms)", fig, name)


if __name__ == "__main__":
    density_matvec("C", "density-matvec-c-1000.svg")
    density_memory("C", "density-memory-c-1000.svg")
    density_matvec("Python", "python-density-matvec-1000.svg")
    density_memory("Python", "python-density-memory-1000.svg")
    size_scaling("C", "size-matvec-c.svg")
    size_scaling("Python", "python-size-matvec.svg")
    structure_bars("C", "structure-matvec-c.svg")
    structure_bars("Python", "python-structure-matvec.svg")
    print("그래프 8개를 report/ 에 저장했습니다.")
