.PHONY: all build tag push bash clean help

MKFILE_PATH  := $(abspath $(lastword $(MAKEFILE_LIST)))
THISDIR_PATH := $(patsubst %/,%,$(abspath $(dir $(MKFILE_PATH))))
PROJECT_PATH := $(patsubst %/,%,$(dir $(MKFILE_PATH)))
.DEFAULT_GOAL := help

#Default Optional Variables
NAME ?= slack-on-call
NAMESPACE ?= quay.io/3scale
RELEASE_VERSION ?= python-36-centos7 

VERSION := $(RELEASE_VERSION)
LOCAL_IMAGE := $(NAME):$(VERSION)
REMOTE_IMAGE := $(NAMESPACE)/$(LOCAL_IMAGE)

all: build tag push

build: ## Build docker image. Name will be LOCAL_IMAGE=$(NAME):$(VERSION). 
	docker build --file $(THISDIR_PATH)/Dockerfile -t $(LOCAL_IMAGE) $(PROJECT_PATH)

run: ## Run the docker in the local machine.
	docker run --rm -u 10000001 -t -P $(LOCAL_IMAGE)

tag: ## Tag IMAGE_NAME in the docker registry
	docker tag $(LOCAL_IMAGE) $(REMOTE_IMAGE)

push: ## Push to the docker registry
	docker push $(REMOTE_IMAGE)

bash: ## Start bash in the build IMAGE_NAME.
	docker run --rm -u 1001 --network host --name $(NAME) --entrypoint=/bin/bash -it $(LOCAL_IMAGE)

clean: ## Clean local environment
	docker rmi $(LOCAL_IMAGE)

# Check http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## Print this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

