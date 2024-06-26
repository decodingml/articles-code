AWS_CURRENT_REGION_ID := $(shell aws configure get region)
AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


local-test-crawler: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
		-d '{"link": "https://www.instagram.com/mcdonalds/"}'

local-test-scheduler: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'


push:
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com/profiles
	docker buildx build \
		--platform linux/amd64 \
		-t $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com/profiles:latest \
		--push .
