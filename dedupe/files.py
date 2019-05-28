# import cfgs
import os
import pathlib
import sys

HEADER_SIZE = 0x1000
BLOCK_SIZE = 0x1000

# APP = cfgs.App('swirly-dedupe')

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

EXCLUDED_SUFFIXES = ('.app', '.cc', '.cpp', '.h', '.hh', '.hpp', '.o', '.so')


def accept(f):
    return not (
        f.startswith('.')
        or f in EXCLUDED_FILES
        or any(f.endswith(s) for s in EXCLUDED_SUFFIXES)
    )


def walk(root, accept=accept):
    root = canonical_path(root)
    for dirpath, dirs, filenames in os.walk(root):
        dirs[:] = (d for d in dirs if accept(d))
        dirpath = pathlib.Path(dirpath)
        for filename in filenames:
            if (not accept) or accept(filename):
                yield dirpath / filename


def size(filename):
    return os.path.isfile(filename) and os.stat(filename).st_size or 0


filesize = size


def canonical_path(filename):
    return os.path.abspath(os.path.expanduser(filename))


def block_iterator(filename, block_size=BLOCK_SIZE):
    with open(filename, 'rb') as fp:
        while True:
            buf = fp.read(block_size)
            if buf:
                yield buf
            else:
                return


def header(filename, header_size=HEADER_SIZE):
    return open(filename, 'rb').read(header_size)


if __name__ == '__main__':
    for f in walk(*sys.argv[1:]):
        print(f)
