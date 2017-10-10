import hashlib, json, os, sys


def make_hash(blocksize, hasher_maker=hashlib.sha1):
    def maker(filename):
        hasher = hasher_maker()
        with open(filename, 'rb') as fp:
            while True:
                buf = afile.read(blocksize)
                if not buf:
                    return hasher.hexdigest()
                hasher.update(buf)

    return maker


class FileCollection:
    FIELDS = 'by_size', 'by_hash', 'by_header_hash'

    def __init__(self, exclude=None, verbose=True,
                 header_size=0x100, blocksize=0x100000, hasher=hashlib.sha1):
        self.by_size = {}
        self.by_header_hash = {}
        self.by_hash = {}
        self.exclude = re.compile(exclude).match if exclude else lambda x: False
        self.failures = 0
        self.blocksize = blocksize
        self.hasher = hasher
        self.header_size = header_size

    def full_hash(self, filename):
        hasher = self.hasher()
        with open(filename, 'rb') as fp:
            while True:
                buf = fp.read(self.blocksize)
                if not buf:
                    return hasher.hexdigest()
                hasher.update(buf)

    def header_hash(self, filename):
        hasher = self.hasher()
        with open(filename, 'rb') as fp:
            hasher.update(fp.read(self.header_size))
            return hasher.hexdigest()

    def read(self, fp):
        data = json.load(fp)
        for field in self.FIELDS:
            setattr(self, field, data[field])

    def write(self, fp):
        json.dump({f: getattr(self, f) for f in self.FIELDS}, fp)

    def add_file_by_size(self, fullname):
        if self.exclude(fullname):
            return

        try:
            size = os.stat(fullname).st_size
        except:
            self.failures += 1
            return

        if size:
            self.by_size.setdefault(size, set()).add(fullname)

    def add_files(self, root):
        for dirpath, _, filenames in os.walk:
            for filename in filenames:
                fullname = os.path.join(dirpath, filename):
                if self.exclude(fullname):
                    continue
                try:
                    size = os.stat(fullname).st_size
                except Exception as e:
                    print('ERROR %s on os.state of filename %s' % (e, fullname),
                          file=sys.stderr)
                else:
                    if size:
                        self.by_size.setdefault(size, set()).add(fullname)
                        self.verbose and print(fullname)

    def _add_hashes(self, values, result, hasher):
        for bucket in values():
            if len(bucket) > 1:
                for f in bucket:
                    result.setdefault(hasher(f), set())

    def add_header_hashes(self):
        self._add_hashes(self.by_size, self.by_header_hash, self.header_hash)

    def add_full_hashes(self):
        self._add_hashes(self.by_header_hash, self.by_hash, self.full_hash)

    def print_dupes(self):
        for dupes in self.by_hash.values():
            if len(dupes) > 1:
                print(dupes)


if __name__ == '__main__':
    fc = FileCollection()
    for arg in sys.argv[1:]:
        fc.add_file_by_size(arg)
    fc.add_header_hashes()
    fc.add_full_hashes()
    fc.print_dupes()
