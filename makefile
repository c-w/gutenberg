MODULE=$(shell sed -n "s@^.*name='\([^']\+\)'.*@\L\1@p" setup.py)
AUTHOR=$(shell sed -n "s@^.*author='\([^']\+\)'.*@\1@p" setup.py)
VERSION=$(shell sed -n "s@^.*version='\([^']\+\)'.*@\1@p" setup.py)

SRC_DIR=$(MODULE)
DOC_DIR=docs
DIST_DIR=dist
VENV_DIR=virtualenv

VENV_ACTIVATE=$(VENV_DIR)/bin/activate

MANIFEST=MANIFEST.in
MANIFEST_INCLUDE=*.txt makefile
MANIFEST_RECURSIVE_INCLUDE=$(DOC_DIR) *.txt

.PHONY: test dist clean docs lint


virtualenv: $(VENV_ACTIVATE)
$(VENV_ACTIVATE): requirements.txt
	test -d "$(VENV_DIR)" || virtualenv "$(VENV_DIR)"
	. "$(VENV_ACTIVATE)"; pip install -U -r requirements.txt
	touch "$(VENV_ACTIVATE)"

test: virtualenv
	. "$(VENV_ACTIVATE)"; \
	nosetests --verbose --with-doctest

$(MANIFEST):
	echo "include $(MANIFEST_INCLUDE)" > $(MANIFEST)
	echo "recursive-include $(MANIFEST_RECURSIVE_INCLUDE)" >> $(MANIFEST)

dist: $(MANIFEST) docs
	. "$(VENV_ACTIVATE)"; \
	python setup.py sdist --dist-dir="$(DIST_DIR)"

increase-major-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"".($$1+1).".0.0"/e' setup.py

increase-minor-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"$$1.".($$2+1).".0"/e' setup.py

increase-micro-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"$$1.$$2.".($$3+1)/e' setup.py

release-major: increase-major-version dist
	@echo "Now at version $(VERSION)"

release-minor: increase-minor-version dist
	@echo "Now at version $(VERSION)"

release-micro: increase-micro-version dist
	@echo "Now at version $(VERSION)"

clean:
	find "$(SRC_DIR)" -name *.pyc -type f -delete
	rm -f MANIFEST*
	rm -rf "$(DIST_DIR)"

setup_docs: virtualenv
	. "$(VENV_ACTIVATE)"; \
	sphinx-apidoc \
		--output-dir="$(DOC_DIR)" \
		--full \
		--separate \
		--doc-author="$(AUTHOR)" \
		--doc-version="$(VERSION)" \
		"$(SRC_DIR)"

docs: setup_docs
	. "$(VENV_ACTIVATE)"; \
	cd "$(DOC_DIR)" && make html && cd -

lint: virtualenv
	. "$(VENV_ACTIVATE)"; \
	pylint "$(SRC_DIR)" \
		--output-format=colorized \
		--reports=no \
		--rcfile=.pylintrc \
	|| true
