# Makefile for Instagram Crawler Application

# Variables
PYTHON = python3
POETRY = poetry
DOCKER_COMPOSE = docker-compose

# Phony targets
.PHONY: all setup run clean stop

# Default target
all: setup run

# Setup the environment
setup:
	@echo "Setting up the environment..."
	$(POETRY) install
	@echo "Environment setup complete."

# Run the MongoDB container
start-db:
	@echo "Starting MongoDB container..."
	$(DOCKER_COMPOSE) up -d mongodb
	@echo "MongoDB container started."

# Run the main application
run: start-db
	@echo "Running the Instagram Crawler application..."
	$(POETRY) run python -m src.main
	@echo "Application run complete."

# Stop the MongoDB container
stop:
	@echo "Stopping MongoDB container..."
	$(DOCKER_COMPOSE) down
	@echo "MongoDB container stopped."

# Clean up
clean: stop
	@echo "Cleaning up..."
	rm -f *.xlsx *.csv
	@echo "Cleanup complete."

# Help target
help:
	@echo "Available targets:"
	@echo "  setup     - Install required Python packages using Poetry"
	@echo "  start-db  - Start the MongoDB container"
	@echo "  run       - Run the Instagram Crawler application"
	@echo "  stop      - Stop the MongoDB container"
	@echo "  clean     - Stop containers and remove generated Excel/CSV files"
	@echo "  all       - Setup environment and run the application (default)"
	@echo "  help      - Display this help message"