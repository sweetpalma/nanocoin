#!/usr/bin/env python3
# Part of PieCoin educational project by SweetPalma, 2017. All rights reserved.
from functools import reduce
from math import gcd
import hashlib
import random


# Default public exponent:
from nanocoin.config import (NANOCOIN_ENCODING, 
	NANOCOIN_HASH, NANOCOIN_EXPONENT)


# NEVER USE THIS WAY OF CHECKING PRIMALITY OF NUMBER IN REAL PROJECTS.
# IT'S USED HERE ONLY FOR DEMONSTRATION. USE MILLER-RABIN TEST INSTEAD.
def isprime(n: int, k: int = 500) -> bool:
	''' Returns result of fermat primality test for number. '''
	if n in [1, 2, 3]:
		return True
	if n % 2 == 0:
		return False
	for i in range(k):
		a = random.randint(1, n - 1)
		if pow(a, n - 1, n) != 1:
			return False
	return True


def lcm(*numbers: list) -> int:
	''' Returns largest common multiple for numbers. '''
	def lcm(a, b):
		return (a * b) // gcd(a, b)
	return reduce(lcm, numbers, 1)


def prime(length: int) -> int:
	''' Returns random prime number with given length. '''
	
	# Ranging:
	start = 10 ** (length - 1)
	end = start * 10 - 1

	# Looking for a prime:
	while True:
		possible_prime = random.randint(start, end)
		if (isprime(possible_prime)):
			return possible_prime


def egcd(a: int, b: int) -> int:
	if a == 0:
		return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)


def mulinv(b: int, n: int) -> int:
	''' Returns modular inverse. '''
	g, x, _ = egcd(b, n)
	if g == 1:
		return x % n


def generate(length, e: int = NANOCOIN_EXPONENT) -> (int, int):
	''' Returns RSA key pair (without public exponent). '''
	while True:
		p, q = prime(length // 2), prime(length // 2)
		totient = lcm(p - 1, q - 1)
		if gcd(e, totient) == 1:
			break

	# Generating public key:
	n = p * q

	# Generating private key:
	d = mulinv(e, totient)
	return (n, d)


def encrypt_number(n: int, key_two: int, key_one: int = NANOCOIN_EXPONENT)->int:
	''' Encrypts number with given keys. '''
	if n > key_two:
		raise ValueError('Input should be less than key!')
	return pow(n, key_one, key_two)


def decrypt_number(n: int, key_two: int, key_one: int = NANOCOIN_EXPONENT)->int:
	''' Decrypts number with given keys. '''
	if n > key_two:
		raise ValueError('Input should be less than key!')
	return pow(n, key_one, key_two)


def hash_string(data) -> int:
	''' Get hash of string data. '''
	hash_func = getattr(hashlib, NANOCOIN_HASH)
	if not isinstance(data, bytes):
		data = bytes(data, NANOCOIN_ENCODING)
	return int(hash_func(data).hexdigest(), base=16)


def encrypt_hash(data, key_two: int, key_one: int = NANOCOIN_EXPONENT) -> int:
	''' Calculates hash of data and encrypts it. '''
	return decrypt_number(hash_string(data), key_two, key_one)


def decrypt_hash(data, key_two: int, key_one: int = NANOCOIN_EXPONENT) -> str:
	''' Decrypts encrypted hash and returns it. '''
	hash_data = decrypt_number(data, key_two, key_one)
	return hash_data
