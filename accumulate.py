#!/usr/bin/env python

from dedupe import files, hasher
import arguments, json, os, re, sys

"""
Needs to work on up to 500,000 files with an average pathlength of 100 = 50 MB

filesize.json:
   {filename: {filesize: set(dirpath)}

header.json:
   {filename: {header_hash: set(dirpath)}

contents.json:
   {filename: {contents_hash: set(dirpath)}

"""


class HashCollection:
    def __init__(self, verbose, data, clear):
        self.verbose = verbose
        self.failures = 0
        self.data = files.canonical_path(data)
        self.clear = clear
        os.makedirs(self.data, exist_ok=True)

    def filename(self, strategy):
        return os.path.join(self.data, strategy + '.json')

    def read(self, strategy, readonly=False):
        filename = self.filename(strategy)
        if not readonly and self.clear:
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
            return json.dump(obj, fp, default=default, indent=4, sort_keys=True)

    def add(self, hasher, dirpath, filename, table):
        entry = table.setdefault(filename, {})
        if any(dirpath in i for i in entry.values()):
            return 0

        hasher_function = getattr(hasher.Hasher, hasher)
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
            print(fullname.encode())
        return 1

    def add_files(self, *roots, exclude):
        def filter_dotfiles(dirs):
            return [d for d in dirs if not d.startswith('.')]

        table = self.read('filesize')
        items = 0

        for root in roots:
            root = files.canonical_path(root)
            for dirpath, dirs, filenames in os.walk(root):
                dirs[:] = filter_dotfiles(dirs)
                filenames[:] = filter_dotfiles(filenames)
                for filename in filenames:
                    fullname = os.path.join(dirpath, filename)
                    if any(e(fullname) for e in exclude):
                        continue

                    items += self.add('filesize', dirpath, filename, table)

        self.write(table, 'filesize')
        print(items, ' file', '' if items == 1 else 's', ' added.', sep='')

    def refine(self, before, after):
        before_table = self.read(before, True)
        after_table = self.read(after)
        items = 0

        for filename, entry in before_table.items():
            for key, bucket in entry.items():
                if len(bucket) > 1:
                    for dirpath in bucket:
                        items += self.add(after, dirpath, filename, after_table)

        self.write(after_table, after)
        print(items, ' file', '' if items == 1 else 's', ' added.', sep='')


def dedupe(args):
    hc = HashCollection(args.verbose, args.data, args.clear)
    if args.add:
        args.verbose and print('Adding roots:', args.add)
        exclude = args.exclude and [
            re.compile(e).search for e in args.exclude.split(':')]
        hc.add_files(*args.add.split(':'), exclude=exclude)

    if args.header:
        hc.refine('filesize', 'header')

    if args.contents:
        hc.refine('header', 'contents')

    print('Failures:', hc.failures)


if __name__ == '__main__':
    dedupe(arguments.parse_arg(sys.argv[1:]))
