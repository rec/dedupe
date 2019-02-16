import cfgs
from . import hasher, files


def fingerprint(name, files, target):
    _clean_dict(target)
    fp = FINGERPRINTERS[name]
    td = target.setdefault(name, {})
    for i, file in enumerate(files):
        if not (i % 5000):
            print(i + 1, file)
        td.setdefault(fp(file), set()).add(file)


def size_and_header(filename):
    return '%s_%s' % (files.size(f), hasher.hash_header(f))


# Map category to fingerprint function
FINGERPRINTERS = {
    'file': hasher.hash_file,
    # 'size': lambda f: str(files.size(f)),
    'size': files.size,
    'size_and_header': size_and_header,
}


def compute_sizes(roots):
    def default(o):
        if isinstance(o, set):
            return list(o)
        raise TypeError

    write_kwds = {'default':  default, 'indent': 4, 'sort_keys': True}
    app = cfgs.App('swirly-dedupe', write_kwds=write_kwds)
    for root in roots:
        with app.data.open('%s/size.json' % root) as f:
            fingerprint('size', files.walk(root), f.contents)


def _clean_dict(d):
    for k, v in d.items():
        for k2, v2 in v.items():
            v[k2] = set(v2)


if __name__ == '__main__':
    import sys
    compute_sizes(sys.argv[1:])
