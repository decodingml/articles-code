RED := \033[0;31m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring

ENV_NAME := "py39upstash"
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "-------------------"
	@echo "$(YELLOW)list$(RESET)            : List available targets with descriptions"
	@echo ""
	@echo "== Env =="
	@echo "$(RED)install$(RESET)			: Installs a new py39 env and sets-up poetry packages"
	@echo ""
	@echo "== Test =="
	@echo "$(YELLOW)test$(RESET)			: Runs unit-tests."
	@echo ""
	@echo "== Production =="
	@echo "$(GREEN)run_producers$(RESET)    : Starts the Kafka Producers"
	@echo "$(GREEN)run_pipeline$(RESET)     : Starts the bytewax pipeline"
	@echo ""
	@echo ""

list: help


install:
	@echo "$(GREEN) [CONDA] Creating [$(ENV_NAME)] python env $(RESET)"
	conda create --name $(ENV_NAME) python=3.9 -y
	@echo "Activating the environment..."
	@bash -c "source $$(conda info --base)/etc/profile.d/conda.sh && conda activate $(ENV_NAME) \
			&& pip install poetry \
			poetry env use $(which python)"
	@echo "Installing Packages"
	@echo "Changing to pyproject.toml location..."
	@bash -c "cd upstash_ingest && poetry install"

run_producers:
	@echo "$(GREEN) [RUNNING] Producers $(RESET)"
	@bash -c "poetry run python upstash_ingest/upstash_ingest/producer.py"

run_bytewax_pipeline:
	@echo "$(GREEN) [RUNNING] Bytewax Pipeline $(RESET)"
	@bash -c "poetry run python -m bytewax.run upstash_ingest/upstash_ingest/start:flow"