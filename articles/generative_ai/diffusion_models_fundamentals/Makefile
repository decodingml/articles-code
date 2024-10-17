# Define the Python environment (use your virtual environment path if needed)
PYTHON := python3

# Install dependencies using poetry
.PHONY: setup
setup:
	@echo "Setting up the environment..."
	poetry install
	@echo "Environment setup complete."

# Run training
.PHONY: train
train:
	@echo "Starting training..."
	$(PYTHON) src/train.py
	@echo "Training complete."

# Run inference
.PHONY: inference
inference:
	@echo "Starting inference..."
	$(PYTHON) src/inference.py
	@echo "Inference complete."

# Clean up temporary files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ src/**/__pycache__ .mypy_cache
	@echo "Cleanup complete."
