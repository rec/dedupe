from dedupe import files, hasher
import os
import sys


def size_and_header(root):
    volumes, name = os.path.split(files.canonical_path(root))
    assert volumes == '/Volumes', volumes

    with open(name + '.txt', 'w') as fp:
        for filename in files.walk(root):
            try:
                filesize, digest = hasher.hash_header_with_size(filename)
                print(filename, filesize, digest, file=fp)
            except Exception:
                print('FAILED', filename, file=sys.stderr)


if __name__ == '__main__':
    for root in sys.argv[1:]:
        size_and_header(root)
