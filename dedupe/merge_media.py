import collections
import mutagen
import os
import pathlib
import shutil
import sys

SUFFIXES = {'.aif', '.aiff', '.m4a', '.mp3', '.wav', '.wave'}
DELTA = 0.001
DRY_RUN = not True
VERBOSE = True


def length(file):
    try:
        return mutagen.File(file).info.length
    except Exception:
        print('*** error on file length', file)
        return 0


def walk(root, accept=lambda x: True):
    root = os.path.abspath(os.path.expanduser(root))
    for dirpath, dirs, filenames in os.walk(root):
        dirs[:] = (d for d in dirs if accept(d))
        dirpath = pathlib.Path(dirpath)
        for filename in filenames:
            if accept(filename):
                yield dirpath / filename


def merge_all(target, *sources):
    counter = collections.Counter()
    for source in sources:
        c = merge_one(pathlib.Path(source), target)
        counter.update(c)
    print('Total counter:', counter, file=sys.stderr)


def merge_one(source, target):
    if VERBOSE:
        print('\nMerging', source, '->', target, file=sys.stderr)

    counter = collections.Counter()
    for sfile in walk(source):
        if sfile.suffix.lower() in SUFFIXES:
            copy(sfile, target, source, counter)
    print('Counter:', counter, file=sys.stderr)


def copy(sfile, target, source, counter):
    rel = sfile.relative_to(source)
    tfile = target / rel

    def do_copy(replace):
        if VERBOSE:
            action = 'Replacing' if replace else 'Copying  '
            print(action, rel)

        if not DRY_RUN:
            if not replace:
                tfile.parent.mkdir(parents=True, exist_ok=True)
            tmp_file = tfile.with_suffix('.tmp')
            shutil.copy(sfile, tmp_file)
            os.rename(tmp_file, tfile)

    counter['total'] += 1

    while tfile.exists():
        slength = length(sfile)
        tlength = length(tfile)
        if not tlength:
            break

        if not slength:
            counter['ignored'] += 1
            return

        if abs(slength - tlength) <= DELTA:
            # If the two sources are the same time length or extremely close
            # we assume they're the same, and we take the biggest file, hoping
            # that's always the highest quality
            if sfile.stat().st_size > tfile.stat().st_size:
                do_copy(True)
                counter['replacements'] += 1
            else:
                counter['ignored'] += 1
            return

        # source and target are actually different: rename and try again
        *rest, last = tfile.stem.split()
        if last.isnumeric():
            rest += (str(1 + int(last)),)
        else:
            rest += (last, '1')
        tfile = tfile.parent / (' '.join(rest) + tfile.suffix)

    counter['copies'] += 1
    do_copy(False)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        print('Usage: merge_media.py target source [..source]')
    else:
        merge_all(*args)
