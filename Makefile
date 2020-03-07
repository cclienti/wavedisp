PROJECT_DIR    ?= wavedisp
TESTS_DIR      ?= tests
PYLINT_SCORE   ?= 9.5


flake8: venv3
	source venv3/bin/activate && flake8 $(PROJECT_DIR) $(TESTS_DIR)

pylint: venv3
	source venv3/bin/activate && pylint-fail-under --fail_under $(PYLINT_SCORE) $(PROJECT_DIR) $(TESTS_DIR)

pytest: venv3
	source venv3/bin/activate && $@

upload: test-install
	source venv3/bin/activate && twine upload -u $$PYPI_PROD_USER -p $$PYPI_PROD_PASSWORD dist/*
	touch upload

test-install: test-upload
	python3 -m venv test-install
	source test-install/bin/activate && pip install --index-url https://test.pypi.org/simple/ --no-deps $(PROJECT_DIR)

test-upload: dist
	source venv3/bin/activate && \
	   twine upload --verbose -u $$PYPI_TEST_USER -p $$PYPI_TEST_PASSWORD --repository-url https://test.pypi.org/legacy/ dist/*
	touch test-upload

dist: venv3
	source venv3/bin/activate && python3 setup.py sdist bdist_wheel

venv3:
	python3 -m venv venv3
	source venv3/bin/activate && pip install --upgrade pip
	source venv3/bin/activate && \
	    pip install flake8 pylint twine pytest pytest-cov pylint-fail-under

clean:
	rm -rf dist venv3 test-install test-upload upload
	rm -rf $(PROJECT_DIR).egg-info
	rm -rf test_*.dot test_*.tcl tests.xml coverage.xml htmlcov
