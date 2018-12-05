class UsersHandlers:
	units = {}
	units_by_ips = {}

	@staticmethod
	def add(user_handler):
		UsersHandlers.units[user_handler.user.id] = user_handler
		UsersHandlers.units_by_ips[user_handler.ip] = user_handler

	@staticmethod
	def rem(uid):
		del UsersHandlers.units_by_ips[UsersHandlers.units[uid].ip]
		del UsersHandlers.units[uid]

	@staticmethod
	def get(uid):
		return UsersHandlers.units[uid]

	@staticmethod
	def get_by_ip(ip):
		return UsersHandlers.units_by_ips[ip]

	@staticmethod
	def exists(uid):
		return uid in UsersHandlers.units
