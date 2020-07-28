from read_find_listing import IGNORE_DIRS, IGNORE_FILES, IGNORE_OS_DIRECTORIES
import json
import os
import sys


def accept_dir(d):
    return not (
        d.startswith('.')
        or d == '__pycache__'
        or d in IGNORE_DIRS
        or d.endswith('.app')
    )


def accept_file(d):
    return not (d.endswith('.pyc') or d in IGNORE_FILES)


def run_one(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath == root:
            dirnames[:] = [
                d for d in dirnames if d not in IGNORE_OS_DIRECTORIES
            ]
        dirnames[:] = sorted(d for d in dirnames if accept_dir(d))
        for filename in sorted(f for f in filenames if accept_file(f)):
            path = '%s/%s' % (dirpath, filename)
            try:
                st = os.stat(path)
            except Exception:
                print('Skipping', path, file=sys.stderr)
                continue

            record = {'mtime': st.st_mtime, 'size': st.st_size, 'path': path}
            print(json.dumps(record))


def main(args=None):
    for arg in args or sys.argv[1:]:
        run_one(arg)


if __name__ == '__main__':
    main()
