# copyright (c) 2014 fclaerhout.fr, released under the MIT license.

"Test Generation Framework -- see bundled README.md for usage instructions"

__version__ = "0.1"

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

class Resources(object):

	__metaclass__ = abc.ABCMeta

	profiles = ("default",)

	tamperings = ()

	@abc.abstractmethod
	def get_key(self, profile): pass

	creation_policy = 0 # Options: 0, 1, 2

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

class _ProfiledResource_In_ProfiledEnvironment_TestCase(_Common):

	def test_test_delete(self):
		"the deletion of an inexisting instance fails"
		key = self.resource.get_key(self.resource_profile)
		if key is not None:
			self.assertFalse(self.resource.exists(key))
			self.assertRaises(NoSuchResource, self.resource.delete, key)

	def test_create_test_delete(self):
		"a created instance exists and can be deleted"
		key = self.resource.create(self.resource_profile)
		self.assertTrue(self.resource.exists(key), "%s: not created" % key)
		self.resource.delete(key)
		self.assertFalse(self.resource.exists(key), "%s: not deleted" % key)

	def test_creation_policy(self):
		"creating twice the same instance ..."
		try:
			key1 = self.resource.create(self.resource_profile)
			if self.resource.creation_policy == 0:
				self.assertRaises(ResourceExists, self.resource.create, self.resource_profile)
			elif self.resource.creation_policy == 1:
				key2 = self.resource.create(self.resource_profile)
				self.assertEqual(key1, key2)
			elif self.resource.creation_policy == 2:
				key2 = self.resource.create(self.resource_profile)
				self.assertNotEqual(key1, key2)
			else:
				raise Exception("%s: unsupported creation policy" % self.creation_policy)
		except AssertionError:
			print "** current creation policy is", self.resource.creation_policy, "- creating twice the same instance", {
				"0": "should fail",
				"1": "should succeed and return the same key",
				"2": "should succeed and return a different key",
			}["%s" % self.resource.creation_policy]
			raise

	def test_no_double_delete(self):
		"a same instance cannot be deleted twice"
		key = self.resource.create(self.resource_profile)
		self.resource.delete(key)
		self.assertRaises(NoSuchResource, self.resource.delete, key)

	def test_invalid_input_on_creation(self):
		"creation with an invalid input fails"
		for tampering in self.resource.tamperings:
			self.assertRaises(
				ValidationError,
				self.resource.create,
				profile = self.resource_profile,
				tampering = tampering)

class _Resource_In_ProfiledEnvironment_TestCase(_Common):

	def _create_many(self):
		"create many instances, return keys"
		if self.resource.creation_policy in (0, 1):
			return tuple(self.resource.create(profile) for profile in self.resource.profiles)
		else:
			return tuple(self.resource.create(profile) for profile in self.resource.profiles for i in xrange(100))

	def test_create_many_delete_many_fifo(self):
		keys = self._create_many()
		for key in keys:
			self.resource.delete(key)

	def test_create_many_delete_many_lifo(self):
		keys = self._create_many()
		for key in reversed(keys):
			self.resource.delete(key)

################################
# concrete testcases generator #
################################

def generate_testsuite(environment, resources):
	testsuite = unittest.TestSuite()
	for environment_profile in environment.profiles:
		for resource in resources.values():
			# allow each resource to access others to resolve dependencies
			resource.resources = resources
			# _ProfiledResource_In_ProfiledEnvironment_TestCase
			for resource_profile in resource.profiles:
				name = "%s%s_In_%sEnvironment_TestCase" % (
					resource_profile.title(),
					type(resource).__name__,
					environment_profile.title())
				cls = type(name, (_ProfiledResource_In_ProfiledEnvironment_TestCase, unittest.TestCase), {
					"environment_profile": environment_profile,
					"environment": environment,
					"resource_profile": resource_profile,
					"resource": resource,
				})
				testsuite.addTest(unittest.makeSuite(cls))
			# _Resource_In_ProfiledEnvironment_TestCase
			name = "%s_In_%sEnvironment_TestCase" % (
				type(resource).__name__,
				environment_profile.title())
			cls = type(name, (_Resource_In_ProfiledEnvironment_TestCase, unittest.TestCase), {
				"environment_profile": environment_profile,
				"environment": environment,
				"resource": resource,
			})
			testsuite.addTest(unittest.makeSuite(cls))
	return testsuite

def test(environment, resources, failfast = False, verbosity = 2):
	"generate and run test cases, return unittest.TestResult"
	testsuite = generate_testsuite(environment, resources)
	return unittest.TextTestRunner(
		failfast = failfast,
		verbosity = verbosity).run(testsuite)
