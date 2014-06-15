MODULE=authorsim


test:
	find $(MODULE) -name *.py -type f -print0 | xargs -0 python -m doctest
