import sqlite3
import traceback
from datetime import datetime


class Model:
	class User:
		def __init__(self, data, users_db):
			self.id = data[0]
			self.email = data[1]
			self.login = data[2]
			self.password = data[3]
			self.avatar_path = data[4]
			self.last_seen = data[5]
			self.salt = data[6]
			self.db = users_db

		def remove_friend(self, uid):
			return self.db.remove_friend(self.id, uid)

		def send_request(self, uid):
			return self.db.send_request(self.id, uid)

		def add_to_contacts(self, uid):
			return self.db.add_to_contacts(self.id, uid)

		def get_contacts(self):
			ids_data = self.db.get_contacts_ids_by_id(self.id)
			contacts = []
			for contact_id in ids_data:
				contact_id = contact_id[0]
				contact = self.db.get_by_id(contact_id)
				if contact is not None:
					contacts.append([contact_id, contact.login, contact.last_seen])
			return contacts

		def get_requests(self):
			ids_data = self.db.get_requests_ids_by_id(self.id)
			reqs = []
			for req_id in ids_data:
				req_id = req_id[0]
				requester = self.db.get_by_id(req_id)
				if requester is not None:
					reqs.append([req_id, requester.login])
			return reqs

		def search_people(self, q):
			people = self.db.search_people(q)
			if people:
				return people
			else:
				return []

		def get_last_seen(self):
			return self.last_seen

		def update_last_seen(self):
			self.db.update_last_seen(self.id)

		def __str__(self):
			return "id " + str(self.id) + "\nlogin " + str(self.login)


class DB:
	class DangerousData(Exception):
		def __init__(self):
			print("DANGEROUS DATA")

	@staticmethod
	def safe_str(data):
		try:
			string = str(data)
			if "'" in string or '"' in string or " " in string or "(" in string or ")" in string:
				raise DB.DangerousData()
			return string
		except Exception:
			raise DB.DangerousData()

	class Users:
		def __init__(self):
			self.connection = sqlite3.connect("../Vsite/db.sqlite3")
			self.cursor = self.connection.cursor()

		def get_by_id(self, u_id):
			try:
				self.cursor.execute("SELECT * FROM intro_vuser WHERE _id=" + DB.safe_str(u_id))
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return None
			data = self.cursor.fetchone()
			if data is None:
				return None
			return Model.User(data, self)

		def update_last_seen(self, u_id):
			try:
				self.cursor.execute(
					"UPDATE intro_vuser SET last_seen = " + DB.safe_str(int(datetime.now().timestamp()))
					+ " WHERE _id = " + DB.safe_str(u_id))
				self.connection.commit()
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				pass

		def get_by_login(self, u_login):
			try:
				self.cursor.execute("SELECT * FROM intro_vuser WHERE login='" + DB.safe_str(u_login) + "'")
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return None
			data = self.cursor.fetchone()
			if data is None:
				return None
			return Model.User(data, self)

		def get_contacts_ids_by_id(self, u_id):
			try:
				self.cursor.execute("SELECT to_vuser_id FROM intro_vuser_contacts WHERE from_vuser_id=" + DB.safe_str(u_id))
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return []
			return self.cursor.fetchall()

		def search_people(self, q):
			try:
				self.cursor.execute("SELECT _id, login FROM intro_vuser WHERE login LIKE '%" + DB.safe_str(q) + "%'")
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return []
			return self.cursor.fetchall()

		def get_requests_ids_by_id(self, u_id):
			try:
				self.cursor.execute("SELECT to_vuser_id FROM intro_vuser_requests WHERE from_vuser_id=" + DB.safe_str(u_id))
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return []
			return self.cursor.fetchall()

		def remove_friend(self, uid1, uid2):
			try:
				self.cursor.execute(
					"DELETE FROM intro_vuser_contacts WHERE from_vuser_id="
					+ DB.safe_str(uid2) + " AND to_vuser_id=" + DB.safe_str(uid1))
				self.cursor.execute(
					"DELETE FROM intro_vuser_contacts WHERE from_vuser_id="
					+ DB.safe_str(uid1) + " AND to_vuser_id=" + DB.safe_str(uid2))
				self.connection.commit()
				return True
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return False

		def add_to_contacts(self, requester_id, u_id2):
			try:
				self.cursor.execute(
					"DELETE FROM intro_vuser_requests WHERE from_vuser_id="
					+ DB.safe_str(u_id2) + " AND to_vuser_id=" + DB.safe_str(requester_id))
				if requester_id != u_id2:
					self.cursor.execute(
						"DELETE FROM intro_vuser_requests WHERE from_vuser_id="
						+ DB.safe_str(requester_id) + " AND to_vuser_id=" + DB.safe_str(u_id2))
				self.cursor.execute(
					"INSERT INTO intro_vuser_contacts (from_vuser_id, to_vuser_id) VALUES ("
					+ DB.safe_str(requester_id) + "," + DB.safe_str(u_id2) + ")")
				if requester_id != u_id2:
					self.cursor.execute(
						"INSERT INTO intro_vuser_contacts (to_vuser_id, from_vuser_id) VALUES ("
						+ DB.safe_str(requester_id) + "," + DB.safe_str(u_id2) + ")")
				self.connection.commit()
				return True
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return False

		def send_request(self, requester_id, to_id):
			try:
				self.cursor.execute(
					"SELECT to_vuser_id FROM intro_vuser_contacts WHERE "
					"from_vuser_id=" + DB.safe_str(requester_id) + " AND to_vuser_id=" + DB.safe_str(to_id))
				contacts = self.cursor.fetchall()
				if len(contacts) == 0:
					self.cursor.execute(
						"INSERT INTO intro_vuser_requests (from_vuser_id, to_vuser_id)"
						+ " VALUES (" + DB.safe_str(to_id) + "," + DB.safe_str(requester_id) +
						")")
					self.connection.commit()
					return True
				else:
					return False
			except (sqlite3.Error, DB.DangerousData):
				traceback.print_exc()
				return False

		def close(self):
			self.cursor.close()
			self.connection.close()

