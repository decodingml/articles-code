.SILENT:

RED:=\033[0;31m
GREEN:=\033[0;32m
BLUE:=\033[0;34m
NC:=\033[0m

# Set the default shell to bash
SHELL := /bin/bash

help:
	@echo -e "$(BLUE)Usage: make [target]$(NC)"
	@echo -e "$(BLUE)Targets:$(NC)"
	@echo -e "$(BLUE)  start_tis$(NC) - Start TIS"
	@echo -e "$(BLUE)  stop_tis$(NC) - Stop TIS"
	@echo -e "$(BLUE)  install$(NC) - Install dependencies"
	@echo -e "$(BLUE)  install_nvidia_container_runtime$(NC) - Install NVIDIA Container Runtime"
	

install_nvidia_container_runtime:
	@echo -e "$(GREEN)Installing NVIDIA Container Runtime...$(NC)"
	@curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
	&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
	sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
	sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
	@sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
	@sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
	sudo systemctl restart docker
	@echo -e "$(GREEN)NVIDIA Container Runtime installed$(NC)"

fix_env:
	@echo -e "$(GREEN)Setting up .env ...$(NC)"
	@cp .env.default .env
	@echo -e "$(GREEN).env setup$(NC)"
	
install:
	@echo -e "$(GREEN)Installing dependencies...$(NC)"
	@pip install poetry
	@poetry install
	@echo -e "$(GREEN)Dependencies installed$(NC)"

start_tis:
	@echo -e "$(GREEN)Starting TIS...$(NC)"
	@docker rm sample-tis-22.04 -f
	@docker compose -f docker-compose.triton.yaml up -d
	@echo -e "$(GREEN)TIS started$(NC)"

stop_tis:
	@echo -e "$(RED)Stopping TIS...$(NC)"
	@docker compose -f docker-compose.triton.yaml down
	@echo -e "$(RED)TIS stopped$(NC)"
