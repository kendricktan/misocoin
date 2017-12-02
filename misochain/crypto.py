
from fastecdsa import keys, curve

from misochain.hashing import sha1


def get_new_priv_key() -> str:
    '''
    Returns a random private key in hex format
    '''
    return '{:x}'.format(keys.gen_private_key(curve.P256))


def get_pub_key(priv_key: str) -> str:
    '''
    Returns the public key associated with
    the private key. 'x' was chosen randomly
    '''
    pub_key = keys.get_public_key(int(priv_key, 16), curve.P256)
    return '{:x}'.format(pub_key.x) + 'x' + '{:x}'.format(pub_key.y)


def get_address(pub_key: str) -> str:
    '''
    Given the public key, return the address (just SHA1 it
    to shorten it)
    '''
    return sha1(pub_key)


def sign_msg(priv_key: str, msg: str) -> str:
    '''
    Given a message, and the private key,
    return the signature
    '''
    pass
