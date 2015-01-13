# copyright (c) 2015 fclaerhout.fr, released under the MIT license.

import testgear

class FakeEnvironment(testgear.Environment):

	profiles = ("foo", "bar", "baz")

	def setUp(self, profile): pass

	def tearDown(self): pass

class FakeResources(testgear.Resources):

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
			raise testgear.NoSuchResource(key)
		self.created[key] = False

	def update(self, key, profile): pass

testgear.test(
	environment = FakeEnvironment(),
	resources = (FakeResources(),))