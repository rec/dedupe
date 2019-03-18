import sys
from pathlib import Path
from . import merge_media

SUFFIXES = '.avi', '.jpg', '.mov', '.mp4', '.tif','.gif'


def collect_all_suffixes(root):
    suffixes = set()
    for f in merge_media.walk(root):
        if f.suffix not in suffixes:
            print(f.suffix)
            suffixes.add(f.suffix)

    return suffixes


def walk(source, suffixes=SUFFIXES):
    for dirpath, dirs, filenames in os.walk(source):
        dirpath = Path(dirpath)
        for filename in filenames:
            path = Path(filename)
            if path.suffix.lower() in suffixes:
                yield path


if __name__ == '__main__':
    print(sorted(collect_all_suffixes(sys.argv[1])))
