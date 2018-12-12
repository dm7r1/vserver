from socket import *
from usersHandlers import UsersHandlers
from handlers.userHandler import Handler

proxy_socket = socket(AF_INET, SOCK_DGRAM)
proxy_socket.bind(("", 8888))


def proxy_handle():
	while True:
		try:
			data, addr = proxy_socket.recvfrom(5000)
			user_handler = UsersHandlers.get_by_ip(addr[0])

			data = user_handler.cipher_aes.decrypt(data)
			data_type = data[0]

			if data_type > 2:
				user_handler.call_addresses[data_type - 3] = addr
				continue

			receiver_uid = int.from_bytes(data[1:5], "big")

			proxy_socket.sendto(data[5:], UsersHandlers.get(receiver_uid).call_addresses[data_type])
		except Exception as e:
			pass
