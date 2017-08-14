#!/usr/bin/env python3
# Part of PieCoin educational project by SweetPalma, 2017. All rights reserved.
from functools import reduce
import json


# Local modules:
from nanocoin.config import NANOCOIN_LENGTH
from nanocoin.transaction import Transaction
from nanocoin.block import Block
from nanocoin.rsa import generate


# General class:
class Chain(object):
	''' Object that holds block data. '''

	def __init__(self, blocks=[], transactions=[]):
		''' Returns new NanoCoin Chain object. '''
		self.transactions = transactions
		self.blocks = blocks


	@staticmethod
	def wallet() -> (int, int):
		''' Returns pair of new generated wallet. '''
		return generate(NANOCOIN_LENGTH)


	def mine(self, receiver: int = None, save: bool = True):
		''' Mines new block with current transactions. '''

		# Peparing block:
		block = Block(self.transactions, len(self.blocks))
		self.transactions = []
		if len(self.blocks) > 0:
			block.previous_hash = self.blocks[-1].current_hash

		# Mining:
		block.mine(receiver)

		# Done:
		if save:
			self.blocks.append(block)
		return block


	def transact(self, sender: int, receiver: int, amount: float, key: int):
		''' Tries to perform transaction signed with key. '''

		# Checking balance in previous block and current transactions:
		sender_balance = self.balance(sender)
		for t in self.transactions:
			sender_balance = sender_balance + t.balance(sender)
		if sender_balance < amount or amount < 0:
			raise ValueError('Invalid amount!')

		# Preparing and signing transaction:
		transaction = Transaction(sender, receiver, amount)
		transaction.sign(key)

		# Done:
		self.transactions.append(transaction)
		return transaction


	def validate(self) -> bool:

		# Validating blocks:
		previous_block = None
		for depth, block in enumerate(self.blocks):

			# General validation:
			block.validate()

			# Checking previous block hash:
			if previous_block != None:
				if previous_block.current_hash != block.previous_hash:
					raise ValueError(
						'Previous block hash is not equal between blocks!')

			# Checking depth:
			if block.depth != depth:
				raise ValueError('Invalid depth!')

			# Updating previous block:
			previous_block = block


	def reduce(self, method, initial=0):
		''' Performs list reduction on current blocks. '''
		return reduce(method, self.blocks, initial)


	def balance(self, address: int) -> float:
		def reducer(balance, b):
			return balance + b.balance(address)
		return self.reduce(reducer, 0.0)


	def json(self) -> dict:
		''' Returns JSON-seriazable dictionary that represents current chain.'''
		return [b.json() for b in self.blocks]


	def text(self, indent: int = None, sort_keys: int = False) -> str:
		''' Returns serialized list that repsents chain. '''
		return json.dumps(self.json(), indent=indent, sort_keys=sort_keys)


	def __repr__(self) -> str:
		''' Returns serialized list that represents chain. '''
		return self.text(indent=4)

