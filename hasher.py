import files, hashlib, itertools

HASHER = hashlib.sha1
HEADER_SIZE = 512
BLOCKSIZE = 0x1000


def hash_digest(items):
    h = HASHER()
    for i in items:
        h.update(i)
    return h.hexdigest()


def hash_header_with_size(filename):
    filesize = files.filesize(filename)
    filesize_string = str(filesize).encode()

    header = files.header(filename, HEADER_SIZE)
    digest = hash_digest([filesize_string, header])
    return filesize, digest


def hash_file(filename):
    it = files.block_iterator(filename, BLOCKSIZE)
    return hash_digest(it)
