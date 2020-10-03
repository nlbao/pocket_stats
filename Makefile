setup:
	pip install pytest pytest-cov flake8 twine freezegun
	pip install .

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f .coverage.*

clean: clean-pyc clean-test

test: clean
	pytest tests --cov=pocket_stats --cov-report=term-missing

lint:
	python -m flake8 .

check: test lint

test-package:
	rm -rf ./dist
	python3 setup.py sdist
	twine check dist/*

release-package:
	python3 setup.py register sdist
	twine upload dist/*
