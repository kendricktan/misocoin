# Here we define the structure of our object
import json

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
        return json.dumps(self.toJSON())

    @classmethod
    def fromJSON(cls, vin_json: Dict):        
        if 'txid' not in vin_json or 'index' not in vin_json:
            raise Exception('Vin missing txid/index, {}'.format(vin_json))

        vin = cls(vin_json['txid'], vin_json['index'])
        vin.pub_key = getattr(vin_json, 'pub_key', None)
        vin.signature = getattr(vin_json, 'signature', None)

        return vin

    def toJSON(self):
        return {
            'txid': self.txid,
            'index': self.index,
            'pub_key': self.pub_key,
            'signature': self.signature
        }


class Vout:
    def __init__(self, address: str, amount: int):
        '''
        address: Which address are we paying?
        amount:   How much are we paying?
        '''
        self.address = address
        self.amount = amount

    def __str__(self):
        return json.dumps(self.toJSON())

    @classmethod
    def fromJSON(cls, vout_json: Dict):        
        if 'address' not in vout_json or 'amount' not in vout_json:
            raise Exception('Vout missing txid/index: {}'.format(vout_json))

        return cls(vout_json['address'], vout_json['amount'])

    def toJSON(self):
        return {
            'address': self.address,
            'amount': self.amount
        }


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
        return json.dumps(self.toJSON())

    @classmethod
    def fromJSON(cls, coinbase_json: Dict):
        if 'prev_block_hash' not in coinbase_json or 'reward_address' not in coinbase_json \
                or 'reward_amount' not in coinbase_json:
            raise Exception(
                'Coinbase missing inputs: {}'.format(coinbase_json))

        return cls(
            coinbase_json['prev_block_hash'],
            coinbase_json['reward_address'],
            coinbase_json['reward_amount']
        )

    def toJSON(self):
        return {
            'txid': self.txid,
            'reward_address': self.reward_address,
            'reward_amount': self.reward_amount
        }


class Transaction:
    def __init__(self, vins: List[Vin], vouts: List[Vout]):
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
        return json.dumps(self.toJSON())

    @classmethod
    def fromJSON(cls, vins: List[Dict], vouts: List[Dict]):
        pass

    @classmethod
    def fromJSON(cls, tx_json: Dict):        
        if 'vins' not in tx_json or 'vouts' not in tx_json:
            raise Exception('Transaction missing inputs: {}'.format(tx_json))

        vins = list(map(Vin.fromJSON, tx_json['vins']))
        vouts = list(map(Vout.fromJSON, tx_json['vouts']))

        return cls(vins, vouts)

    def toJSON(self):
        vins_json = reduce(lambda x, y: x + [y.toJSON()], self.vins, [])
        vouts_json = reduce(lambda x, y: x + [y.toJSON()], self.vouts, [])

        return {
            'txid': self.txid,
            'vins': vins_json,
            'vouts': vouts_json,
        }


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
        return json.dumps(self.toJSON())

    @classmethod
    def fromJSON(cls, block_json: Dict):
        if 'block_hash' not in block_json or 'prev_block_hash' not in block_json \
                or 'height' not in block_json or 'difficulty' not in block_json \
                or 'nonce' not in block_json or 'timestamp' not in block_json \
                or 'coinbase' not in block_json or 'transactions' not in block_json:
            raise Exception('Block missing inputs: {}'.format(block_json))        
        coinbase = None
        transactions = list(
            map(Transaction.fromJSON, block_json['transactions']))

        if block_json['coinbase'] is not None:
            coinbase = Coinbase.fromJSON(block_json['coinbase'])

        block = cls(
            block_json['prev_block_hash'],
            transactions,
            block_json['height'],
            block_json['timestamp'],
            block_json['difficulty'],
            block_json['nonce']
        )
        block.coinbase = coinbase
        return block

    def toJSON(self):
        transactions = list(map(lambda x: x.toJSON(), self.transactions))
        return {
            'block_hash': self.block_hash,
            'prev_block_hash': self.prev_block_hash,
            'height': self.height,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'coinbase': self.coinbase.toJSON(),
            'transactions': transactions
        }
