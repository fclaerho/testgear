TestGear
========

Test Generation Framework.

* * *

Usage
-----

  1. Implement the testgear.Environment interface to control the test envionment
  2. Implement the testgear.Entity interface for all your data model entities
  3. Call testgear.test() on the environment and entities
  4. Enjoy

Both Environment and Entity support profiles to vary the created instances.
Testgear uses the native python unittest framework to build the testcases.

Installation
------------

Copy testgear.py in your project vendor/ directory.