import sys
from pathlib import Path
from . import merge_media


def collect_all_suffixes(root):
    suffixes = set()
    for f in merge_media.walk(root):
        suffixes.add(f.suffix)

    return suffixes


def walk(source, suffixes):
    for dirpath, dirs, filenames in os.walk(source):
        dirpath = Path(dirpath)
        for filename in filenames:
            path = Path(filename)
            if path.suffix.lower() in suffixes:
                yield path


if __name__ == '__main__':
    print(sorted(collect_all_suffixes(sys.argv[1])))
