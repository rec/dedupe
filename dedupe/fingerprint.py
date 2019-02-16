import cfgs
from . import hasher, files

APP = cfgs.App('swirly-dedupe')


def fingerprint(name, files, target):
    fp = FINGERPRINTERS[name]
    td = target.setdefault(name, {})
    for file in files:
        td.setdefault(fp(file), set()).add(file)


def size_and_header(filename):
    return '%s_%s' % (files.size(f), hasher.hash_header(f))


# Map category to fingerprint function
FINGERPRINTERS = {
    'file': hasher.hash_file,
    'size': lambda f: str(files.size(f)),
    'size_and_header': size_and_header,
}


def compute_sizes(roots):
    with APP.data.open('size.json') as f:
        for root in roots:
            fingerprint('size', files.walk(root), f.contents)


def _merge_into(source, target):
    for category, entries in source.items():
        t_entries = target.setdefault(category, {})
        for key, bucket in entries.items():
            t_entries.setdefault(key, set()).update(bucket)
