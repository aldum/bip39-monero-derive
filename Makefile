# vi: set noet:

test:
	/usr/bin/env python derive.py


clean:
	rm -rf dist/*

dist_exe:
	pyinstaller -F derive.py

dist_script:
	stickytape derive.py --add-python-path . --python-binary .venv/bin/python --output-file dist/prog.py
