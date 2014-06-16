MODULE=authorsim

SRC_DIR=$(MODULE)


test:
	find $(SRC_DIR) -name *.py -type f -print0 | xargs -0 python -m doctest

clean:
	find $(SRC_DIR) -name *.pyc -type f -delete

install-requirements:
	pip install -r requirements.txt
