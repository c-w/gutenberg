MODULE=gutenberg

SRC_DIR=$(MODULE)


test:
	find $(SRC_DIR) -name *.py -type f -print0 | xargs -0 python -m doctest

clean:
	find $(SRC_DIR) -name *.pyc -type f -delete

install-requirements:
	pip install -r requirements.txt

pylint:
	pylint $(SRC_DIR) --output-format=colorized --reports=no --const-rgx='[A-Za-z_][A-Za-z0-9_]{2,30}$$' || true
