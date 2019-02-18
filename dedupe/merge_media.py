from . import files
import collections, mutagen, pathlib, shutil, sys

SUFFIXES = {'.aif', '.aiff', '.m4a', '.mp3', '.wav', '.wave'}
DELTA = 0.001
DRY_RUN = True
VERBOSE = True


def merge_one(source, target, counter):
    source = pathlib.Path(source)

    if VERBOSE:
        print('Merging  ', source, '->', target)

    for sfile in files.walk(source):
        if sfile.suffix.lower() in SUFFIXES:
            copy(sfile, target / sfile.relative_to(source), counter)


def copy(sfile, tfile, counter):
    def do_copy(replace):
        if VERBOSE:
            action = 'Replacing' if replace else 'Copying  '
            print(action, sfile, '->', tfile)

        if not DRY_RUN:
            if not replace:
                tfile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(sfile, tfile)

    counter['total'] += 1

    while tfile.exists():
        slength = mutagen.File(sfile).info.length
        tlength = mutagen.File(tfile).info.length

        if abs(slength - tlength) <= DELTA:
            # If the two sources are the same time length or extremely close
            # we assume they're the same, and we take the biggest file, hoping
            # that's always the highest quality
            if sfile.stat.st_size > tfile.stat.st_size:
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



def merge_all(source, target, counter):
    for s in pathlib.Path(source).glob('*'):
        if not s.stem.startswith('.'):
            merge_one(source, target, counter)
    report(counter)


def report(counter):
    total = 0
    for name in 'copies', 'replacements', 'ignored':
        value = counter[name]
        print(value, name)
        total += value

    print(counter['total'], 'total')
    print(total, 'check total')


if __name__ == '__main__':
    merge_all(*sys.argv[1:])
