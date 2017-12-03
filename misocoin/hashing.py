# Converts python's OOP way to a more functional way

import hashlib

from functools import reduce


def shaX(s: str, hashfunc) -> str:
    hash = hashfunc()
    hash.update(s.encode())
    return hash.hexdigest()


def sha256(s: str) -> str:
    return shaX(s, hashlib.sha256)


def sha1(s: str) -> str:
    return shaX(s, hashlib.sha1)


def get_hash(vins=[],
             vouts=[],
             txids=[],
             reward_address='',
             reward_amount='',
             prev_block_hash='',
             height='',
             timestamp='',
             difficulty='',
             nonce='') -> str:
    '''
    Gets the hash given the inputs.

    Union type of str is only there so I can supply
    it an empty string by default

    Params:
        vins:           Total amount of vins
        vouts:          Total amonut of vouts
        reward_address:  Reward address of coinbase
                        (Only for Coinbase/Block type)
        reward_amount:   Reward amout of coinbase
                        (Only for Coinbase/Block type)
        prevBlockHash:  Previous block hash
        height:         Block height (only for Block type)
        difficulty:     Block difficulty (only for Block type)
        nonce:          Block nonce (only for Block type)
    '''
    # Use all of the args
    vins_str = reduce(lambda x, y: x + y.txid + str(y.index), vins, '')
    vouts_str = reduce(
        lambda x, y: x + str(getattr(y, 'address', '')) + str(getattr(y, 'value', '')) +
                        str(getattr(y, 'reward_address', '')) + str(getattr(y, 'reward_amount', '')),
        vouts, ''
    )
    rewards_str = reward_address + str(reward_amount)
    block_str = prev_block_hash + \
        str(height) + str(difficulty) + str(nonce) + str(timestamp)
    tx_str = reduce(lambda x, y: x + y, txids, '')

    # Order and prepend was arbitrarily chosen
    # Done this was so any slight change to the inputs
    # Will result in a huge difference overall
    return sha256(
        'vins_str' + vins_str +
        'rewards_str' + rewards_str +
        'tx_str' + tx_str +
        'block_str' + block_str +
        'vouts_str' + vouts_str
    )
