import copy
import time

from typing import List, Union, Dict, Tuple
from functools import reduce

from misocoin.crypto import get_pub_key, sign_msg, is_sig_valid, get_address
from misocoin.struct import Block, Transaction, Vin, Vout, Coinbase
from misocoin.hashing import sha256, get_hash


def mine_block(block: Block, address: str, utxos: Dict) -> Tuple[Block, Dict]:
    '''
    Mines a block and returns its mined hash
    '''
    _block = copy.deepcopy(block)
    _utxos = copy.deepcopy(utxos)

    # Oh wow state mutation :(
    # Too pleb to do this in a pure way
    while True:
        _block.nonce += 1

        if _block.mined:
            # Find fees in the block
            fees = reduce(lambda x, y: x + get_fees(y, _utxos),
                          _block.transactions, 0)
            reward_amount = 15 + fees

            # Reward miner who found the right nonce
            # With 15 misocoin + fees in the block
            coinbase = Coinbase(
                _block.prev_block_hash, address, reward_amount
            )

            _block.coinbase = coinbase

            # Add coinbase to utxo
            # Coinbase's vout will only contain
            # 1 item
            _utxos[coinbase.txid] = {}
            _utxos[coinbase.txid][0] = {
                'address': address,
                'amount': reward_amount,
                'spent': None
            }

            return _block, _utxos


def create_raw_tx(vins: List[Vin], vouts: List[Vout]) -> Transaction:
    '''
    Creates a new transaction object given
    a list of ins and outs
    '''
    return Transaction(vins, vouts)


def sign_tx(tx: Transaction, idx: int, priv_key: str) -> Transaction:
    '''
    Signs the transaction

    Params:
        tx: Transaction object to be signed
        idx: Index of the vin to sign
        priv_key: private key used to prove that you authorized it
    '''
    # Make a copy so we don't overwrite the original object
    _tx = copy.deepcopy(tx)

    # When we're signing, null out all the vins
    # Except for ours when hashing
    vin = _tx.vins[idx]
    vouts = _tx.vouts
    txid = _tx.txid

    # Message for the signature is the hash of the transaction
    # with all vins nulled except for the one we're signing
    tx_hash = get_hash(vins=[vin], vouts=vouts, txids=[txid])

    pub_key = get_pub_key(priv_key)
    signature = sign_msg(tx_hash, priv_key)

    vin.signature = signature
    vin.pub_key = pub_key

    # Rebuild vins
    vins = _tx.vins
    vins[idx] = vin

    return Transaction(vins, vouts)


def get_fees(tx: Transaction, utxos: Dict) -> int:
    '''
    Gets the fees inside a transaction
    '''
    total_in = reduce(
        lambda x, y: x + utxos[y.txid][y.index]['amount'], tx.vins, 0)
    total_out = reduce(lambda x, y: x + y.amount, tx.vouts, 0)
    return (total_in - total_out)


def add_tx_to_block(tx: Transaction,
                    block: Block,
                    utxos: Dict) -> Tuple[Block, Dict]:
    '''
    Adds the tx to the to the blockchain and broadcasts it to
    connected nodes. 

    Updates and maintains the global cache of utxos. This is also used
    to check for double spending
    '''
    # Make copy of object
    _block = copy.deepcopy(block)
    _tx = copy.deepcopy(tx)
    _utxos = copy.deepcopy(utxos)

    # Can't send more than you received
    if (get_fees(_tx, _utxos) < 0):
        raise Exception('Attempting to spend more than you have!')

    # Update utxo cache
    # Whilst checking signature validity
    for idx, vout in enumerate(_tx.vouts):
        if _tx.txid not in _utxos:
            _utxos[_tx.txid] = {}

        _utxos[_tx.txid][idx] = {
            'address': vout.address,
            'amount': vout.amount,
            'spent': None
        }

    for vin in _tx.vins:
        if (vin.txid in _utxos) and (vin.index in _utxos[vin.txid]):
            if _utxos[vin.txid][vin.index]['spent'] is None:
                # Check if the address in the utxos[tx.txid] is the same as the public key
                # If it doesn't exist in the utxos, we're trying to double spend
                # If the vout address in the utxos doesn't match the private key
                # Then we're not authorized to spend this transaction

                # Check the signature
                try:
                    tx_hash = get_hash(
                        vins=[vin], vouts=_tx.vouts, txids=[_tx.txid])

                    same_address = get_address(
                        vin.pub_key) == _utxos[vin.txid][vin.index]['address']
                    valid_sig = is_sig_valid(
                        vin.signature, vin.pub_key, tx_hash)
                except:
                    raise Exception(
                        'Corrupted pub_key/signature for vin\n{}'.format(vin))

                if not (same_address and valid_sig):
                    raise Exception('You don\'t have the credentials to authorize this transaction:\n\t{}'.format(
                        vin
                    ))

                # Mark it as spent
                _utxos[vin.txid][vin.index]['spent'] = _tx.txid

            else:
                raise Exception(
                    'Transaction {} at vin {} has been spent'.format(vin.txid, vin.index))

        else:
            raise Exception('Transaction {} does not exist'.format(vin.txid))

    # Wow state mutations
    _block.transactions = _block.transactions + [_tx]
    return _block, _utxos


def print_blockchain(blockchain: List[Block]):
    for idx, b in enumerate(blockchain):
        print('--- Block {} ---'.format(idx + 1))
        print(b)
