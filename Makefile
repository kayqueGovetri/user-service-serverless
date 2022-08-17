_install_dev:
	pip install -r requirements_dev.txt
	pre-commit install

_install_prod:
	pip install -r requirements.txt

_flake8:
	@flake8 --show-source user_service/ tests/ layers/ authorizer/

_black:
	@black --check --safe user_service/ tests/ layers/ authorizer/

_black_fix:
	@black user_service/ tests/ layers/  authorizer/

_isort-fix:
	@isort --profile=black user_service/ tests/ layers/ authorizer/

_isort:
	@isort --diff --check-only --profile=black user_service/ tests/ layers/ authorizer/

build:
	rm -rf .aws_sam
	sam build --use-container

deploy:
	@make build
	sam deploy

start:
	sam local start-api

###
# Tests section
###
test: ##=> Run pytest
	@pytest -x tests/

test-coverage:  ## Run tests with coverage output
	@pytest --cov --cov-report term-missing --cov-fail-under 80 tests/ -vv


lint: _flake8 _isort _black
format-code: _black_fix _isort-fix ## Format code
dev: _install_prod _install_dev
prod: _install_prod
run: build start