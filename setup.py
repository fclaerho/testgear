from setuptools import setup

import testgear

setup(
	name = "testgear",
	author = "fclaerhout.fr",
	license = "MIT",
	version = "1.0.0",
	py_modules = ["testgear"],
	test_suite = "selftest",
	description = "Test Generation Framework",
	author_email = "contact@fclaerhout.fr")