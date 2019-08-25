dist:
	python setup.py sdist bdist_wheel

test-upload: dist
	twine upload --verbose -u $$PYPI_TEST_USER -p $$PYPI_TEST_PASSWORD --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*

test-install:
	pip install --index-url https://test.pypi.org/simple/ --no-deps wavedisp

clean:
	rm -rf dist
