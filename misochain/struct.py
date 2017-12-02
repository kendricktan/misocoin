# Here we define the structure of our object

from functools import reduce
from typing import List, Union, Dict

from misochain.hashing import sha256


class Vin:
    def __init__(self, txid: str, index: int):
        '''
        txid:  The transaction id               
        index: Index of the vout in the list of transactions               
        '''
        self.txid = txid
        self.index = index


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

    def __init__(self, txid: str, vins: [Vin], vouts: [Vout], rewardAddress: str, rewardAmount: int):
        '''
        txid:          Txid of the Coinbase transaction
        vins:          All vins inside the block
        vouts:         All vouts inside the block
        rewardAddress: Address of miner who found the solution to block
        rewardAmount:  Amount rewarded
        '''
        self.txid = txid
        self.vins = vins
        self.vouts = vouts
        self.rewardAddress = rewardAddress
        self.rewardAmount = rewardAmount


class Transaction:
    def __init__(self, vins: List[Union[Coinbase, Vin]], vouts: List[Vout]):
        '''
        vins:  List of inputs (where we our money is supplied from)
               Note: First item in array will always be a coinbase
        vouts: List of outputs (where our supplied money is going to go)
        '''
        self.vins = vins
        self.vouts = vouts


class Block:
    def __init__(self,
                 blockHash: str,
                 transactions: List[Transaction],
                 height: int,
                 difficulty: int,
                 nonce: str):
        '''
        blockHash: Hash of the block
        transactions: Transactions in our blockchain
        height:  Current block height
        '''
        self.blockHash = blockHash
        self.transactions = transactions
        self.height = height
        self.difficulty = difficulty
        self.nonce = nonce


def get_hash(vins: List[Vin],
            vouts: List[Vout],
            rewardAddress: str = '',
            rewardAmount: Union[str, int] = '',
            height: Union[str, int] = '',
            difficulty: Union[str, int] = '',
            nonce: Union[str, int] = '') -> str:
    '''
    Gets the hash given the inputs.

    Union type of str is only there so I can supply
    it an empty string by default

    Params:
        vins:           Total amount of vins
        vouts:          Total amonut of vouts
        rewardAddress:  Reward address of coinbase
                        (Only for Coinbase/Block type)
        rewardAmount:   Reward amout of coinbase
                        (Only for Coinbase/Block type)
        height:         Block height (only for Block type)
        difficulty:     Block difficulty (only for Block type)
        nonce:          Block nonce (only for Block type)
    '''
    # Use the of all pass vins, vouts,
    vins_str = reduce(lambda x, y: x + y.txid + str(getattr(y, 'index', '')), vins, '')
    vouts_str = reduce(lambda x, y: x + y.address + str(y.value), vouts, '')
    rewards_str = rewardAddress + str(rewardAmount)
    block_str = str(height) + str(difficulty) + str(nonce)

    # Order was arbitrarily chosen
    return sha256(vins_str + rewards_str + block_str + vouts_str)
