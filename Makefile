check:
	@python selftest.py
	@find . -name "*.pyc" -delete
