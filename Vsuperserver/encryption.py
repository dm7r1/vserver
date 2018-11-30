from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Util.Padding import pad, unpad


class CipherAes:
	def __init__(self, key):
		self.encrypter = AES.new(key, AES.MODE_CBC)
		self.decrypter = AES.new(key, AES.MODE_CBC)

	def decrypt(self, encrypted_data):
		return unpad(self.decrypter.decrypt(encrypted_data[8:]), AES.block_size)[AES.block_size:]

	def encrypt(self, data):
		enc_data = self.encrypter.encrypt(pad(get_random_bytes(AES.block_size) + data, AES.block_size))
		return len(enc_data).to_bytes(8, "big") + enc_data


class CipherRSA:
	def __init__(self, another_publickey, my_privatekey):
		if another_publickey:
			self.encrypter = PKCS1_OAEP.new(RSA.import_key(another_publickey))
		if my_privatekey:
			self.decrypter = PKCS1_OAEP.new(my_privatekey)

	def encrypt(self, data):
		return self.encrypter.encrypt(data)

	def decrypt(self, data):
		return self.decrypter.decrypt(data)
