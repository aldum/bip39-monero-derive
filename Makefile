# vi: set noet:

BIN=.venv/bin

uname_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')
uname_M := $(shell sh -c 'uname -m 2>/dev/null || echo not')
UNI =
ifeq ($(uname_S),Linux)
	OS = linux
endif
ifneq (,$(findstring arm,$(uname_M)))
	ARCH = arm
endif
ifneq (,$(findstring x86_64,$(uname_M)))
	ARCH = x64
endif
ifneq (,$(findstring riscv,$(uname_M)))
	ARCH = $(uname_M)
endif
ifeq ($(uname_S),Darwin)
	OS = macos
	ARCH = universal
	UNI = --target-arch universal2
endif

test:
	/usr/bin/env python derive.py

clean:
	rm -rf dist/*

dist_exe: check_venv
	$(BIN)/pyinstaller -F derive.py $(UNI) -n derive-$(OS)-$(ARCH)

dist_script: check_venv
	$(BIN)/stickytape derive.py \
		--add-python-path . \
		--add-python-module 'importlib.machinery' \
		--python-binary $(BIN)/python \
		--output-file dist/prog.py

dist_all: dist_exe dist_script

check_venv:
	test -f $(BIN)/python

create_venv:
	python3.9 -m venv .venv
	$(BIN)/pip install poetry
	$(BIN)/poetry install


