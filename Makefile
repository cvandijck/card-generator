ifeq ($(OS), Windows_NT)
	MAKE_OS := Windows
else
	MAKE_OS := Linux
endif

PYTHON_VERSION = 3.12
VENV_NAME = .venv
DOCKER_TAG = card-generator

BUILD_DIR = ./_build
BUILD_WHEEL_DIR = $(BUILD_DIR)/wheel
BUILD_TEST_DIR = $(BUILD_DIR)/test

UV = uv
CREATE_ENV_CMD=$(UV) venv --python $(PYTHON_VERSION) $(VENV_NAME) --seed
ifeq ($(MAKE_OS), Windows)
	PYTHON = $(VENV_NAME)\Scripts\python
	ACTIVATE = $(VENV_NAME)\Scripts\activate
else
	PYTHON = $(VENV_NAME)/bin/python
	ACTIVATE = source $(VENV_NAME)/bin/activate
endif

PIP = $(RUN_MODULE) pip

install: create-env install-project install-pre-commit

create-env:
	$(info MAKE: Initializing environment in .venv ...)
	$(CREATE_ENV_CMD)
	$(UV) pip install --upgrade "pip>=24"

install-project:
	$(info MAKE: Installing project ...)
	$(UV) sync

install-pre-commit:
	$(info MAKE: Installing pre-commit hooks...)
	$(UV) run pre-commit install

test:
	$(info MAKE: Running tests ...)
	$(UV) run pytest tests

pre-commit:
	$(info MAKE: Pre-commit hooks check over all files...)
	$(UV) run pre-commit run --all-files

build-wheels:
	$(UV) build . --out-dir $(BUILD_WHEEL_DIR)

install-wheels:
	$(UV) pip install $(BUILD_WHEEL_DIR)/*.whl

build-docker:
	docker build -t $(DOCKER_TAG) .

run-app:
	$(PYTHON) app/app.py

run-docker:
	docker run -p 8501:8501 $(DOCKER_TAG)

publish-wheels:
	$(UV) publish $(BUILD_WHEEL_DIR)/*