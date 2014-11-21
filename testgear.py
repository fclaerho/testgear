# copyright (c) 2014 fclaerhout.fr, released under the MIT license.

"Test Generation Framework -- see bundled README.md for usage instructions"

__version__ = "0.2"

import unittest, abc

##############
# exceptions #
##############

class ResourceExists(Exception): pass

class NoSuchResource(Exception): pass

class ValidationError(Exception): pass

##############
# interfaces #
##############

class Environment(object):

	__metaclass__ = abc.ABCMeta

	profiles = ("default",)

	@abc.abstractmethod
	def setUp(self, profile): pass

	@abc.abstractmethod
	def tearDown(self): pass

class Entity(object):

	__metaclass__ = abc.ABCMeta

	profiles = ("default",)

	tamperings = ()

	@abc.abstractmethod
	def get_key(self, profile): pass

	creation_policy = 0

	@abc.abstractmethod
	def create(self, profile, tampering = None): pass

	@abc.abstractmethod
	def exists(self, key): pass

	@abc.abstractmethod
	def delete(self, key): pass

	@abc.abstractmethod
	def update(self, key, profile): pass

######################
# testcase templates #
######################

class _Common(object):

	def setUp(self):
		self.environment.setUp(self.environment_profile)

	def tearDown(self):
		self.environment.tearDown()

class _ProfiledEntity_In_ProfiledEnvironment_TestCase(_Common):

	def test_test_delete(self):
		"the deletion of an inexisting instance fails"
		key = self.entity.get_key(self.entity_profile)
		if key is not None:
			self.assertFalse(self.entity.exists(key))
			self.assertRaises(NoSuchResource, self.entity.delete, key)

	def test_create_test_delete(self):
		"a created instance exists and can be deleted"
		key = self.entity.create(self.entity_profile)
		self.assertTrue(self.entity.exists(key), "%s: not created" % key)
		self.entity.delete(key)
		self.assertFalse(self.entity.exists(key), "%s: not deleted" % key)

	def test_creation_policy(self):
		"creating twice the same instance...(result depends on creation policy)"
		key1 = self.entity.create(self.entity_profile)
		if self.entity.creation_policy == 0:
			self.assertRaises(ResourceExists, self.entity.create, self.entity_profile)
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
		self.assertRaises(NoSuchResource, self.entity.delete, key)

	def test_invalid_input_on_creation(self):
		"creation with an invalid input fails"
		for tampering in self.entity.tamperings:
			self.assertRaises(
				ValidationError,
				self.entity.create,
				profile = self.entity_profile,
				tampering = tampering)

class _Entity_In_ProfiledEnvironment_TestCase(_Common):

	def _create_many(self):
		"create many instances, return keys"
		if self.entity.creation_policy in (0, 1):
			return tuple(self.entity.create(profile) for profile in self.entity.profiles)
		else:
			return tuple(self.entity.create(profile) for profile in self.entity.profiles * 1000)

	def test_create_many_delete_many_fifo(self):
		keys = self._create_many()
		for key in keys:
			self.entity.delete(key)

	def test_create_many_delete_many_lifo(self):
		keys = self._create_many()
		for key in reversed(keys):
			self.entity.delete(key)

################################
# concrete testcases generator #
################################

def generate_testsuite(environment, entities):
	testsuite = unittest.TestSuite()
	for environment_profile in environment.profiles:
		for entity in entities:
			# _ProfiledEntity_In_ProfiledEnvironment_TestCase
			for entity_profile in entity.profiles:
				name = "%s%s_In_%sEnvironment_TestCase" % (
					entity_profile.title(),
					type(entity).__name__,
					environment_profile.title())
				cls = type(name, (_ProfiledEntity_In_ProfiledEnvironment_TestCase, unittest.TestCase), {
					"environment_profile": environment_profile,
					"environment": environment,
					"entity_profile": entity_profile,
					"entity": entity,
				})
				testsuite.addTest(unittest.makeSuite(cls))
			# _Entity_In_ProfiledEnvironment_TestCase
			name = "%s_In_%sEnvironment_TestCase" % (
				type(entity).__name__,
				environment_profile.title())
			cls = type(name, (_Entity_In_ProfiledEnvironment_TestCase, unittest.TestCase), {
				"environment_profile": environment_profile,
				"environment": environment,
				"entity": entity,
			})
			testsuite.addTest(unittest.makeSuite(cls))
	return testsuite

def test(environment, entities, failfast = False, verbosity = 2):
	"generate and run test cases, return unittest.TestResult"
	testsuite = generate_testsuite(environment, entities)
	return unittest.TextTestRunner(
		failfast = failfast,
		verbosity = verbosity).run(testsuite)

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

		def get_key(self, profile):
			return profile

		creation_policy = 1

		def create(self, profile, tampering = None):
			key = self.get_key(profile)
			self.created[key] = True
			return key

		def exists(self, key):
			return key in self.created and self.created[key]

		def delete(self, key):
			if not self.exists(key):
				raise NoSuchResource(key)
			self.created[key] = False

		def update(self, key, profile): pass

	test(
		environment = FakeEnvironment(),
		entities = (FakeEntity(),))

