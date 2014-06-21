MODULE=gutenberg

SRC_DIR=$(MODULE)
VENV_DIR=virtualenv

VENV_ACTIVATE=$(VENV_DIR)/bin/activate


virtualenv: $(VENV_ACTIVATE)
$(VENV_ACTIVATE): requirements.txt
	test -d $(VENV_DIR) || virtualenv $(VENV_DIR)
	. $(VENV_ACTIVATE); pip install -U -r requirements.txt
	touch $(VENV_ACTIVATE)

test: virtualenv
	. $(VENV_ACTIVATE); nosetests --verbose --with-doctest

clean:
	find $(SRC_DIR) -name *.pyc -type f -delete

lint: virtualenv
	. $(VENV_ACTIVATE); pylint $(SRC_DIR) --output-format=colorized --reports=no --rcfile=.pylintrc || true
