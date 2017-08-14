#!/usr/bin/env python3
# Part of PieCoin educational project by SweetPalma, 2017. All rights reserved.
from threading import Thread
import socket
import struct


# Local modules:
from nanocoin.config import (NANOCOIN_ENCODING,
	NANOCOIN_RANGE)


# Nanocoin message structure:
# NANOCOINXXXXYYYYMMMMMMMMMMMMMMM...
#
# NANOCOIN - Nanocoin header.
# XXXX     - 4 bytes of sender port.
# YYYY     - 4 bytes of message length.
# MMMM...  - Message body, length is defined by YYYY.

# Nanocoin message response structure:
# XXXXMMMMMMMMMMMMMMMMMMMMMMMMMM...
#
# XXXX    - 4 bytes of message length.
# MMMM... - Message body.


# Genral class:
class Socket(object):
	''' Object that performs socket manipulations. '''

	def __init__(self, port: int = None):
		''' Returns new NanoCoin Socket object. '''
		# Looking for a free port:
		if not port:
			for port in range(*NANOCOIN_RANGE):
				if self.isfree(port):
					break

		# If port is already taken:
		elif not self.isfree(port):
			raise ValueError('Port %d is already taken!' % port)

		# Basic values:
		self.handler = None
		self.encoding = NANOCOIN_ENCODING
		self.handler = None
		self.alive = False
		self.port = port


	@staticmethod
	def isfree(port: int) -> bool:
		''' Tests some port for being free to bind. '''
		try:
			tester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tester.bind(('localhost', port))
		except OSError:
			result = False
		else:
			result = True
		finally:
			tester.close()
			return result


	def start(self, daemon: bool = True):
		''' Starts current socket handler in a separate thread. '''

		# Preparing socket:
		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listener.bind(('localhost', self.port))
		listener.listen(5)

		# Loop body:
		def loop_body():

			# Main loop:
			while self.alive:

				# Waiting for new connection:
				try:

					# Accepting it and reading NanoCoin header:
					connection, address = listener.accept()
					if not connection.recv(8) == b'NANOCOIN':
						raise socket.error('Message with invalid header.')

					# Reading rest of PieCoin message header (sender and len):
					try:
						sender, message_length = struct.unpack('!II', 
							connection.recv(4 * 2))
					except struct.error:
						raise socket.error('Message with invalid header size.')

					# Reading rest of message:
					message = connection.recv(message_length).decode(self.encoding)

					# Handling and encoding:
					answer = self.handler(sender, message) or 'ok'
					answer = bytes(answer, self.encoding)

					# Sending answer:
					result_length = struct.pack('!I', len(answer))
					connection.send(result_length + answer)

				# Catching errors:
				except socket.error as e:
					print('Shit: %s' % e)

				# Closing connection:
				finally:
					connection.close()

			# Closing:
			listener.close()

		# Starting thread:
		self.alive = True
		self.thread = Thread(target=loop_body)
		self.thread.daemon = daemon
		self.thread.start()


	def stop(self):
		''' Stops current socket handler. '''
		self.alive = False
		self.thread.join()


	def send(self, port: int, message: str) -> str:
		''' Send message to certain port or list of ports. '''

		# In case if input is list of ports:
		if isinstance(port, list):
			result = []
			for p in port:
				result.append(self.send(p, message))
			return result

		# Encoding message body:
		message = bytes(message, self.encoding)

		# Building message header (piecoin label, sender port and length):
		message_header = struct.pack('!II', self.port, len(message))
		message_header = b'NANOCOIN' + message_header

		# Operning socket and sending message:
		try:
			connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connection.connect(('localhost', port))
			connection.send(message_header + message)
		except (socket.error, OSError, ConnectionError):
			return False

		# Receiving answer:
		try:
			size   = struct.unpack('!I', connection.recv(4))[0]
			result = connection.recv(size).decode(self.encoding)

		except struct.error:
			result = False

		# Closing and returning:
		connection.close()
		return result


	def locate(self, port_range:tuple = NANOCOIN_RANGE) -> list:
		''' Returns list of other available nodes. '''
		result = []
		for port in range(*port_range):
			if port != self.port:
				answer = self.send(port, 'hi')
				if answer:
					result.append(port)
		return result
