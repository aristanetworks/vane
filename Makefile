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
#       make pylint -- source code checks
#       make rpm-cvp -- build RPM package for CVP extension
#       make sdist-cvp -- build python source distribution for CVP extension
#       make sample_network_tests -- runs the sample network tests
#       make unittest -- runs the unit tests
#
# Notes:
# 1) flake8 is a wrapper around pep8, pyflakes, and McCabe.
########################################################

# variable section
TOPDIR = $(shell pwd)
TMPDIR=./tmp
MKDIR_P = mkdir -p

NAME = vane
NAME_CVP = $(NAME)-cvp

PYTHON=python3
COVERAGE=coverage

VERSION := $(shell awk '/^version =/{print $$NF}' pyproject.toml | sed "s/\"//g")

CONTAINER_ENGINE = docker
DOCKER = docker
IMAGE_TAG = latest
CONTAINER_NAME = $(NAME)
CONTAINER_NAME_CVP = $(NAME_CVP)
CONTAINER_TAG = $(IMAGE_TAG)
CONTAINER_FULL_NAME = $(CONTAINER_NAME):$(CONTAINER_TAG)
CONTAINER_CVP = $(CONTAINER_NAME_CVP):$(CONTAINER_TAG)

UID = $(shell id -u)
GID = $(shell id -g)

# CVP RPM build vars
RPMRELEASE = 1
BASENAME_CVP = $(NAME_CVP)-$(VERSION)-$(RPMRELEASE)
RPMSPECDIR = $(TOPDIR)
CVPRPMSPEC = $(RPMSPECDIR)/$(NAME_CVP)_cvpinstall.spec
SDIST = $(TMPDIR)/build/$(BASENAME_CVP)
PYTHON3_SITELIB = $(shell python3 -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')

PROJECT_DIR = $(shell pwd)
CONTAINER_DIR = "/project"

PEP8_IGNORE = E302,E203,E261,W503,C0209,E501

########################################################

# Removed 'check' target as we need to work out the MANEFEST.IN issues
all: clean flake8 pylint unittest

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
	rm -rf mkdir tests/unittests/fixtures/reports/results

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

# ---- Container related targets --------------------------------------------------

.PHONY: format
format:
	${CONTAINER_ENGINE} run --rm --name $(CONTAINER_NAME) -v $(PROJECT_DIR):$(CONTAINER_DIR) $(CONTAINER_FULL_NAME) bash -c "poetry run black -l 100 /project/vane/*py"

.PHONY: container
# Builds the container
container:
	${CONTAINER_ENGINE} build -t $(CONTAINER_FULL_NAME) . --build-arg UID=$(UID) --build-arg GID=$(GID)

.PHONY: run
# Runs the container
run:
	${CONTAINER_ENGINE} run --cap-add=NET_ADMIN --device /dev/net/tun:/dev/net/tun -it --rm --name $(CONTAINER_NAME) -v $(PROJECT_DIR):$(CONTAINER_DIR) $(CONTAINER_FULL_NAME)

# ---- CVP RPM related targets --------------------------------------------------

docker_build_cvp:
	${DOCKER} build -f Dockerfile.CVP -t vane-cvp . --network=host
	${DOCKER} save $(CONTAINER_NAME_CVP) | gzip > $(NAME_CVP).tar.gz

docker_stop_cvp:
	- ${DOCKER} stop $(CONTAINER_NAME_CVP)

cvp: docker_stop_cvp docker_build_cvp

rpm-cvp: rpmcommon-cvp rpm-build

rpmcommon-cvp: sdist-cvp
	@sed -e 's#^Version:.*#Version: $(VERSION)#' \
		 -e 's#^Release:.*#Release: $(RPMRELEASE)#' $(CVPRPMSPEC) \
		 >rpmbuild/$(NAME_CVP).spec

sdist-cvp: clean
	$(MKDIR_P) rpmbuild
	$(MKDIR_P) $(SDIST)
	cp -r conf/* $(SDIST)
	$(MKDIR_P) $(SDIST)/cvpi/docker
	mv vane-cvp.tar.gz $(SDIST)/cvpi/docker
	tar -czf $(BASENAME_CVP).tar.gz -C $(TMPDIR)/build $(BASENAME_CVP)/
	$(MKDIR_P) dist
	mv $(BASENAME_CVP).tar.gz dist

rpm-build:
	@rpmbuild --define "_topdir %(pwd)/rpmbuild" \
	--target noarch \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %(pwd)/dist/" \
	--define "_rpmdir %(pwd)/rpms" \
	--define "_srcrpmdir %{_rpmdir}" \
	--define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" \
	--define "python3_sitelib $(PYTHON3_SITELIB)" \
	--define "__python python3" \
	-bb rpmbuild/$(NAME_CVP).spec
	@rm -f rpmbuild/$(NAME_CVP).spec
