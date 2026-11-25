# 희소 행렬 저장 방식에 따른 행렬-벡터 곱셈 성능 비교

Dense, CSR(Compressed Sparse Row), CSC(Compressed Sparse Column) 세 가지
행렬 저장 방식으로 행렬-벡터 곱셈을 구현하고, C언어와 Python에서 실행
시간과 메모리 사용량을 비교하는 프로젝트입니다.

핵심 연산은 다음과 같습니다.

$$ y = Ax $$

프로젝트에서는 행렬 크기, 비제로 원소 밀도(Density), 비제로 원소의 분포
구조를 바꾸어 실험합니다. 실험 결과는 CSV로 저장하고, 통합·검증한 뒤
그래프로 시각화합니다.

## 1. 비교 대상 및 실험 조건

### 저장 방식

  -----------------------------------------------------------------------
  방식                    저장 방법               행렬-벡터 곱셈의 접근
                                                  방식
  ----------------------- ----------------------- -----------------------
  Dense                   모든 행렬 원소를 2차원  모든 행과 열을 순회
                          배열에 저장             

  CSR                     비제로 원소, 열 인덱스, 행별 비제로 원소만 순회
                          행별 시작 위치를 저장   

  CSC                     비제로 원소, 행 인덱스, 열별 비제로 원소를
                          열별 시작 위치를 저장   순회하고 결과 벡터에
                                                  누적
  -----------------------------------------------------------------------

### 실험 조건

  항목             기본 구조 실험                           Density 심화 실험
  ---------------- ---------------------------------------- -------------------
  행렬 크기        100×100, 500×500, 1000×1000, 2000×2000   동일
  목표 Density     1%, 5%, 10%, 30%, 50%                    1%\~50%, 1% 간격
  원소 분포 구조   Random, Banded, Row, Block               동일
  저장 방식        Dense, CSR, CSC                          동일
  구현 언어        C, Python                                C, Python

정확성은 Dense의 계산 결과를 기준으로 CSR과 CSC의 결과가 일치하는지로
확인합니다. Python의 모든 실험과 C 기본 구조 실험(`main.c`)은 실행 중에
비교하여 CSV의 `valid` 열에 기록합니다. C Density 실험(`main_density.c`)은
실행 중 비교를 하지 않고 `valid`에 시간 측정 성공 여부만 기록하므로,
[6.5 C Density 결과의 정확성 재검증](#65-c-density-결과의-정확성-재검증)으로
따로 확인합니다. 측정 항목은 변환 시간, 행렬-벡터 곱셈 시간, 메모리
사용량입니다.

## 2. 준비 환경

### 권장 환경: GitHub Codespaces 또는 Dev Containers

저장소에는 `.devcontainer/`, `Dockerfile`, `compose.yml`이 포함되어
있습니다. Codespaces 또는 VS Code Dev Containers를 사용하면 저장소에
정의된 컨테이너 환경에서 C와 Python 코드를 실행할 수 있습니다.

### 로컬 실행에 필요한 프로그램

-   Git
-   Docker 및 Docker Compose
-   VS Code 사용 시 Dev Containers 확장(선택)

컨테이너에는 GCC, Make, GDB, Python 3가 설치됩니다. 그래프 생성에는
Python의 `matplotlib`가 추가로 필요합니다.

## 3. 프로젝트 내려받기 및 실행 환경 시작

### 3.1 GitHub Codespaces 사용

1.  GitHub에서 이 저장소를 엽니다.
2.  **Code → Codespaces → Create codespace on main**을 선택합니다.
3.  Codespaces가 실행되면 VS Code 터미널을 엽니다.
4.  아래 [4. 테스트 실행](#4-테스트-실행)으로 이동합니다.

### 3.2 로컬에서 Docker 사용

터미널에서 저장소를 내려받고 프로젝트 폴더로 이동합니다.

``` bash
git clone <저장소 URL>
cd Algorithm-Project
```

`<저장소 URL>`은 본인의 GitHub 저장소 주소로 바꿉니다. 압축 파일(zip)을
내려받은 경우에는 압축을 푼 뒤 폴더명이 `Algorithm-Project-main`이므로
그 폴더로 이동합니다.

저장소 루트 폴더에서 컨테이너를 시작하고 셸에 접속합니다.

``` bash
docker compose up -d --build
docker compose exec lab bash
```

이후의 명령은 별도 표시가 없는 한 컨테이너 내부의 프로젝트
루트(`/work`)에서 실행합니다.

## 4. 테스트 실행

실험을 실행하기 전에 테스트를 수행하여 C와 Python 구현의 기본 동작을
확인합니다.

``` bash
make test
```

이 명령은 다음을 수행합니다.

-   C 소스 파일의 문법 검사 및 테스트 프로그램 실행
-   Python 테스트 실행
-   Dense, CSR, CSC의 행렬-벡터 곱셈 결과 비교
-   직사각형 행렬 및 모든 원소가 0인 행렬 처리 확인
-   데이터 생성기의 재현성과 입력 조건 검사

테스트가 정상적으로 끝나면 C 테스트와 Python 테스트가 모두 통과했다는
결과가 출력됩니다.

언어별로 따로 실행하려면 다음 명령을 사용합니다.

``` bash
make test-c
make test-py
```

## 5. 기본 구조 실험 실행

기본 구조 실험은 네 가지 행렬 구조와 다섯 가지 Density를 조합하여 세
저장 방식의 결과를 비교합니다.

### 5.1 C언어 실험

프로젝트 루트에서 다음 명령을 실행합니다.

``` bash
gcc -std=c17 -Wall -Wextra -O2 -Isrc \
    src/main.c \
    src/benchmark.c \
    src/data_generator.c \
    src/dense.c \
    src/csr.c \
    src/csc.c \
    -o src/main.out -lm

./src/main.out
```

실행이 끝나면 다음 파일이 생성됩니다.

``` text
report/c_structure_results.csv
```

### 5.2 Python 실험

새 터미널을 열거나 같은 터미널에서 다음 명령을 실행합니다.

``` bash
python3 src/main.py
```

실행이 끝나면 다음 파일이 생성됩니다.

``` text
report/python_structure_results.csv
```

### 5.3 C와 Python 결과 통합

두 실험이 모두 끝난 뒤 다음 명령을 실행합니다.

``` bash
python3 src/merge_results.py
```

C와 Python의 결과가 하나의 CSV 파일로 통합됩니다.

``` text
report/combined_structure_results.csv
```

### 5.4 기본 구조 실험 그래프 생성

`matplotlib`가 설치되어 있어야 합니다. Docker 컨테이너에서 그래프를 처음
생성하는 경우 다음 명령으로 설치할 수 있습니다.

``` bash
apt-get update
apt-get install -y python3-matplotlib
```

그다음 그래프 생성 스크립트를 실행합니다.

``` bash
python3 src/plot_results.py
```

생성된 그래프는 `figures/` 폴더에 저장됩니다.

## 6. Density 심화 실험 실행

Density 심화 실험은 행렬 크기와 분포 구조를 유지하면서 목표 Density를
1%부터 50%까지 1% 간격으로 바꾸어 실행합니다. 실험량이 기본 구조
실험보다 많으므로 실행이 완료될 때까지 기다립니다.

### 6.1 C언어 Density 실험

``` bash
gcc -std=c17 -Wall -Wextra -O2 -Isrc \
    src/main_density.c \
    src/benchmark.c \
    src/data_generator.c \
    src/dense.c \
    src/csr.c \
    src/csc.c \
    -o src/main_density.out -lm

./src/main_density.out
```

생성 파일:

``` text
report/c_density_results.csv
```

### 6.2 Python Density 실험

``` bash
python3 src/main_density.py
```

생성 파일:

``` text
report/python_density_results.csv
```

### 6.3 Density 결과 통합

C와 Python 실험이 모두 완료된 뒤 실행합니다.

``` bash
python3 src/merge_density_results.py
```

생성 파일:

``` text
report/combined_density_results.csv
```

### 6.4 통합 결과 검증

``` bash
python3 src/validate_results.py
```

검증 결과는 다음 파일에 기록됩니다.

``` text
report/density_validation_summary.txt
```

검증에 실패한 항목이 있다면 요약 파일과 터미널 메시지를 확인한 뒤 원본
실험 결과를 점검합니다.

이 스크립트의 `valid` 검사는 CSV의 `valid` 열이 1인지 확인할 뿐입니다.
C Density 행에서는 이 열이 정확성 비교가 아니므로, 같은 결과의 정확성은
다음 절의 도구로 확인합니다.

### 6.5 C Density 결과의 정확성 재검증

`main_density.c`는 CSR·CSC 결과를 Dense와 비교하지 않습니다. 이를
보완하는 `tools/verify_density.c`는 `main_density.c`와 같은 순서로
`srand(42)`, 행렬, 입력 벡터를 재현하여 800개 조건 전체에서 CSR·CSC가
Dense와 일치하는지 검사하고, `report/c_density_results.csv`의 조건·nnz와
순서대로 일치하는지도 확인합니다. C Density 실험을 실행해
`report/c_density_results.csv`를 만든 뒤 실행합니다.

``` bash
make verify-density
```

마지막 줄이 `PASS`이고 불일치가 0건이면 통과입니다(약 40초 소요).

### 6.6 Density 그래프 및 성능 역전 분석

``` bash
python3 src/plot_density_results.py
```

이 스크립트는 Density에 따른 행렬-벡터 곱셈 시간, 변환 시간, 전체 시간,
메모리 사용량을 그래프로 생성합니다. 또한 Dense와 CSR·CSC의 성능이
역전되는 Density를 추정합니다.

주요 생성 파일:

``` text
figures/                         # Density별 그래프
report/density_crossover_summary.csv
```

### 6.7 보고서용 결과 그래프(SVG) 생성

보고서에 실리는 결과 그래프 8개(Density별 곱셈 시간·메모리, 크기별 곱셈
시간(로그-로그), 구조별 곱셈 시간)를 통합 CSV에서 다시 만듭니다. 라벨은
한국어이므로 한글 글꼴(예: Noto Sans CJK, NanumGothic)이 필요합니다.
`report/*.svg`가 같은 이름으로 덮어써집니다.

``` bash
python3 src/make_report_figures.py
```

## 7. 실행 순서 한눈에 보기

처음부터 전체 실험을 진행할 때는 아래 순서를 따릅니다.

### 기본 구조 실험

``` bash
# 1. 테스트
make test

# 2. C 기본 구조 실험
gcc -std=c17 -Wall -Wextra -O2 -Isrc \
    src/main.c src/benchmark.c src/data_generator.c \
    src/dense.c src/csr.c src/csc.c \
    -o src/main.out -lm
./src/main.out

# 3. Python 기본 구조 실험
python3 src/main.py

# 4. 결과 통합
python3 src/merge_results.py

# 5. 그래프 생성
python3 src/plot_results.py
```

### Density 심화 실험

``` bash
# 1. C Density 실험
gcc -std=c17 -Wall -Wextra -O2 -Isrc \
    src/main_density.c src/benchmark.c src/data_generator.c \
    src/dense.c src/csr.c src/csc.c \
    -o src/main_density.out -lm
./src/main_density.out

# 2. Python Density 실험
python3 src/main_density.py

# 3. 결과 통합
python3 src/merge_density_results.py

# 4. 통합 데이터 검증
python3 src/validate_results.py

# 5. C Density 결과의 정확성 재검증
make verify-density

# 6. 그래프 및 성능 역전 분석
python3 src/plot_density_results.py

# 7. 보고서용 SVG 그래프
python3 src/make_report_figures.py
```

## 8. 주요 파일 및 폴더

``` text
Algorithm-Project/                 # zip으로 받으면 Algorithm-Project-main/
├── .devcontainer/              # Codespaces 및 Dev Containers 설정
├── .vscode/                    # VS Code 실행·디버그 설정
├── src/
│   ├── dense.c / dense.h       # C Dense 행렬-벡터 곱셈
│   ├── csr.c / csr.h           # C CSR 변환 및 행렬-벡터 곱셈
│   ├── csc.c / csc.h           # C CSC 변환 및 행렬-벡터 곱셈
│   ├── data_generator.c/.h     # C 행렬 데이터 생성
│   ├── benchmark.c/.h          # C 실행 시간·메모리 측정
│   ├── main.c                  # 기본 구조 C 실험
│   ├── main.py                 # 기본 구조 Python 실험
│   ├── main_density.c          # Density 심화 C 실험
│   ├── main_density.py         # Density 심화 Python 실험
│   ├── merge_results.py        # 기본 구조 CSV 통합
│   ├── merge_density_results.py# Density CSV 통합
│   ├── validate_results.py     # Density 통합 데이터 검증
│   ├── make_report_figures.py  # 보고서용 결과 그래프(SVG) 생성
│   ├── plot_results.py         # 기본 구조 그래프 생성
│   └── plot_density_results.py # Density 그래프·역전 분석
├── tools/
│   └── verify_density.c        # C Density 결과 정확성 재검증
├── tests/
│   ├── test.c                  # C 단위 테스트
│   └── test.py                 # Python 단위 테스트
├── report/
│   ├── REPORT.md               # 프로젝트 보고서
│   ├── *.svg                   # 구조도·흐름도 및 결과 그래프
│   ├── matvec-visualizer.html  # 행렬-벡터 연산 시각화
│   └── *.csv                  # 실험 결과 및 분석 데이터
├── figures/                    # 실험 결과 그래프(PNG)
├── Dockerfile
├── compose.yml
├── Makefile
└── README.md
```

## 9. 결과 파일 안내

  -----------------------------------------------------------------------------
  경로                                      내용
  ----------------------------------------- -----------------------------------
  `report/c_structure_results.csv`          C 기본 구조 실험 결과

  `report/python_structure_results.csv`     Python 기본 구조 실험 결과

  `report/combined_structure_results.csv`   기본 구조 실험 통합 결과

  `report/c_density_results.csv`            C Density 심화 실험 결과

  `report/python_density_results.csv`       Python Density 심화 실험 결과

  `report/combined_density_results.csv`     Density 심화 실험 통합 결과

  `report/density_validation_summary.txt`   Density 데이터 검증 결과

  `report/density_crossover_summary.csv`    Dense와 CSR·CSC의 성능 역전 분석

  `figures/`                                실험 결과 그래프
  -----------------------------------------------------------------------------

`report/`에 포함된 SVG 파일은 자료구조와 프로그램 실행 흐름을 설명하는
그림과, `src/make_report_figures.py`가 통합 CSV에서 만든 결과 그래프입니다. `report/matvec-visualizer.html`은 브라우저에서
열어 행렬-벡터 곱셈 과정을 확인할 수 있습니다.

## 10. 자주 사용하는 명령

  -----------------------------------------------------------------------
  명령                                기능
  ----------------------------------- -----------------------------------
  `make test`                         C 및 Python 테스트

  `make test-c`                       C 테스트

  `make test-py`                      Python 테스트

  `make run`                          C·Python Density 심화 실험 실행

  `make verify-density`               C Density 결과의 정확성 재검증

  `make clean`                        `src/`, `tests/`, `tools/`의 `.out`
                                      실행 파일과 Python 캐시 정리

  `docker compose up -d --build`      컨테이너 빌드 및 시작

  `docker compose exec lab bash`      컨테이너 셸 접속

  `docker compose down`               컨테이너 중지 및 정리
  -----------------------------------------------------------------------

## 11. 실행 시 유의 사항

-   모든 명령은 프로젝트 최상위 폴더에서 실행합니다.
-   C 실험은 `main.c`와 `main_density.c`가 각각 별도의 실행
    진입점이므로, 위에 제시된 것처럼 실행할 메인 파일을 명시하여
    컴파일합니다. `Makefile`의 `src/main.out`, `src/main_density.out`
    규칙은 필요한 파일만 링크하므로 `make run`도 사용할 수 있습니다.
-   C Density 결과(`c_density_results.csv`)의 `valid` 열은 정확성
    비교가 아닙니다. 정확성은 `make verify-density`로 확인합니다.
-   C의 난수는 `srand(42)`를 프로그램 시작에 한 번만 호출하므로 행렬이
    실행 순서에 의존합니다. 재현과 `make verify-density`는 전체 실험을
    같은 순서로 실행한 결과에 대해서만 성립합니다.
-   CSV 통합 스크립트는 해당 언어의 원본 CSV가 먼저 생성되어 있어야
    실행할 수 있습니다.
-   그래프 생성 스크립트는 통합 CSV가 있어야 하며, `matplotlib` 설치가
    필요합니다. `make_report_figures.py`는 한글 글꼴도 필요합니다.
-   실험 프로그램은 같은 이름의 CSV 파일을 새로 작성하므로, 이전 결과를
    보존하려면 실행 전에 별도 복사해 둡니다.
-   `make clean`은 실험 결과 CSV나 그래프를 삭제하지 않습니다.

컨테이너 작업을 마친 뒤에는 프로젝트 폴더에서 다음 명령으로 컨테이너를
정리할 수 있습니다.

``` bash
docker compose down
```
