import hashlib
from . import files

HASHER = hashlib.sha1


def hash_digest(items):
    h = HASHER()
    for i in items:
        h.update(i)
    return h.hexdigest()


def hash_header(filename):
    header = files.header(filename)
    return hash_digest([header])


def hash_file(filename):
    it = files.block_iterator(filename)
    return hash_digest(it)
