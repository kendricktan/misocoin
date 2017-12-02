# Converts python's OOP way to a more functional way

import hashlib


def shaX(s: str, hashfunc) -> str:
    hash = hashfunc()
    hash.update(s.encode())
    return hash.hexdigest()


def sha256(s: str) -> str:
    return shaX(s, hashlib.sha256)


def sha1(s: str) -> str:
    return shaX(s, hashlib.sha1)
