from typing import List

from misochain.utils import get_hash, mine_block
from misochain.hashing import sha256
from misochain.address import get_new_priv_key, get_pub_key
from misochain.struct import Vin, Vout, Coinbase, Transaction, Block

# Private Key to the GenesisBlock's output address is
# 88281420167349101861192746382314614104560710470069537024699432233910802456854
# Address is
# f1325433dd08a4c07d9bf63f9c5c738446bcd33c

# Genesis block
GenesisCoinbase = Coinbase(
    get_hash(reward_address='f1325433dd08a4c07d9bf63f9c5c738446bcd33c',
             reward_amount=15),
    [],
    [],
    'f1325433dd08a4c07d9bf63f9c5c738446bcd33c',
    15
)

GenesisBlock: List[Block] = [
    Block(
        get_hash(vins=[GenesisCoinbase], height=1, difficulty=0, nonce='0'),
        [Transaction(get_hash(vins=[GenesisCoinbase]), [GenesisCoinbase], [])],
        1,
        0,
        0
    )
]

newBlock = Block(
    get_hash(vins=[GenesisCoinbase], height=1, difficulty=0, nonce=0),
    [Transaction(get_hash(vins=[GenesisCoinbase]), [GenesisCoinbase], [])],
    height=2,
    difficulty=1,
    nonce=-1
)

mine_block(newBlock, GenesisBlock[-1].block_hash)
