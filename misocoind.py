#! /usr/bin/env python

import json
import copy
import sys
import threading
import time
import misocoin.utils as mutils

from functools import reduce, partial
from typing import List, Dict, Tuple
from pprint import pprint
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

from misocoin.hashing import sha256
from misocoin.crypto import get_new_priv_key, get_pub_key, get_address
from misocoin.struct import Vin, Vout, Coinbase, Transaction, Block
from misocoin.sync import misocoin_cli, MisocoinRequestHandler

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

# Our own host and port info
global_host = 'localhost'
global_port = 4000

# global nodes
global_nodes = []

# Global difficulty
global_difficulty = 1

# utxo cache
# is of structure
# utxo[txid][index] = { 'address': address, 'amount': amount, 'spent': None or txid }
global_utxos = {}

# Tx is a dict of all transactions
# that ever took place
global_txs = {}

# blockchain
global_blockchain = {}

# blacklisted nodes
global_blacklisted_nodes = {}

# Genesis block
genesis_epoch = 1512254915
genesis_block = Block(
    prev_block_hash='0000000000000000000000000000000000000000000000000000000000000000',
    transactions=[],
    height=1,
    timestamp=genesis_epoch,
    difficulty=1,
    nonce=0
)

# At init best block will the the genesis_block
global_best_block = genesis_block

# For now we'll just fix their address and private key
account_address = '461ec74a3ce3ea96267c1b7d043b35004a7058f1'
account_priv_key = '60c8cb60c21143fffdd682f399ef3baa4b67c56a1f83a274284cfe7c57e007ed'


def add_to_blockchain(block: Block):
    """
    Helper function to update the blockchain.    

    Also updates the utxo cache and tx cache
    """
    global global_best_block, global_txs, global_utxos, global_difficulty

    # If we don't have the prev block, get it from our nodes
    if (block.height - 1) not in global_blockchain:
        for node in global_nodes:
            try:
                missing_block_dict: Dict = misocoin_cli(
                    'get_block', [block.height - 1], **node)
                missing_block: Block = Block.fromJSON(missing_block_dict)
                add_to_blockchain(missing_block)
                break
            except:
                pass

    # Check block hashes
    if len(global_blockchain) > 0:
        # Check hashes
        if block.prev_block_hash != global_blockchain[block.height - 1].block_hash:
            raise Exception(
                'Block previous hash doesn\'t match')

        if not block.mined:
            raise Exception('Block hasn\'t been mined')

    # Add block to node
    if block.height not in global_blockchain:
        global_blockchain[block.height] = block

        # Add coinbase to cache
        if block.coinbase.txid not in global_txs:
            global_txs[block.coinbase.txid] = block.coinbase

        if block.coinbase.txid not in global_utxos:
            global_utxos[block.coinbase.txid] = {}
            global_utxos[block.coinbase.txid][0] = {
                'address': block.coinbase.reward_address,
                'amount': block.coinbase.reward_amount,
                'spent': None
            }

        # Add tx
        for tx in block.transactions:
            if tx.txid not in global_txs:
                # Update utxos
                global_best_block, global_txs, global_utxos = mutils.add_tx_to_block(
                    tx, global_best_block, global_txs, global_utxos
                )

        # Only ammend global_best_block if the block.height
        # is higher
        if (global_best_block.height < block.height + 1):
            global_best_block = Block(
                prev_block_hash=block.block_hash,
                transactions=[],
                height=block.height + 1,
                timestamp=int(time.time()),
                difficulty=global_difficulty,
                nonce=0
            )

        # Broadcast block
        for node in global_nodes:
            try:
                misocoin_cli('receive_mined_block', [
                             json.dumps(block.toJSON())], **node)
            except:
                pass

        # Auto adjust difficulty ever 10 blocks
        # Should be around 300 seconds after 10 blocks
        last_ten_blocks = []
        for i in range(max(1, global_best_block.height - 10), global_best_block.height - 1):
            if i in global_blockchain:
                last_ten_blocks.append(global_blockchain[i])

        if (len(global_blockchain) % 10 == 0):
            lowest_timestamp = reduce(lambda x, y: min(
                x, y.timestamp), last_ten_blocks, int(time.time()))
            highest_timestamp = reduce(lambda x, y: max(
                x, y.timestamp), last_ten_blocks, genesis_epoch)
            
            if (highest_timestamp - lowest_timestamp < 300):
                global_difficulty = min(global_difficulty + 1, 64)

            if (highest_timestamp - lowest_timestamp > 300):
                global_difficulty = max(global_difficulty - 1, 1)

            print('[UPDATE] Difficulty adjusted to {}'.format(global_difficulty))

        print('[INFO] Received mined block {}'.format(block.height))


def mine_block(block: Block, address: str):
    '''
    Mines a block and returns its mined hash
    '''
    global global_best_block

    # Oh wow state mutation :(
    # Too pleb to do this in a pure way
    while True:
        global_best_block.nonce += 1

        if global_best_block.mined:
            # Find fees in the block
            fees = reduce(lambda x, y: x + mutils.get_fees(y, global_utxos),
                          global_best_block.transactions, 0)
            reward_amount = 15 + fees

            # Reward miner who found the right nonce
            # With 15 misocoin + fees in the block
            coinbase = Coinbase(
                global_best_block.prev_block_hash, address, reward_amount
            )
            global_best_block.coinbase = coinbase

            # Add coinbase to utxo and txs
            # Coinbase's vout will only contain
            # 1 item
            global_utxos[coinbase.txid] = {}
            global_utxos[coinbase.txid][0] = {
                'address': address,
                'amount': reward_amount,
                'spent': None
            }
            global_txs[coinbase.txid] = coinbase

            # Add to blockchain
            mined_block = copy.deepcopy(global_best_block)
            add_to_blockchain(mined_block)
            return mined_block


@dispatcher.add_method
def get_balance():
    global global_utxos

    total = 0
    for txid in global_utxos:
        for index in global_utxos[txid]:
            if global_utxos[txid][index]['address'] == account_address:
                if global_utxos[txid][index]['spent'] is None:
                    total += global_utxos[txid][index]['amount']

    return {'address': account_address, 'amount': total}


@dispatcher.add_method
def send_misocoin(to_address: str, amount: int):
    global global_utxos
    # I know this is slow in recovering the utxos, but ceebs
    try:
        accumulated_amount = 0
        send_amount = int(amount)

        vins: List[Vin] = []
        vouts: List[Vout] = [Vout(to_address, send_amount)]

        # Construct vins and vouts
        for txid in global_utxos:
            for index in global_utxos[txid]:
                if global_utxos[txid][index]['address'] == account_address:
                    if global_utxos[txid][index]['spent'] is None:
                        accumulated_amount += global_utxos[txid][index]['amount']
                        vins.append(Vin(txid, index))

                        if (accumulated_amount >= send_amount):
                            break

            if (accumulated_amount >= send_amount):
                break

        if (accumulated_amount < send_amount):
            return {'error': 'You\'re trying to send {} misocoin when you have {} misocoin'.format(send_amount, accumulated_amount)}

        # Send remaining to self
        if (accumulated_amount > send_amount):
            vouts.append(
                Vout(account_address, accumulated_amount - send_amount))

        # Create tx object and sign it
        tx = Transaction(vins, vouts)

        for i in range(len(tx.vins)):
            tx = mutils.sign_tx(tx, i, account_priv_key)

        # Send raw tx and return the txid
        return send_raw_tx(json.dumps(tx.toJSON()))

    except Exception as e:
        return {'error': str(e)}


@dispatcher.add_method
def get_info():
    return {
        'height': len(global_blockchain),
        'connections': len(global_nodes),
        'difficulty': global_difficulty
    }


@dispatcher.add_method
def get_best_block():
    return global_best_block.toJSON()


@dispatcher.add_method
def get_block(i: int):
    try:
        return global_blockchain[int(i)].toJSON()

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
        # Original tx
        _tx_og = copy.deepcopy(tx)

        # Create new tx from the json dump
        tx = Transaction.fromJSON(json.loads(tx))

        # If is new tx then add it to block
        if tx.txid not in global_txs:
            # Add tx to global best block
            global_best_block, global_txs, global_utxos = mutils.add_tx_to_block(
                tx, global_best_block, global_txs, global_utxos
            )

            print('[INFO] txid {} added to block {}'.format(
                tx.txid, global_best_block.height))

            # Broadcast transaction to connected nodes
            for node in global_nodes:
                try:
                    misocoin_cli('send_raw_tx', [
                                 json.dumps(tx.toJSON())], **node)
                except Exception as e:
                    pass

        return {'txid': tx.txid}

    except Exception as e:
        return {'error': str(e)}


@dispatcher.add_method
def receive_mined_block(block_str: str):
    global global_best_block, global_blockchain

    try:
        block: Block = Block.fromJSON(json.loads(block_str))
        add_to_blockchain(block)
        return {'success': True}

    except Exception as e:
        return {'error': str(e)}


@Request.application
def misocoin_app(request):
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


# Block management
# Handles the mining of blocks, as well as the automatic adjusting of difficulty
def block_management():
    global global_best_block, global_blockchain, global_txs, global_utxos, global_difficulty

    while True:
        time.sleep(10)

        try:
            last_mined_time = global_blockchain[-1].timestamp
        except:
            last_mined_time = genesis_epoch

        # Auto mine
        # if 30 seconds has passed since last mining
        if (time.time() - last_mined_time > 30):
            # Mine block
            mined_block = mine_block(global_best_block, account_address)

            if (mined_block.coinbase.reward_address == account_address):
                print('[SUCCESS] You found the nonce for block {}'.format(
                    mined_block.height))

            # Broadcast block to nodes
            mined_block_str = json.dumps(mined_block.toJSON())
            for node in global_nodes:
                # If node['host'] is in black list then continue
                if node['host'] in global_blacklisted_nodes:
                    continue

                try:
                    misocoin_cli('receive_mined_block', [
                                 mined_block_str], **node)

                except:
                    pass


@dispatcher.add_method
def init_connection(host, port):
    global global_nodes

    # Check if we already have the node,
    # add it if we dont
    has_node = reduce(lambda x, y: x and (
        y['host'] == host), global_nodes, False)
    if not has_node:
        global_nodes.append({'host': host, 'port': port})
    return json.dumps(global_nodes)


def sync_with_nodes():
    '''
    Syncs blocks with node
    '''
    global global_nodes

    # Init connection
    for node in global_nodes:
        try:
            misocoin_cli('init_connection', [global_host, global_port], **node)
        except:
            pass

    # Checks every 15 seconds
    while True:
        # Checks with nodes, syncs with the one with
        # the longest chain
        longest_node = None
        best_height = len(global_blockchain)

        for node in global_nodes:
            # If node['host'] is in black list then continue
            if node['host'] in global_blacklisted_nodes:
                continue

            try:
                node_best_length = misocoin_cli(
                    'get_info', [], **node)['height']

                if node_best_length > best_height:
                    longest_node = node
                    best_height = node_best_length

            except:
                pass

        # Syncs with that node
        if longest_node is not None:
            latest_block_dict: Dict = misocoin_cli(
                'get_block', [best_height], **longest_node)
            latest_block: Block = Block.fromJSON(latest_block_dict)

            # Append to latest blockchain
            add_to_blockchain(latest_block)

        time.sleep(10)


def run_misocoin(host='localhost', port=4000, nodes=['localhost:4000'], **kwargs):
    t1 = threading.Thread(target=partial(
        run_simple, threaded=True, request_handler=MisocoinRequestHandler), args=(host, port, misocoin_app))
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=sync_with_nodes, args=())
    t2.start()

    t3 = threading.Thread(target=block_management, args=())
    t3.start()

    t1.join()
    t2.join()
    t3.join()


if __name__ == '__main__':
    config = list(filter(lambda x: x[0] is '-', sys.argv[1:]))
    config_kwargs = reduce(lambda x, y: {y.split(
        '=')[0][1:]: y.split('=')[1], **x}, config, {})

    # global host and port
    global_host = config_kwargs.get('host', global_host)
    global_port = config_kwargs.get('port', global_port)

    # Get global node and filter out useless values and
    # mush it into the format we want
    global_nodes = config_kwargs.get('nodes', '').split(',')
    global_nodes = list(
        filter(lambda x: (len(x) > 0 and ':' in x and x is not (global_host + ':' + str(global_port))), global_nodes))
    global_nodes = list(map(lambda x: {'host': x.split(
        ':')[0], 'port': x.split(':')[1]}, global_nodes))

    # account private key
    account_priv_key = config_kwargs.get('priv_key', account_priv_key)
    account_address = get_address(get_pub_key(account_priv_key))

    run_misocoin(**config_kwargs)
