import sys
from pathlib import Path
from . import merge_media

SUFFIXES = '.avi', '.jpg', '.mov', '.mp4', '.tif','.gif'
DRY_RUN = True

def collect_all_suffixes(root):
    suffixes = set()
    for f in merge_media.walk(root):
        if f.suffix not in suffixes:
            print(f.suffix)
            suffixes.add(f.suffix)

    return suffixes


def walk(source, suffixes=SUFFIXES):
    for dirpath, dirs, filenames in os.walk(source):
        for filename in filenames:
            path = Path(filename)
            if path.suffix.lower() in suffixes:
                yield dirpath / path


def merge(source, target):
    for source_file in walk(source):
        rel = source_file.relative_to(source)
        target_file = target / rel
        if not  target_file.exists:
            if DRY_RUN:
                print('Moving', rel)
            else:
                _move(source_file, target_file)


def _move(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(source, target)
    except:
        print('FAILED to move', source, file=sys.err)
    else:
        print('Moved', source)


if __name__ == '__main__':
    print(sorted(collect_all_suffixes(sys.argv[1])))
