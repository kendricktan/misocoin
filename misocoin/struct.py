# Here we define the structure of our object

from functools import reduce
from typing import List, Union, Dict

from misocoin.hashing import sha256, get_hash


class Vin:
    def __init__(self, txid: str, index: int):
        '''
        txid:  The transaction id
        index: Index of the vout in the list of transactions
        pub_key: public key corresponding to the address
        signature: signature to verify sender authorized the
                   spending
        '''
        self.txid = txid
        self.index = index
        self.pub_key = ''
        self.signature = ''

    def __str__(self):
        return '\t\t[txid: {}, index: {}, pub_key: {}, signature: {}]'.format(
            self.txid, self.index, self.pub_key, self.signature
        )


class Vout:
    def __init__(self, address: str, amount: int):
        '''
        address: Which address are we paying?
        amount:   How much are we paying?
        '''
        self.address = address
        self.amount = amount

    def __str__(self):
        return '\t\t[address: {}, amount: {}]'.format(self.address, self.amount)


class Coinbase:
    '''
    Note: Coinbase is a transaction type
    Each block contains ONE coinbase transcation. Coinbase
    magically produces money (and fees in the block) to
    whoever who solves the block.    

    If you wanna reference coinbase as a txin, the index is 0
    '''

    def __init__(self, prev_block_hash: str, reward_address: str, reward_amount: int):
        '''
        prev_block_hash: hash of the previous successful block
        reward_address: Address of miner who found the solution to block
        reward_amount:  Amount rewarded
        '''
        self.prev_block_hash = prev_block_hash
        self.reward_address = reward_address
        self.reward_amount = reward_amount

    @property
    def txid(self):
        return get_hash(
            prev_block_hash=self.prev_block_hash,
            reward_address=self.reward_address,
            reward_amount=self.reward_amount
        )

    def __str__(self):
        return '\ttxid: {}\n\treward_address: {}\n\treward_amount: {}'.format(
            self.txid, self.reward_address, self.reward_amount
        )


class Transaction:
    def __init__(self, vins: List[Vin], vouts: List[Union[Vout, Coinbase]]):
        '''
        vins:  List of inputs (where we our money is supplied from)
               Note: First item in array will always be a coinbase
        vouts: List of outputs (where our supplied money is going to go)
        '''
        self.vins = vins
        self.vouts = vouts

    @property
    def txid(self):
        return get_hash(vins=self.vins, vouts=self.vouts)

    def __str__(self):
        vins_str = reduce(lambda x, y: x + '\t' + str(y) + '\n', self.vins, '')
        vouts_str = reduce(lambda x, y: x + '\t' +
                           str(y) + '\n', self.vouts, '')
        return 'txid: {}\n\t[Vins]\n{}\n\t[Vouts]\n{}'.format(self.txid, vins_str, vouts_str)


class Block:
    def __init__(self,
                 prev_block_hash: str,
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
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.height = height
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce
        self.coinbase = None

    @property
    def block_hash(self):
        # Don't use coinbase to calculate blockhash (since its appended)
        # after mining
        transactions = filter(lambda x: type(
            x) == Transaction, self.transactions)
        txids = reduce(lambda x, y: x + [y.txid], transactions, [])
        vins = reduce(lambda x, y: x + y.vins, transactions, [])
        vouts = reduce(lambda x, y: x + y.vouts, transactions, [])

        return get_hash(
            vins=vins,
            vouts=vouts,
            txids=txids,
            prev_block_hash=self.prev_block_hash,
            height=self.height,
            timestamp=self.timestamp,
            difficulty=self.difficulty,
            nonce=self.nonce
        )

    @property
    def mined(self):
        '''
        Checks if block is mined
        '''
        return self.block_hash[:self.difficulty] == '0' * self.difficulty

    def __str__(self):
        txs_str = reduce(
            lambda x, y: x + '\t' + str(y) + '\n',
            self.transactions, ''
        )

        return ('block_hash: {}\n' +
                'prev_block_hash: {}\n' +
                'height: {}\n' +
                'difficulty: {}\n' +
                'nonce: {}\n' +
                'timestamp: {}\n' +
                '[Coinbase]\n{}\n' +
                '[Transactions]\n{}').format(
            self.block_hash, self.prev_block_hash, self.height,
            self.difficulty, self.nonce, self.timestamp, self.coinbase, txs_str)
