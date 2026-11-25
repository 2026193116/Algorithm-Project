# 빌드와 테스트를 한 단어로 돌리기 위한 Makefile.
# 컨테이너 안에서 실행한다 (docker compose exec lab bash).
#
#   make run             Density 심화 실험 실행 (C, Python)
#   make test            유닛 테스트 (C, Python)
#   make verify-density  C Density 실험의 CSR·CSC 결과가 Dense와 같은지 재검증
#   make debug           디버그 심볼을 넣어 빌드 (VS Code의 F5가 쓴다)
#   make clean           빌드 산출물 정리
#
# 실행 파일은 `*.out`으로 만든다. .gitignore가 그것만 걸러낸다.

CC ?= gcc
CFLAGS ?= -std=c17 -Wall -Wextra -O2
# 디버그 빌드: 최적화를 끄고 심볼을 남긴다 (VS Code의 F5가 이 결과물을 쓴다).
# `-I`는 아래 패턴 규칙이 대상 파일의 폴더로 붙인다. 여기서 고정하지 않는다.
DEBUGFLAGS ?= -std=c17 -Wall -Wextra -g -O0

.PHONY: all run run-c run-py test test-c test-py check-c-syntax debug clean verify-density

all: test

run: run-c run-py

run-c: src/main_density.out
	@./src/main_density.out

run-py:
	@python3 src/main_density.py

test: test-c test-py

test-c: check-c-syntax tests/test.out
	@./tests/test.out

test-py:
	@python3 -m unittest discover -s tests -p 'test*.py' -v

check-c-syntax:
	$(CC) $(CFLAGS) -Isrc -fsyntax-only $(wildcard src/*.c)

debug: src/main_density.debug.out

# src/ 에는 main이 둘(main.c, main_density.c)이므로 아래 패턴 규칙(`%.out`)을 쓰면
# 두 main이 함께 링크되어 실패한다. 실험 실행 파일은 명시 규칙으로 필요한 파일만 링크한다.
# 명시 규칙이 패턴 규칙보다 우선한다.
COMMON_C := src/benchmark.c src/data_generator.c src/dense.c src/csr.c src/csc.c
COMMON_H := $(wildcard src/*.h)

src/main.out: src/main.c $(COMMON_C) $(COMMON_H)
	$(CC) $(CFLAGS) -Isrc -o $@ src/main.c $(COMMON_C) -lm

src/main_density.out: src/main_density.c $(COMMON_C) $(COMMON_H)
	$(CC) $(CFLAGS) -Isrc -o $@ src/main_density.c $(COMMON_C) -lm

src/main_density.debug.out: src/main_density.c $(COMMON_C) $(COMMON_H)
	$(CC) $(DEBUGFLAGS) -Isrc -o $@ src/main_density.c $(COMMON_C) -lm

# C Density 실험 결과(report/c_density_results.csv)를 같은 난수 순서로 재현해
# CSR·CSC가 Dense와 일치하는지 검사한다. (`valid` 열은 정확성 검사가 아니다.)
src/verify_density.out: src/verify_density.c $(COMMON_C) $(COMMON_H)
	$(CC) $(CFLAGS) -Isrc -o $@ src/verify_density.c src/data_generator.c src/dense.c src/csr.c src/csc.c -lm

verify-density: src/verify_density.out
	@./src/verify_density.out

# 파일 하나를 그 자리에서 빌드한다. 같은 폴더의 .c를 함께 링크하므로 헤더에
# 선언만 있고 구현이 옆 파일에 있어도 된다. 대신 **한 폴더에 main은 하나만** 둔다.
#   %.out        실행용 (Code Runner의 ▶ 버튼이 이 규칙을 부른다)
#   %.debug.out  디버그용 (VS Code의 "C 디버그 (현재 파일)"이 부른다)
# 명시 규칙(tests/test.out 등)이 있으면 그쪽이 우선한다.
%.out: %.c
	$(CC) $(CFLAGS) -I$(@D) -o $@ $(wildcard $(@D)/*.c)

%.debug.out: %.c
	$(CC) $(DEBUGFLAGS) -I$(@D) -o $@ $(wildcard $(@D)/*.c)

tests/test.out: tests/test.c src/dense.c src/dense.h src/csr.c src/csr.h \
		src/csc.c src/csc.h src/data_generator.c src/data_generator.h
	$(CC) $(CFLAGS) -Isrc -o $@ tests/test.c src/dense.c src/csr.c \
		src/csc.c src/data_generator.c

clean:
	rm -f src/*.out tests/*.out tools/*.out
	rm -rf src/__pycache__ tests/__pycache__
