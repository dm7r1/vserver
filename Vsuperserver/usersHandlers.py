class UsersHandlers:
	units = {}

	@staticmethod
	def add(user_handler):
		UsersHandlers.units[user_handler.user.id] = user_handler

	@staticmethod
	def rem(uid):
		del UsersHandlers.units[uid]

	@staticmethod
	def get(uid):
		return UsersHandlers.units[uid]

	@staticmethod
	def exists(uid):
		return uid in UsersHandlers.units
