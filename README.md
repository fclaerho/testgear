TestGear
========

Intro
-----

TestGear is a Test Generation Framework:
it's packed with usual test patterns so that you just have to interface your
code with the framework to get an off-the-shelf test suite instead of recoding the wheel every time.

Available Patterns:
  * CRUD (both valid and invalid cases)
  * (to be completed)

Usage
-----

  1. Checkout the framework in your project vendor/ directory

		# if you're using git:
		$ git submodule add http://www.github.com/fclaerho/testgear.git
		# otherwise just checkout the code

  2. Implement the `testgear.Environment` interface to control the test environment
  3. Implement the `testgear.Entity` interface for all your data model entities
  4. Call `testgear.test`() on the environment and entities

Interfaces
----------

  * `NoSuchResource` -- Exception
  * `CreationFailure` -- Exception
  * class `Environment`:
    * `profiles` = ("default",) -- add any profile you see fit.
    * abstract `setUp`(profile)
      -- setup a new test environment, it may be populated with anything but not with the profiles of your entities
    * abstract `tearDown`() -- teardown the test environment
  * class `Entity`:
    * `profiles` = ("default",) -- add any profile you see fit.
    * `tamperings` = () -- add any tampering you see fit
    * abstract `create`(profile, tampering = None)
      -- create the instance, return a key on success, raise CreationFailure on error;
      the tampering parameter indicates how to corrupt the initial profile and if it's set, a CreationFailure is expected.
    * abstract `exists`(key) -- return True if the instance exists, False otherwise
    * abstract `delete`(key)
      -- delete the instance, return nothing on success, raise NoSuchResource if the instance does not exist
    * abstract `update`(key, profile)
      -- update the instance to a new profile, return nothing on success, raise NoSuchResource if the instance does not exist

