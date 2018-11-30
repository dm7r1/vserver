from django.db import models
from os import urandom
from pbkdf2 import pbkdf2
from hashlib import sha256


class VUser(models.Model):
	_id = models.IntegerField(primary_key=True, auto_created=True)
	login = models.CharField(max_length=20)
	last_seen = models.BigIntegerField(default=0)
	email = models.EmailField(blank=True)
	password = models.BinaryField(max_length=64)
	avatar = models.FilePathField(blank=True)
	contacts = models.ManyToManyField("VUser", blank=True)
	requests = models.ManyToManyField("VUser", blank=True, related_name="reqs")
	salt = models.BinaryField(max_length=32, default="A"*32)

	@staticmethod
	def makenew(login, password):
		salt = urandom(32)
		return VUser.objects.create(login=login, password=pbkdf2(sha256, sha256(password.encode()).hexdigest().encode(), salt, 1000, 64), salt=salt)
