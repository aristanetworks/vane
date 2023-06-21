#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for Vane
#
# useful targets:
#       make check -- syntax checking and manifest checks
#       make clean -- clean distutils
#       make dev -- build and run the dev container
#       make coverage_report -- code coverage report
#       make flake8 -- flake8 checks
#       make install -- install application
#       make pycodestyle -- pycodestyle checks
#       make pylint -- source code checks
#       make rpm -- build RPM package
#       make sdist -- build python source distribution
#       make systest -- runs the system tests
#       make tests -- run all of the tests
#       make unittest -- runs the unit tests
#
# Notes:
# 1) flake8 is a wrapper around pep8, pyflakes, and McCabe.
########################################################
# variable section

NAME = "vane"

PYTHON=python3
COVERAGE=coverage

VERSION := $(shell awk '/__version__/{print $$NF}' vane/__init__.py | sed "s/'//g")

RPMSPECDIR = $(TOPDIR)
RPMSPEC = $(RPMSPECDIR)/$(NAME).spec
CVPRPMSPEC = $(RPMSPECDIR)/$(NAME)_cvpinstall.spec
RPMRELEASE = 1

BASENAME = $(NAME)-$(VERSION)-$(RPMRELEASE)
DOCKER = docker
UID = $(shell id -u)
GID = $(shell id -g)
IMAGE_TAG = latest
SDIST = $(TMPDIR)/build/$(BASENAME)
DIR_NAME = $(NAME)
CONTAINER_NAME = vane
CONTAINER_TAG = $(IMAGE_TAG)
CONTAINER = $(CONTAINER_NAME):$(CONTAINER_TAG)
PROJECT_DIR = $(shell pwd)
DOCKER_DIR = "/project"
REPO = "registry.gitlab.aristanetworks.com/arista-eosplus/vane"

PEP8_IGNORE = E302,E203,E261,W503,C0209,E501
########################################################

# Removed 'check' target as we need to work out the MANEFEST.IN issues
all: clean pycodestyle flake8 pylint tests

.PHONY: check
check:
	check-manifest

.PHONY: clean
clean:
	@echo "Cleaning up distutils stuff"
	rm -rf MANIFEST build dist rpmbuild rpms
	rm -rf $(SDIST) $(TMPDIR)
	@echo "Cleaning up byte compiled python stuff"
	find . -type f -regex ".*\.py[co]$$" -delete
	find . -type d -name __pycache__ | xargs rm -fr
	@echo "Cleaning up generated test files"
	rm -fr tests/systests/fixtures/reports/*
	rm -rf mkdir tests/unittests/fixtures/reports/results

.PHONY: pycodestyle
pycodestyle:
	-pycodestyle -r --ignore=$(PEP8_IGNORE) vane/ tests/

.PHONY: flake8
flake8:
	flake8 --ignore=$(PEP8_IGNORE)  vane/ tests/

.PHONY: pylint
pylint:
	pylint vane/ tests/

.PHONY: sample_network_tests
sample_network_tests: 
	sudo openvpn --config ovpn_profiles/eosplus-act.ovpn --daemon
	ping 10.255.74.38 -c 5
	coverage run --source /project/vane -m vane.vane_cli --definitions_file sample_network_tests/definitions.yaml --duts_file sample_network_tests/duts.yaml
	coverage report -m /project/vane/*.py

.PHONY: unittest
unittest:
	mkdir -p tests/unittests/fixtures/reports/results
	pytest --cov-report term-missing --cov=/project/vane tests/unittests

.PHONY: coverage_report
coverage_report:
	$(COVERAGE) report -m

.PHONY: tests
tests: unittest systest

.PHONY: install
install:
	$(PYTHON) setup.py install

.PHONY: exec
exec:
	docker exec -it $(CONTAINER_NAME) /bin/bash

.PHONY: format
format:
	docker exec -it $(CONTAINER_NAME) bash -c "black -l 80 /project/vane/bin/*py"

.PHONY: hints
hints:
	docker exec -it $(CONTAINER_NAME) bash -c "mypy /project/vane/bin/*py"

.PHONY: dev
docker_build:
	docker build -t $(CONTAINER) . --build-arg UID=$(UID) --build-arg GID=$(GID)

docker_stop:
	- docker stop $(CONTAINER_NAME)

docker_run:
	docker run --cap-add=NET_ADMIN --device /dev/net/tun:/dev/net/tun -t -d --rm --name $(CONTAINER_NAME) -v $(PROJECT_DIR):$(DOCKER_DIR) $(CONTAINER)

dev: docker_stop docker_build docker_run exec
