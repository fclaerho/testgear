	  ______          __  ______               
	 /_  __/__  _____/ /_/ ____/__  ____ ______
	  / / / _ \/ ___/ __/ / __/ _ \/ __ `/ ___/
	 / / /  __(__  ) /_/ /_/ /  __/ /_/ / /    
	/_/  \___/____/\__/\____/\___/\__,_/_/     

TestGear is a Test Generation Framework for Python:
it's packed with the usual test patterns so that you just have to interface your
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
  4. Implement the `testgear.Entity` interface for all your data model entities
  5. Call `testgear.test`(%environment%, (%entity%…)) to run the tests

To retrieve the test suite instead of running the tests, call `testgear.generate_testsuite`(%environment%, (%entity%…)).

To make the test suite accessible to unittest from `loadTestsFromModule`():

	def load_tests(loader, standard_tests, pattern):
		return testgear.generate_testsuite(%environment%, (%entity%…))

INTERFACE SPECIFICATION
-----------------------

  * Exception `NoSuchResource`
  * Exception `ResourceExists`
  * Exception `ValidationError`
  * Class `Environment`:
    * List `profiles` = ("default",);
      Add any profile you see fit.
      The profile will be passed as argument at the entity creation.
    * Abstract `setUp`(profile);
      Setup a new test environment, it may be populated with anything but not with the profiles of your entities
    * Abstract `tearDown`();
      Teardown the test environment
  * Class `Entity`:
    * List `profiles` = ("default",);
      Add any profile you see fit.
      The profile will be passed as argument at the entity creation.
    * List `tamperings` = ();
      Add any tampering you see fit.
      The tampering will be passed as argument at the entity creation.
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
