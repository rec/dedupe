import argparse, hashlib, json, os, re, sys

"""
Needs to work on up to 500,000 files with an average pathlength of 100 = 50 MB

filesize.json:
   {filename: {filesize: set(dirpath)}

header.json:
   {filename: {header_hash: set(dirpath)}

contents.json:
   {filename: {contents_hash: set(dirpath)}

"""


class Hasher:
    HEADER_SIZE = 0x1000
    CONTENTS_SIZE = 0x100000
    HASHER = hashlib.sha1

    @classmethod
    def _hash(cls, filename, blocksize):
        hasher = cls.HASHER()
        with open(filename, 'rb') as fp:
            buf = fp.read(blocksize)
            if buf:
                hasher.update(buf)
                return hasher.hexdigest()

    @staticmethod
    def filesize(filename):
        return os.path.isfile(filename) and os.stat(filename).st_size

    @classmethod
    def header(cls, filename):
        return cls._hash(filename, cls.HEADER_SIZE)

    @classmethod
    def contents(cls, filename):
        return cls._hash(filename, cls.CONTENTS_SIZE)


def canonical_path(filename):
    return os.path.abspath(os.path.expanduser(filename))


class HashCollection:
    def __init__(self, verbose, data, clear):
        self.verbose = verbose
        self.failures = 0
        self.data = canonical_path(data)
        self.clear = clear
        os.makedirs(self.data, exist_ok=True)

    def filename(self, strategy):
        return os.path.join(self.data, strategy + '.json')

    def read(self, strategy):
        filename = self.filename(strategy)
        if self.clear:
            print('Starting new datafile', filename)
            return {}

        def object_hook(x):
            return set(x) if isinstance(x, list) else x

        try:
            fp = open(filename)
        except:
            print('Starting new datafile', filename)
            return {}
        else:
            with fp:
                return json.load(fp, object_hook=object_hook)

    def write(self, obj, strategy):
        def default(o):
            try:
                return list(o)
            except:
                raise TypeError

        with open(self.filename(strategy), 'w') as fp:
            return json.dump(obj, fp, default=default)

    def add(self, hasher, dirpath, filename, table):
        entry = table.setdefault(filename, {})
        if any(dirpath in i for i in entry.values()):
            return 0

        hasher_function = getattr(Hasher, hasher)
        fullname = os.path.join(dirpath, filename)
        try:
            key = hasher_function(fullname)
        except Exception as e:
            print('ERROR', e, 'in dir', dirpath, 'file', filename,
                  file=sys.stderr)
            self.failures += 1
            return 0

        if not key:
            return 0

        entry.setdefault(key, set()).add(dirpath)
        if self.verbose:
            print(os.path.join(dirpath, filename))
        return 1

    def add_files(self, *roots, exclude=None):
        table = self.read('filesize')
        items = 0

        for root in roots:
            for dirpath, dirs, filenames in os.walk(root):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for filename in filenames:
                    if not (filename.startswith('.') or
                            exclude and exclude(filename)):
                        items += self.add('filesize', dirpath, filename, table)

        self.write(table, 'filesize')
        print(items, ' files', 's' if items == 1 else '', ' added.', sep='')

    def refine(self, before, after):
        after_table = self.read(after)
        items = 0

        for filename, entry in self.read(before).items():
            for key, bucket in entry.items():
                if len(bucket) > 1:
                    for dirpath in bucket:
                        items += self.add(after, dirpath, filename, after_table)

        self.write(after_table, after)
        print(items, ' file', 's' if items == 1 else '', ' added.', sep='')


ADD_HELP = 'A comma-separated list of file roots to add'
HEADER_HELP = 'Compute file headers hashes from sizes'
CONTENTS_HELP = 'Compute contents hashes headers from header hashes'
DATA_DIR = '~/.swirly_dedupe'


def dedupe(args):
    hc = HashCollection(args.verbose, args.data, args.clear)
    if args.add:
        args.verbose and print('Adding roots:', args.add)
        exclude = args.exclude and re.compile(args.exclude).match
        hc.add_files(*args.add.split(':'), exclude=exclude)

    if args.header:
        hc.refine('filesize', 'header')

    if args.contents:
        hc.refine('header', 'contents')

    print('Failures:', hc.failures)


def parse_arg(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', help=ADD_HELP, default=None)
    parser.add_argument('--header', help=HEADER_HELP, action='store_true')
    parser.add_argument('--contents', help=CONTENTS_HELP, action='store_true')
    parser.add_argument(
        '--verbose', help='Print each file', action='store_true')
    parser.add_argument(
        '--data', help='Name of data directory', default=DATA_DIR)
    parser.add_argument(
        '--exclude', help=HEADER_HELP, default=None)
    parser.add_argument(
        '-c', '--clear', help='Clear files before starting', action='store_true')

    return parser.parse_args(argv)


if __name__ == '__main__':
    dedupe(parse_arg(sys.argv[1:]))
