import time

from typing import List
from pprint import pprint
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

from misocoin.utils import get_hash, mine_block, create_raw_tx, sign_tx, add_tx_to_block, print_blockchain
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

mined_block, global_utxos = mine_block(
    genesis_block, '461ec74a3ce3ea96267c1b7d043b35004a7058f1', global_utxos
)

global_blockchain.append(mined_block)

# Testing

# New block to house our transactions
new_timestamp = 1512257130
new_block = Block(
    transactions=[],
    prev_block_hash=genesis_block.block_hash,
    height=2,
    timestamp=new_timestamp,
    difficulty=1,
    nonce=1
)

# New transaction
new_tx = create_raw_tx(
    [Vin(mined_block.coinbase.txid, 0)],
    [
        Vout('7b13fb41e910a1b022639f8463ce02596b8c9d4b', 5),
        Vout('461ec74a3ce3ea96267c1b7d043b35004a7058f1', 9)
    ]
)
signed_tx = sign_tx(
    new_tx, 0, '60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed'
)

new_block, global_utxos = add_tx_to_block(signed_tx, new_block, global_utxos)

mined_block, global_utxos = mine_block(
    new_block, '7b13fb41e910a1b022639f8463ce02596b8c9d4b', global_utxos
)

global_blockchain.append(mined_block)

# pprint(mined_block.toJSON())
# print_blockchain(global_blockchain)


@dispatcher.add_method
def get_block(i):
    if (i - 1) < 0 or i > len(global_blockchain):
        return {'error': 'Block not found'}
    return global_blockchain[i - 1].toJSON()


@Request.application
def misocoin_app(request):
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, misocoin_app)
