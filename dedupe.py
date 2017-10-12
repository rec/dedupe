import argparse, hashlib, json, os, re, sys

"""
Needs to work on up to 500,000 files.

With the current
"""


class Hasher:
    BLOCK_SIZE = 0x100000
    HEADER_SIZE = 0x1000
    HASHER = hashlib.sha1

    @staticmethod
    def filesize(cls, filename):
        return os.stat(filename).st_size

    @classmethod
    def header(cls, filename):
        hasher = cls.HASHER()
        with open(filename, 'rb') as fp:
            buf = fp.read(cls.HEADER_SIZE)
            if buf:
                hasher.update(buf)
                return hasher.hexdigest()

    @classmethod
    def contents(filename):
        hasher = hashlib.sha1()
        with open(filename, 'rb') as fp:
            empty = True
            while True:
                buf = fp.read(cls.BLOCK_SIZE)
                if not buf:
                    return not empty and hasher.hexdigest()
                empty = False
                hasher.update(buf)


def canonical_path(filename):
    return os.path.abspath(os.path.expanduser(filename))


class HashCollection:
    def __init__(self, verbose, datafile):
        def object_hook(x):
            return set(x) if isinstance(x, list) else x

        self.exclude = re.compile(exclude).match if exclude else lambda x: False
        self.verbose = verbose
        self.failures = 0
        self.datafile = canonical_path(datafile)

        try:
            fp = open(self.datafile)
        except:
            print('Starting new datafile', self.datafile)
            self.hashes = {}
        else:
            with fp:
                return json.load(fp, object_hook=object_hook)

    def write(self):
        def default(o):
            try:
                return list(o)
            except:
                raise TypeError

        with open(self.datafile, 'w') as fp:
            return json.dump(obj, fp, default=default)

    def add(self, filename, hasher):
        hasher_function = getattr(Hasher, hasher)
        try:
            key = hasher_function(filename)
        except:
            self.failures += 1
            return

        if key:
            hasher_dict = self.hashes.setdefault(hasher, {})
            hash_entries = hasher_dict.setdefault(key, set())
            hash_entries.add(filename)
            if self.verbose:
                print(filename)

    def add_files(self, *roots, exclude=None):
        for root in roots:
            for dirpath, _, filenames in os.walk(root):
                for relative_filename in filenames:
                    filename = os.path.join(dirpath, relative_filename)
                    if not (exclude and exclude(filename)):
                        add(filename, 'filesize')

    def refine(self, before, after):
        for bucket in self.hashes[before].values():
            if len(bucket) > 1:
                for f in bucket:
                    add(f, after)


ADD_HELP = 'A comma-separated list of file roots to add'
DATAFILE = '~/.swirly_dedupe.json'


def dedupe(args):
    hc = HashCollection(args.verbose, args.datafile)
    if args.add:
        args.verbose and print('Adding roots:', *args.add)
        hc.add_files(*args.split(':'), exclude=args.exclude)

    if args.header:
        pass

def parse_argv(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', help=ADD_HELP, default=None)
    parser.add_argument('--header', help=HEADER_HELP, action='store_true')
    parser.add_argument('--full', help=FULL_HELP, action='store_true')
    parser.add_argument(
        '--verbose', help='Print each file', action='store_true')
    parser.add_argument(
        '--datafile', help='Name of datafile', default=DATAFILE):
    parser.add_argument(
        '--exclude', help=HEADER_HELP, default=None)

    return parser.parse_args(argv)


if __name__ == '__main__':
    parse_arg(sys.argv[1:])
