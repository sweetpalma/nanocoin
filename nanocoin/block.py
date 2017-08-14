#!/usr/bin/env python3
# Part of PieCoin educational project by SweetPalma, 2017. All rights reserved.
from time import time as current_time
from functools import reduce
import json


# Local modules:
from nanocoin.config import (NANOCOIN_HASH, 
	NANOCOIN_REWARD, NANOCOIN_DIFFICULTY)
from nanocoin.transaction import Transaction
from nanocoin.rsa import hash_string


# General class:
class Block(object):
	''' Object that holds block data. '''

	def __init__(self, transactions=[], depth: int = 0, nonce: int = 0, 
			current_hash: int = 0, previous_hash: int = 0, time: int = None):
		''' Returns new NanoCoin Block object. '''
		self.transactions = transactions
		self.depth = depth
		self.nonce = nonce
		self.current_hash = current_hash
		self.previous_hash = previous_hash
		self.time = time


	def hash_data(self) -> str:
		''' Returns all data used for hashing. '''
		transactions = [t.text(sort_keys=True) for t in self.transactions]
		return str(self.previous_hash) + ''.join(transactions)


	def mine(self, receiver: int = None) -> int:
		''' Mines nonce for current block. '''

		# Adding reward transaction (if receiver wallet stated):
		if receiver:
			reward = Transaction(0, receiver, NANOCOIN_REWARD, 0)
			self.transactions.insert(0, reward)
		
		# Preparing mining values:
		current_hash, nonce = 0, 0
		self.time = current_time()
		data = self.hash_data()

		# Looking for a proper nonce:
		while not str(current_hash).endswith(NANOCOIN_DIFFICULTY * '0'):
			nonce = nonce + 1
			current_hash = hash_string(str(nonce) + data)

		# Done:
		self.current_hash = current_hash
		self.nonce = nonce
		return nonce


	def validate(self) -> bool:
		''' Validates self and raises errors in case of fail. '''

		# Checking nonce availibility:
		if not self.nonce:
			raise ValueError('No nonce!')

		# Comparing stated hash and real:
		if hash_string(str(self.nonce) + self.hash_data()) != self.current_hash:
			raise ValueError('Real hash is not equal to stated!')

		# Checking stated nonce difficulty:
		if not str(self.current_hash).endswith(NANOCOIN_DIFFICULTY * '0'):
			raise ValueError('Invalid nonce!')

		# Checking transactions:
		had_reward = False
		for t in self.transactions:

			# If reward transaction found:
			if t.sender == 0:
				if had_reward:
					raise ValueError(
						'Block has more than one reward transaction!')
				else:
					had_reward = True

			# Checking transaction time:
			if t.time > self.time:
				raise ValueError(
					'Transaction was made after the block was mined!')

			# Validating:
			t.validate()

		# If all is ok:
		return True


	def reduce(self, method, initial=0):
		''' Performs list reduction on current transactions. '''
		return reduce(method, self.transactions, initial)


	def balance(self, address: int) -> float:
		''' Returns balance of current transactions for address. '''
		def reducer(balance, t):
			if t.sender == address:
				balance = balance - t.amount
			elif t.receiver == address:
				balance = balance + t.amount
			return balance
		return self.reduce(reducer, 0.0)


	def json(self) -> dict:
		''' Returns JSON-seriazable dictionary that represents block. '''
		return {
			'depth': self.depth,
			'nonce': self.nonce,
			'current_hash': self.current_hash,
			'previous_hash': self.previous_hash,
			'time': self.time,
			'transactions': [t.json() for t in self.transactions],
		}


	def text(self, indent: int = None, sort_keys: int = False) -> str:
		''' Returns serialized dictionary that repsents block. '''
		return json.dumps(self.json(), indent=indent, sort_keys=sort_keys)


	def __repr__(self) -> str:
		''' Returns serialized dictionary that represents block. '''
		return self.text(indent=4)
