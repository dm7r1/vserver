import asyncore
import socket
import settings
from encryption import CipherAes, CipherRSA
from utils.parsejson import bjson2object, object2bjson
from json import JSONDecodeError
from handlers.userHandler import Handler
from db import DB
from usersHandlers import UsersHandlers
from random import getrandbits
from Cryptodome.PublicKey import RSA
from hashlib import sha256
from pbkdf2 import pbkdf2

TOKEN_BITS = 128
BUSY_USER = -2
INVALID_USER = -1


class ConnectionsHandler(asyncore.dispatcher):
	MAX_PEERS = 8192
	KEY_SIZE = 16

	def __init__(self):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind((settings.address, settings.mainPort))
		self.listen(ConnectionsHandler.MAX_PEERS)
		self.first = True

		self.private_key = RSA.generate(2048)
		self.public_key = self.private_key.publickey()
		self.decrypter_rsa = CipherRSA(None, self.private_key)

		self.users = DB.Users()

	@staticmethod
	def make_a_token():
		return hex(getrandbits(TOKEN_BITS))[2:].ljust(TOKEN_BITS // 8, "0")

	def handle_accept(self):
		connection = self.accept()
		if connection is not None:
			try:
				sock, addr = connection
				sock.setblocking(True)
				sock.settimeout(3.0)  # ????
				try:
					req = bjson2object(sock.recv(512))
					if req["operation"] == "get_pubkey":
						sock.send(object2bjson({"key": self.public_key.export_key().decode()}))
					req = bjson2object(self.decrypter_rsa.decrypt(sock.recv(512)))
					result = self.validate_user(req["data"])
					cipher_aes = CipherAes(req["data"]["session_key"].to_bytes(ConnectionsHandler.KEY_SIZE, "big"))
					if result == INVALID_USER:
						sock.send(cipher_aes.encrypt(object2bjson({"result": "invalid"})))
						sock.close()
					elif result == BUSY_USER:
						sock.send(cipher_aes.encrypt(object2bjson({"result": "busy"})))
						sock.close()
					else:
						token = self.make_a_token()
						Handler(sock, result, token, cipher_aes, port=req["data"]["port"], dbusers=self.users)
				except (JSONDecodeError, KeyError):
					pass
			except socket.error:
				pass

	def shutdown(self):
		print()
		self.users.close()

	def validate_user(self, data):
		user = self.users.get_by_login(data["login"])
		if user is None:
			return INVALID_USER
		if user.password != pbkdf2(sha256, data["password"].encode(), user.salt, 1000, 64):
			return INVALID_USER
		if UsersHandlers.exists(user.id):
			return BUSY_USER
		return user


