from typing import List

from misochain.hashing import sha256
from misochain.address import get_new_priv_key, get_pub_key
from misochain.struct import Vin, Vout, Coinbase, Transaction, Block, get_hash

# Private Key to the GenesisBlock's output address is
# 88281420167349101861192746382314614104560710470069537024699432233910802456854
# Address is
# f1325433dd08a4c07d9bf63f9c5c738446bcd33c

# Genesis block
GenesisCoinbase = Coinbase(
    get_hash([], [], 'f1325433dd08a4c07d9bf63f9c5c738446bcd33c', 15),
    [],
    [],
    'f1325433dd08a4c07d9bf63f9c5c738446bcd33c',
    15
)

GenesisBlock: List[Block] = [
    Block(
        get_hash([GenesisCoinbase], [], height=1, difficulty=0, nonce='0'),
        Transaction([GenesisCoinbase], []),
        1,
        0,
        0
    )
]
