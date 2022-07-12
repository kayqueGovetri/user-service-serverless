_install_dev:
	pip install -r requirements_dev.txt
	pre-commit install

_install_prod:
	pip install -r requirements.txt

_flake8:
	@flake8 --show-source user_service/

_black:
	@black --check --safe user_service/

_black_fix:
	@black user_service/

_isort-fix:
	@isort --profile=black user_service/

_isort:
	@isort --diff --check-only --profile=black user_service/

up:
	sam local start-api

build:
	sam build


lint: _flake8 _isort _black
format-code: _black_fix _isort-fix ## Format code
dev: _install_prod _install_dev
prod: _install_prod
start: build up