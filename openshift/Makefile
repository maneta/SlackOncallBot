.PHONY: all imagestream deploy
.DEFAULT_GOAL := help

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
THISDIR_PATH := $(patsubst %/,%,$(abspath $(dir $(MKFILE_PATH))))

all: imagestream buildconfig deploy route

imagestream: ## Create the Imagestreams 
	oc create -f $(THISDIR_PATH)/01-slack-on-call-imagestream.yml

deploy: ## Create the BuildConfig. Parameters: SLACK_VERIFICATION_TOKEN, SLACK_TEAM_ID, ESCALATION_POLICY_ID, API_TOKEN
	oc new-app -f $(THISDIR_PATH)/02-deployment-template.yml \
		-p SLACK_VERIFICATION_TOKEN=${SLACK_VERIFICATION_TOKEN} \
		-p SLACK_TEAM_ID=${SLACK_TEAM_ID} \
		-p ESCALATION_POLICY_ID=${ESCALATION_POLICY_ID} \
		-p API_TOKEN=${API_TOKEN}

help: ## Print this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
