from fastecdsa import keys, curve

from misochain.hashing import sha1


def get_new_priv_key() -> str:
    '''
    Returns a random private key
    '''
    return str(keys.gen_private_key(curve.P256))


def get_pub_key(priv_key: str) -> str:
    '''
    Returns te public key associated with
    the private key. This is used to shorten
    the public key
    '''
    pub_key = keys.get_public_key(int(priv_key), curve.P256)
    return sha1(str(pub_key.x) + str(pub_key.y))
