#!/usr/bin/env python3
# Part of PieCoin educational project by SweetPalma, 2017. All rights reserved.
from time import time as current_time
import json


# Local modules:
from nanocoin.config import (NANOCOIN_ENCODING, NANOCOIN_HASH, NANOCOIN_LENGTH,
	NANOCOIN_REWARD)
from nanocoin.rsa import (encrypt_hash, decrypt_hash, 
	encrypt_number, decrypt_number, hash_string)


# General class:
class Transaction(object):
	''' Object that holds transaction data. '''

	def __init__(self, sender: int, receiver: int, amount: float, \
			signature: int = None, time: int = None):
		''' Returns new NanoCoin Transaction object. '''
		self.signature = signature
		self.sender = sender
		self.receiver = receiver
		self.amount = amount
		self.time = int(time if time != None else current_time())


	def hash_data(self) -> str:
		''' Returns all data used for signing. '''
		fields = [self.sender, self.receiver, self.amount, self.time]
		return ''.join(map(str, fields))


	def sign(self, key:int) -> int:
		''' Signs current transaction with private key. '''

		# Checking key for being valid (239 is just a random number):
		c = encrypt_number(239, self.sender, key)
		if decrypt_number(c, self.sender) != 239:
			raise ValueError('Invalid key!')

		# Encrypting:
		self.signature = encrypt_hash(self.hash_data(), self.sender, key)
		return self.signature


	def validate(self) -> bool:
		''' Validates self and raises errors in case of fail. '''
		# Chechking average transaction:
		if self.sender != 0:

			# Checking sender address length:
			if len(str(self.sender)) != NANOCOIN_LENGTH:
				raise ValueError('Invalid sender address length.')

			# Checking signature availability:
			if not self.signature:
				raise ValueError('No signature.')

			# Validating signature:
			data = self.hash_data()
			if hash_string(data) != decrypt_hash(self.signature, self.sender):
				raise ValueError('Invalid signature!')

		# Checking reward transaction:
		else:

			# Checking reward amount:
			if self.amount != NANOCOIN_REWARD:
				raise ValueError('Invalid reward transaction amount!')

		# Checking receiver address length:
		if len(str(self.receiver)) != NANOCOIN_LENGTH:
			raise ValueError('Invalid receiver length.')

		# All is ok:
		return True


	def balance(self, address: int) -> float:
		''' Returns balance of current transactions for certain address. '''
		if self.sender == address:
			return -self.amount
		elif self.receiver == address:
			return self.amount
		return 0.0


	def json(self) -> dict:
		''' Returns JSON-seriazable dictionary that represents transaction. '''
		return {
			'signature': self.signature,
			'sender': self.sender,
			'receiver': self.receiver,
			'amount': self.amount,
			'time': self.time,
		}


	def text(self, indent: int = None, sort_keys: int = False) -> str:
		''' Returns serialized dictionry that repsents transaction. '''
		return json.dumps(self.json(), indent=indent, sort_keys=sort_keys)


	def __repr__(self) -> str:
		''' Returns serialized dictionary that represents transaction. '''
		return self.text(indent=4)

