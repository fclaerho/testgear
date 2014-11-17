# copyright (c) 2014 fclaerhout.fr, released under the MIT license.

"""
Test Generation Framework.

Usage:
  1. Implement the testgear.Environment interface to control the test envionment
  2. Implement the testgear.Entity interface for all your data model entities
  3. Call testgear.test() on the environment and entities
  4. Enjoy

Both Environment and Entity support profiles to vary the created instances.
Testgear uses the native python unittest framework to build the testcases.
"""

__version__ = "0.1"

import unittest, abc

##############
# interfaces #
##############

class Environment(object):

	__metaclass__ = abc.ABCMeta

	profiles = ("default",)

	@abc.abstractmethod
	def setUp(self, profile):
		"create a test environment not containing any of the entity profiles below"
		pass

	@abc.abstractmethod
	def tearDown(self): pass

class Entity(object):

	__metaclass__ = abc.ABCMeta

	profiles = ("default",)

	def get_key(self, profile):
		"""
		Return the same key than create() on that profile if supported, None otherwise.
		Examples:
		- Not supported: (RDBMS, record id)
		- Supported: (filesystme, filename)
		"""
		return None

	# 0: create() cannot be called twice with the same profile
	# 1: create() is idempotent
	# 2: multiple instances of the same profile can be created
	creation_policy = 0

	@abc.abstractmethod
	def create(self, profile):
		"return the instance key (aka. record id for a rdbms)"
		pass

	@abc.abstractmethod
	def exists(self, key): pass

	@abc.abstractmethod
	def delete(self, key): pass

	@abc.abstractmethod
	def update(self, key, profile): pass

######################
# testcase templates #
######################

class _1Env_1Entity_1Profile_TestCase(object):

	def setUp(self):
		self.environment.setUp(self.environment_profile)

	def tearDown(self):
		self.environment.tearDown()

	def test_test_delete(self):
		"the deletion of an inexisting instance fails"
		key = self.entity.get_key(self.entity_profile)
		if key is not None:
			self.assertFalse(self.entity.exists(key))
			self.assertRaises(Exception, self.entity.delete, key)

	def test_create_test_delete(self):
		"a created instance exists and can be deleted"
		key = self.entity.create(self.entity_profile)
		self.assertTrue(self.entity.exists(key), "%s: not created" % key)
		self.entity.delete(key)
		self.assertFalse(self.entity.exists(key), "%s: not deleted" % key)

	def test_creation_policy(self):
		key1 = self.entity.create(self.entity_profile)
		if self.entity.creation_policy == 0:
			self.assertRaises(Exception, self.entity.create, self.entity_profile)
		elif self.entity.creation_policy == 1:
			key2 = self.entity.create(self.entity_profile)
			self.assertEqual(key1, key2)
		elif self.entity.creation_policy == 2:
			key2 = self.entity.create(self.entity_profile)
			self.assertNotEqual(key1, key2)
		else:
			raise Exception("%s: unsupported creation policy" % self.creation_policy)

	def test_no_double_delete(self):
		"a same instance cannot be deleted twice"
		key = self.entity.create(self.entity_profile)
		self.entity.delete(key)
		self.assertRaises(Exception, self.entity.delete, key)

class _1Entity_NProfiles_TestCase(object):

	def test_create_many_delete_many(self):
		if self.entity.creation_policy in (0, 1):
			keys = tuple(self.entity.create(profile) for profile in self.entity.profiles)
		else:
			keys = tuple(self.entity.create(profile) for profile in self.entity.profiles * 1000)
		for key in keys:
			self.entity.delete(key)

################################
# concrete testcases generator #
################################

def generate_testsuite(environment, entities):
	testsuite = unittest.TestSuite()
	for environment_profile in environment.profiles:
		for entity in entities:
			# _1Env_1Entity_1Profile_TestCase
			for entity_profile in entity.profiles:
				name = "Test_%s%s_in_%sEnv" % (
					entity_profile.title(),
					type(entity).__name__,
					environment_profile.title())
				cls = type(name, (_1Env_1Entity_1Profile_TestCase, unittest.TestCase), {
					"environment_profile": environment_profile,
					"environment": environment,
					"entity_profile": entity_profile,
					"entity": entity,
				})
				testsuite.addTest(unittest.makeSuite(cls))
			# _1Entity_NProfiles_TestCase
			cls = type(name, (_1Entity_NProfiles_TestCase, unittest.TestCase), {
				"environment_profile": environment_profile,
				"environment": environment,
				"entity": entity,
			})
			testsuite.addTest(unittest.makeSuite(cls))
	return testsuite

def test(environment, entities):
	testsuite = generate_testsuite(environment, entities)
	unittest.TextTestRunner(verbosity = 2).run(testsuite)

############
# selftest #
############

if __name__ == "__main__":

	class FakeEnvironment(Environment):

		profiles = ("foo", "bar", "baz")

		def setUp(self, profile): pass

		def tearDown(self): pass

	class FakeEntity(Entity):

		profiles = ("foo", "bar", "baz")

		def __init__(self):
			self.created = {}

		creation_policy = 1

		def create(self, profile):
			key = profile
			self.created[key] = True
			return key

		def exists(self, key):
			return key in self.created and self.created[key]

		def delete(self, key):
			assert key in self.created and self.created[key], "no such instance"
			self.created[key] = False

		def update(self, key, profile): pass

	test(
		environment = FakeEnvironment(),
		entities = (FakeEntity(),))
