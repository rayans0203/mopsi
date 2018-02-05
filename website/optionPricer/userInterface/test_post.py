from django.test import TestCase
from . import models

class PostTestCase(TestCase):
	def setUp(self):
		title='Titre de test pour les posts'
		self.post=models.Post()
		self.post.title=title

	def test_str(self):
		'Titre de test pour les posts'
		self.assertEqual(self.post.__str__(),'Titre de test pour les posts')




