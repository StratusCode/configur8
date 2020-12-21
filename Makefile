.PHONY: clean dev package publish test lint

COV_REPORT ?= html
GEMFURY_USERNAME ?= bradg

clean:
	@rm -rf dist build htmlcov

local:
	@pip install -e .[dev] --extra-index-url=https://$(GEMFURY_TOKEN):@pypi.fury.io/$(GEMFURY_USERNAME)/

package: clean
	python setup.py sdist
	python setup.py bdist_wheel

publish: package
	TWINE_USERNAME=$(GEMFURY_PUBLISH_TOKEN) twine upload dist/* \
		--repository-url https://push.fury.io/$(GEMFURY_USERNAME) \
		-p ""

test:
	pytest -s --cov-report $(COV_REPORT) --cov --mypy-ini-file=setup.cfg

lint:
	mypy src/
	flake8 src/ tests
