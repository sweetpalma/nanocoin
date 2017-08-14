========
Nanocoin
========
Blockchain currencies for dummies!

What the hell this is about?
============================
NanoCoin is a toy cryptocurrency that was made entirely as a demonstration of general blockchain currency principlies in a simple manner. It was done in a extremely short period of time (in couple of days), so forgive me for possible typos, bugs, kernel panics, development database failures and so on.

Do you have any differences with Bitcoin?
=========================================
Yes, Nanocoin is simplified in some aspects:

* Bitcoin uses SHA for hashing, Nanocoin uses MD5.
* Bitcoin uses complicated ECDSA for signing, Nanocoin uses good old RSA with fixed public exponent.
* Bitcoin works with overcomplicated input-output transactions, Nanocoin' transactions are simple as hell (and vulnerable too).
* Bitcoin difficulty is number of zeroes in the start of hash, Nanocoin counts tail zeroes.
* Bitcoin mining reward divides by two like every two years, Nanocoin reward is constant.

What about a short example?
===========================

.. code-block:: python

	# Import and making new blockchain to work with:
	from nanocoin import Chain
	chain = Chain()

	# Generating two wallets:
	your_wallet, your_key = chain.wallet()
	other_wallet, other_wallet = chain.wallet()

	# Mining first block with only 50 nanocoins reward:
	chain.mine(your_wallet)
	print(chain.balance(your_wallet))

	# Making first transaction from your wallet to other wallet and mining again:
	chain.transact(your_wallet, other_wallet, 25.0, your_key)
	chain.mine(your_wallet)

	# Displaying final balance and chain:
	print('Your balance is %d, other wallet is %d.' % (
		chain.balance(your_wallet), chain.balance(other_wallet)))
	print('Final blockchain look: %s.' % chain.text(indent=4))


License, huh?
=============
Nanocoin is licensed under MIT, so, basically, do whatever you want.