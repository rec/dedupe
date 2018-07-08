import os, sys

EXCLUDED_FILES = {
    'Applications',
    'Backups.backupdb',
    'Library',
    'Network',
    'System',
    'User Information',
    'Volumes',
    'bin',
    'cores',
    'dev',
    'development',
    'etc',
    'home',
    'installer.failurerequests',
    'net',
    'opt',
    'private',
    'sbin',
    'tmp',
    'usr',
    'var',

    '__pycache__',
    'Shared',
}


def accept(f):
    return not (f.startswith('.') or f.endswith('.app') or f in EXCLUDED_FILES)


def walk(root, accept=accept):  # lambda f: True):
    for dirpath, dirs, filenames in os.walk(root):
        if accept:
            dirs[:] = filter(accept, dirs)
        for filename in filter(accept, filenames):
            yield os.path.join(dirpath, filename)


def filesize(filename):
    return os.path.isfile(filename) and os.stat(filename).st_size


def canonical_path(filename):
    return os.path.abspath(os.path.expanduser(filename))


def block_iterator(filename, blocksize):
    with open(filename, 'rb') as fp:
        while True:
            buf = fp.read(blocksize)
            if buf:
                yield buf
            else:
                return

def header(filename, size):
    return open(filename, 'rb').read(size)


DATA_DIR = canonical_path('~/.swirly_dedupe')
SIZE_AND_HEADER_DIR = os.path.join(DATA_DIR, 'size_and_header')

if __name__ == '__main__':
    for f in walk(*sys.argv[1:]):
        print(f)
