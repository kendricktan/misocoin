# Here we define the structure of our object

from functools import reduce
from typing import List, Union, Dict

from misochain.hashing import sha256


class Vin:
    def __init__(self, txid: str, index: int, signature: str):
        '''
        txid:  The transaction id               
        index: Index of the vout in the list of transactions
        signature: signature to know that the sender actually verified
                   the payment
        '''
        self.txid = txid
        self.index = index
        self.signature = signature


class Vout:
    def __init__(self, address: str, value: int):
        '''
        address: Which address are we paying?
        value:   How much are we paying?
        '''
        self.address = address
        self.value = value


class Coinbase:
    '''
    Note: Coinbase is a transaction type
    Each block contains ONE coinbase transcation. Coinbase
    magically produces money (and fees in the block) to
    whoever who solves the block.

    Vins are used to construct the hash, and are the
    vins of the transaction in the same block
    '''

    def __init__(self, txid: str, vins: [Vin], vouts: [Vout], reward_address: str, reward_amount: int):
        '''
        txid:          Txid of the Coinbase transaction
        vins:          All vins inside the block
        vouts:         All vouts inside the block
        reward_address: Address of miner who found the solution to block
        reward_amount:  Amount rewarded
        '''
        self.txid = txid
        self.vins = vins
        self.vouts = vouts
        self.reward_address = reward_address
        self.reward_amount = reward_amount


class Transaction:
    def __init__(self, txid: str, vins: List[Union[Coinbase, Vin]], vouts: List[Vout]):
        '''
        txid:  Transaction id of the hashes
        vins:  List of inputs (where we our money is supplied from)
               Note: First item in array will always be a coinbase
        vouts: List of outputs (where our supplied money is going to go)
        '''
        self.txid = txid
        self.vins = vins
        self.vouts = vouts


class Block:
    def __init__(self,
                 block_hash: str,
                 transactions: List[Transaction],
                 height: int,
                 timestamp: int,
                 difficulty: int,                 
                 nonce: str):
        '''
        blockHash: Hash of the block
        transactions: Transactions in our blockchain
        height:  Current block height
        '''
        self.block_hash = block_hash
        self.transactions = transactions
        self.height = height
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce        