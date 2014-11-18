SETUP=setup.py

MODULE=$(shell sed -n "s/.*name='\(.*\)',/\1/p" "$(SETUP)" | tr '[:upper:]' '[:lower:]')
AUTHOR=$(shell sed -n "s/.*author='\(.*\)',/\1/p" "$(SETUP)")
VERSION=$(shell sed -n "s/.*version='\(.*\)',/\1/p" "$(SETUP)")

SRC_DIR=$(MODULE)
DOC_DIR=docs
DIST_DIR=dist

VENV_DIR=virtualenv
VENV_ACTIVATE=$(VENV_DIR)/bin/activate

MANIFEST=MANIFEST.in
MANIFEST_INCLUDE=*.txt makefile
MANIFEST_RECURSIVE_INCLUDE=$(DOC_DIR) *.txt

PYLINT_RC=.pylintrc
NOSE_RC=.noserc


.PHONY: virtualenv test publish clean docs lint setup_docs
.PHONY: increase-major-version increase-minor-version increase-micro-version
.PHONY: release-major-version release-minor-version release-micro-version


virtualenv: $(VENV_ACTIVATE)
$(VENV_ACTIVATE): requirements.txt
	test -d "$(VENV_DIR)" || virtualenv "$(VENV_DIR)"
	. "$(VENV_ACTIVATE)"; pip install -U -r requirements.txt
	touch "$(VENV_ACTIVATE)"

test: virtualenv
	. "$(VENV_ACTIVATE)"; \
	nosetests --config="$(NOSE_RC)"

$(MANIFEST):
	echo "include $(MANIFEST_INCLUDE)" > $(MANIFEST)
	echo "recursive-include $(MANIFEST_RECURSIVE_INCLUDE)" >> $(MANIFEST)

publish: $(MANIFEST) docs
	. "$(VENV_ACTIVATE)"; \
	python $(SETUP) sdist --dist-dir="$(DIST_DIR)" upload

increase-major-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"".($$1+1).".0.0"/e' "$(SETUP)"

increase-minor-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"$$1.".($$2+1).".0"/e' "$(SETUP)"

increase-micro-version:
	perl -i -p -e 's/(\d+).(\d+).(\d+)/"$$1.$$2.".($$3+1)/e' "$(SETUP)"

release-major-version: increase-major-version publish
	@echo "Now at version $(VERSION)"

release-minor-version: increase-minor-version publish
	@echo "Now at version $(VERSION)"

release-micro-version: increase-micro-version publish
	@echo "Now at version $(VERSION)"

clean:
	find "$(SRC_DIR)" -name *.pyc -type f -delete
	rm -f MANIFEST*
	rm -rf "$(DIST_DIR)"
	find "$(DOC_DIR)" -not \( -name conf.py -or -name $(DOC_DIR) \) -delete

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
		--rcfile="$(PYLINT_RC)" \
	|| true
