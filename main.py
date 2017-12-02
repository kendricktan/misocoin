import time

from typing import List

from misochain.utils import get_hash, mine_block
from misochain.hashing import sha256
from misochain.crypto import get_new_priv_key, get_pub_key
from misochain.struct import Vin, Vout, Coinbase, Transaction, Block

# Private Key to the GenesisBlock's output address is
# 893cdf5921a0cd49b4c1f4b69907d8b3ae20dd7ca6d9328f66078ff1f2ede594
# Address is
# 9274249f8d4d98270602358b75263967502fbd39

# Genesis block
GenesisCoinbase = Coinbase(
    get_hash(reward_address='9274249f8d4d98270602358b75263967502fbd39',
             reward_amount=15),
    [],
    [],
    '9274249f8d4d98270602358b75263967502fbd39',
    15
)

GenesisBlock: List[Block] = [
    Block(
        get_hash(vins=[GenesisCoinbase], height=1, difficulty=0, nonce='0'),
        [Transaction(get_hash(vins=[GenesisCoinbase]), [GenesisCoinbase], [])],
        1,
        int(time.time()),
        0,
        0
    )
]

newBlock = Block(
    get_hash(vins=[GenesisCoinbase], height=1, difficulty=0, nonce=0),
    [Transaction(get_hash(vins=[GenesisCoinbase]), [GenesisCoinbase], [])],
    height=2,
    timestamp=int(time.time()),
    difficulty=1,
    nonce=-1
)

print(mine_block(newBlock, GenesisBlock[-1].block_hash))
