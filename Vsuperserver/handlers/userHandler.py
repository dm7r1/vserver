import asyncore
from db import DB
from utils.parsejson import bjson2object, object2bjson
from json import JSONDecodeError
from usersHandlers import UsersHandlers


class Handler(asyncore.dispatcher):
	def __init__(self, sock, user, token, cipher_aes, port, dbusers):
		asyncore.dispatcher.__init__(self)
		self.set_socket(sock)
		self.data_to_send = ""
		self.user = user

		self.users = dbusers
		self.users = DB.Users()
		self.token = token
		self.cipher_aes = cipher_aes

		self.send2client(None, {
			"result":   "pubkey_left",
			"id":       user.id,
			"token":    token
			}
		)

		req = bjson2object(cipher_aes.decrypt(sock.recv(2048)))
		if self.validate(req) and req["operation"] == "set_user_pubkey":
			self.user_pubkey = req["user_pubkey"]
		else:
			raise Exception("user didnt send pubkey")
		self.ip = sock.getpeername()[0]
		self.port = port

		UsersHandlers.add(self)

		print(" [+] new connection ", self.user.login, self.ip, self.port)
		contacts = self._get_contacts()

		self.get_contacts()
		self.get_requests()
		self.send_updates_to_friends(contacts)

	@staticmethod
	def bytes_to_int(array):
		n = 0
		for i in range(len(array)):
			n <<= 8
			n += array[i]
		return n

	def send_updates_to_friends(self, contacts):
		for contact in contacts:
			cid = contact[0]
			if UsersHandlers.exists(cid) and cid != self.user.id:
				UsersHandlers.get(cid).get_contacts()

	def handle_read(self):
		try:
			req = bjson2object(self.cipher_aes.decrypt(self.recv(512)))
		except JSONDecodeError as err:
			return
		except Exception as err:
			print(" ERROR: " + str(err))
			return

		try:
			if self.validate(req):
				operation = req["operation"]
				if operation == "get_msgs":
					self.get_msgs()
				elif operation == "get_requests":
					self.get_requests()
				elif operation == "search_people":
					self.search_people(req)
				elif operation == "send_request":
					self.send_request(req)
				elif operation == "add_to_contacts":
					self.add_to_contacts(req)
				elif operation == "remove_friend":
					self.remove_friend(req)
		except KeyError as err:
			return
		except Exception as err:
			print(" ERROR: " + str(err))
			return

	def send2client(self, operation, data):
		if operation:
			data["operation"] = operation
		self.send(self.cipher_aes.encrypt(object2bjson(data)))

	def send_request(self, data):
		uid = data["uid"]
		if self.user.send_request(uid):
			if UsersHandlers.exists(uid):
				UsersHandlers.get(uid).get_requests()

	def remove_friend(self, data):
		uid = data["uid"]
		if self.user.remove_friend(uid):
			self.get_contacts()
			if UsersHandlers.exists(uid):
				UsersHandlers.get(uid).get_contacts()

	def add_to_contacts(self, data):
		uid = data["uid"]
		if self.user.add_to_contacts(uid):
			self.get_requests()
			self.get_contacts()
			if UsersHandlers.exists(uid):
				UsersHandlers.get(uid).get_contacts()

	def get_requests(self):
		self.send2client("get_requests", {"requests": self.user.get_requests()})

	def search_people(self, data):
		self.send2client(
			"search_people",
			{"people": self.user.search_people(data["q"])})

	def get_msgs(self):
		self.send2client("get_msgs", {"msgs": []})

	def _get_msgs(self):
		return []

	def _get_contacts(self):
		contacts = self.user.get_contacts()
		for contact in contacts:
			cid = contact[0]
			if UsersHandlers.exists(cid):
				contact_uhandler = UsersHandlers.get(cid)
				# ONLINE
				contact.append(contact_uhandler.ip)
				contact.append(contact_uhandler.port)
				contact.append(contact_uhandler.user_pubkey)
			else:
				# OFFLINE
				contact.append("")
				contact.append(-1)
				contact.append("")

		return contacts

	def validate(self, req):
		return req["id"] == self.user.id and req["token"] == self.token

	def get_contacts(self):
		self.send2client("get_contacts", {"contacts": self._get_contacts()})

	def handle_close(self):
		print(" [-] disconnected ", self.user.login, self.ip, self.port)
		self.user.update_last_seen()
		UsersHandlers.rem(self.user.id)
		self.send_updates_to_friends(self._get_contacts())
		self.close()
