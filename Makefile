 .PHONY: default
default: package

.PHONY: venv
venv:
	test -d venv || virtualenv -p /usr/bin/python3 ./venv

.PHONY: package
package:
		python3 setup.py sdist

.PHONY: install
install:
		python3 setup.py install

## Remove Python build artifacts
.PHONY: clean-build
clean-build:
		rm -rvf ./build/
		rm -rvf ./dist/
		rm -rvf ./.eggs/
		rm -rvf ./*egg-info

## Remove Python file artifacts and binaries
.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -delete -print
	find . -name '*.pyo' -delete -print
	find . -name '*~' -delete -print
	find . -name '__pycache__' -delete -print


.PHONY: clean
clean: clean-build clean-pyc
		rm -rf ./tests/.cache

.PHONY: distclean
distclean:
	git clean -fdX