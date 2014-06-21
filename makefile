MODULE=gutenberg

SRC_DIR=$(MODULE)


test:
	nosetests --verbose --with-doctest

clean:
	find $(SRC_DIR) -name *.pyc -type f -delete

install:
	pip install -r requirements.txt

lint:
	pylint $(SRC_DIR) --output-format=colorized --reports=no --rcfile=.pylintrc || true
