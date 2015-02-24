from setuptools import setup

import testgear

setup(
    name = "testgear",
    version = testgear.__version__,
    py_modules = ["testgear.py"],
    test_suite = "selftest",
    description = testgear.__doc__.splitlines()[0],
    tests_require = None,
    install_requires = None)