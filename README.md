	 _____         _      _    _____                 
	|_   _|       | |  /\| |/\|  __ \                
	  | | ___  ___| |_ \ ` ' /| |  \/ ___  __ _ _ __ 
	  | |/ _ \/ __| __|_     _| | __ / _ \/ _` | '__|
	  | |  __/\__ \ |_ / , . \| |_\ \  __/ (_| | |   
	  \_/\___||___/\__|\/|_|\/ \____/\___|\__,_|_|   

A **Test Generation Framework for Python**
packed with the usual test patterns so that you just have to interface your
code with the framework to get an off-the-shelf test suite instead of recoding the wheel every time.

Available Patterns:
  * CRUD
  * _(to be completed)_

USAGE
-----

  1. Checkout the framework in your project `vendor/` directory

		# if you're using git:
		$ git submodule add http://www.github.com/fclaerho/testgear.git
		# otherwise just checkout the code

  2. `import testgear`
  3. Implement the `testgear.Environment` interface to control the test environment
  4. Implement the `testgear.Resources` interface for all your resources
  5. Call `testgear.test`(%environment%, {key:%resources%,…}) to run the tests
     The number of tests generated will vary depending on the number of profiles and tampering configurations you've configured.

To retrieve the test suite instead of running the tests, call `testgear.generate_testsuite`(%environment%, (%resources%…)).

To let unittest autoload the suite, implement the `load_tests` protocol:

	def load_tests(loader, standard_tests, pattern):
		return testgear.generate_testsuite(%environment%, (%resources%…))

See https://docs.python.org/2/library/unittest.html#load-tests-protocol for details.

INTERFACE SPECIFICATION
-----------------------

  * Class `Environment`:
    * List `profiles` = ("default",);
      Add any profile you see fit.
      The profile will be passed as argument at the resource creation.
    * Abstract `setUp`(profile);
      Setup a new test environment, it may be populated with anything but not with the profiles of your resources
    * Abstract `tearDown`();
      Teardown the test environment
  * Class `Resources`:
    * Dict `resources` pointing to the resources argument of `.test()` and allowing to handle resources dependencies.
    * List `profiles` = ("default",);
      Add any profile you see fit.
      The profile will be passed as argument at the resource creation.
    * List `tamperings` = ();
      Add any tampering you see fit.
      The tampering will be passed as argument at the resource creation.
    * Abstract `get_key`(profile);
      Return the same key than `create`() on that profile if supported, `None` otherwise
    * Integer `creation_policy` = 0;
      * 0: `create`() cannot be called twice with the same profile
      * 1: `create`() is idempotent
      * 2: multiple instances of the same profile can be created
    * Abstract `create`(profile, tampering = `None`);
      Create the instance, return a key on success, raise `ResourceExists` or `ValidationError` on error;
      The tampering parameter indicates how to corrupt the initial profile;
      If the tampering parameter is not `None`, a `ValidationError` is expected.
    * Abstract `exists`(key);
      Return `True` if the instance exists, `False` otherwise
    * Abstract `delete`(key);
      Delete the instance, return nothing on success, raise `NoSuchResource` if the instance does not exist
    * Abstract `update`(key, profile);
      Update the instance to a new profile, return nothing on success, raise `NoSuchResource` if the instance does not exist

**BEWARE**
The testgear exceptions on `create()`, `delete()` and `update()` should simply be re-mapped from the underlying exceptions.
Do not add any check into your `Resources` implementations!
