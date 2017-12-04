import json
import time
import misocoin.utils as mutils

from typing import List
from pprint import pprint
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

from misocoin.hashing import sha256
from misocoin.crypto import get_new_priv_key, get_pub_key
from misocoin.struct import Vin, Vout, Coinbase, Transaction, Block

# Private Key to the genesis_block's output address is
# sha256('miso is a good boy')
# which is
# 60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed
# Address is
# 461ec74a3ce3ea96267c1b7d043b35004a7058f1

# 2nd private key
# sha256('miso is a happy boy')
# which is
# c551a109f752cf7ae8b3e2c8f33349c8840cf9bfc86cf05863dad0bb8a626667
# Address is
# 7b13fb41e910a1b022639f8463ce02596b8c9d4b

# 3rd private key
# sha256('miso says meow')
# b1020620ab7e2bdf59c252d55bb105917396decf73e8a30f92d324fefbd6e521
# Address is
# 3fa99d6a624547040b10012127e10fa67f2be667

# utxo cache
# is of structure
# utxo[txid][index] = { 'address': address, 'amount': amount, 'spent': None or txid }
global_utxos = {}

# Tx is a dict of all transactions
# that ever took place
global_txs = {}

# best block
global_best_block = None

# blockchain
global_blockchain = []

# Genesis block
genesis_epoch = 1512254915
genesis_block = Block(
    transactions=[],
    prev_block_hash='0000000000000000000000000000000000000000000000000000000000000000',
    height=1,
    timestamp=genesis_epoch,
    difficulty=1,
    nonce=0
)


@dispatcher.add_method
def get_info():
    return {
        'blocks': len(global_blockchain)
    }


@dispatcher.add_method
def get_best_block_hash():
    return {
        'hash': global_blockchain[-1].block_hash
    }


@dispatcher.add_method
def get_block(i: int):
    try:
        i = int(i)
        if (i - 1) > 0 and i < len(global_blockchain):
            return global_blockchain[i - 1].toJSON()

    except Exception as e:
        return {'error': str(e)}
    return {'error': 'Block not found'}


@dispatcher.add_method
def create_raw_tx(vins, vouts):
    try:
        vins = json.loads(vins)
        vouts = json.loads(vouts)
        return Transaction.fromJSON({'vins': vins, 'vouts': vouts}).toJSON()

    except Exception as e:
        return {'error': str(e)}


@dispatcher.add_method
def sign_raw_tx(tx: str, idx: int, pk: str):
    try:
        idx = int(idx)
        tx = Transaction.fromJSON(json.loads(tx))
        signed_tx = mutils.sign_tx(tx, idx, pk)
        return signed_tx.toJSON()

    except Exception as e:
        return {'error': str(e)}


@dispatcher.add_method
def get_tx(txid: str):
    txid = str(txid)
    if txid in global_txs:
        return global_txs[txid].toJSON()
    return {'error': 'txid not found'}


@dispatcher.add_method
def send_raw_tx(tx: str):
    global global_best_block, global_txs, global_utxos
    try:
        tx = Transaction.fromJSON(json.loads(tx))
        global_best_block, global_txs, global_utxos = mutils.add_tx_to_block(
            tx, global_best_block, global_txs, global_utxos
        )

        # TODO: Broadcast transaction to connected nodes
        return {'txid': tx.txid}

    except Exception as e:
        return {'error': str(e)}


@Request.application
def misocoin_app(request):
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, misocoin_app)
