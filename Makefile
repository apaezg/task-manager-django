SHELL = /bin/bash
.DEFAULT_GOAL := help

PROJECT ?= simple_tasks

DC=docker-compose -p ${PROJECT} -f docker-compose.yml

REQUIREMENTS_FILE ?= "requirements.txt"

#COLORS
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
# A category can be added with @category
HELP_FUN = \
    %help; \
    while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
    print "usage: make [target]\n\n"; \
    for (sort keys %help) { \
    print "${WHITE}$$_:${RESET}\n"; \
    for (@{$$help{$$_}}) { \
    $$sep = " " x (32 - length $$_->[0]); \
    print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
    }; \
    print "\n"; }

.PHONY: help
help: ##@other Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

.PHONY: build
build: ##@main Build containers. Needed only after changes in requierements.
build:
	${DC} build web

.PHONY: server
server: ##@main Run application server in port 8000
server:
	${DC} up -d web

.PHONY: shell
shell: ##@main Start a bash shell in a standalone container.
shell:
	${DC} run --rm application /bin/bash

.PHONY: attach
attach: ##@main Attach to running server for debugging. Ctrl+D to detach.
attach: instance  ?= 1
attach:
	docker attach --detach-keys="ctrl-d" ${PROJECT}_web_${instance}

.PHONY: clean
clean: ##@main Destroy containers for current project. Will keep database volume.
clean:
	${DC} down --remove-orphans

.PHONY: migrate-db
migrate-db: ##@main Apply migrations
migrate-db:
	${DC} run --rm application "python manage.py migrate --noinput"

.PHONY: reset-db
reset-db: ##@main Apply migrations back to intial point and then forward, populating initial data
reset-db:
	@${DC} stop db
	@docker volume rm ${PROJECT}_postgre-volume || true
	${DC} up -d db; \
	${DC} run --rm application "python manage.py migrate --noinput"; \
	${DC} run --rm application "python manage.py loaddata initial_data.yaml"

.PHONY: tests
tests: ##@main Run automatic tests
tests:
	${DC} up -d application
	${DC} run --rm application "coverage run --source='.' manage.py test; coverage report"
