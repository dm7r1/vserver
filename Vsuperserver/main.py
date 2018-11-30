from connectionsHandler import ConnectionsHandler
import asyncore
import threading


class ConnHandlerThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("starting server")
		self.server = ConnectionsHandler()
		asyncore.loop()

	def stop(self):
		print("closing")
		asyncore.close_all()


cht = ConnHandlerThread()
cht.setDaemon(True)
cht.start()


while True:
	try:
		command = str(input())
		if command == "close":
			print(command)
			cht.stop()
			break
	except KeyboardInterrupt:
		cht.stop()
		break

print("Server closed")
