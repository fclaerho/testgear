from setuptools import setup

import testgear

setup(
	name = "testgear",
	version = testgear.__version__,
	license = "MIT",
	py_modules = ["testgear"],
	test_suite = "selftest",
	description = testgear.__doc__.splitlines()[0],
	tests_require = None,
	install_requires = None)