from . import files
import mutagen, pathlib, shutil, sys

SUFFIXES = {'.aif', '.aiff', '.m4a', '.mp3', '.wav', '.wave'}
DELTA = 0.001
DRY_RUN = True
VERBOSE = True
COPIES = REPLACEMENTS = IGNORED = TOTAL = 0


def merge_all(source, target):
    for s in pathlib.Path(source).glob('*'):
        if not s.stem.startswith('.'):
            merge_one(source, target)
    print(COPIES, 'copies')
    print(REPLACEMENTS, 'replacements')
    print(IGNORED, 'ignored')
    print(COPIES + REPLACEMENTS + IGNORED, 'total')
    print(TOTAL, 'check total')


def merge_one(source, target):
    source = pathlib.Path(source)
    for sfile in files.walk(source):
        if sfile.suffix.lower() in SUFFIXES:
            copy(sfile, target / sfile.relative_to(source))


def copy(sfile, tfile):
    def do_copy(replace):
        if VERBOSE:
            print('Replacing' if replace else 'Copying', sfile, '->', tfile)

        if not DRY_RUN:
            if not replace:
                tfile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(sfile, tfile)

    global IGNORED, TOTAL, COPIES, REPLACEMENTS
    TOTAL += 1

    while tfile.exists():
        slength = mutagen.File(sfile).info.length
        tlength = mutagen.File(tfile).info.length

        if abs(slength - tlength) <= DELTA:
            # If the two sources are the same time length or extremely close
            # we assume they're the same, and we take the biggest file, hoping
            # that's always the highest quality
            if sfile.stat.st_size > tfile.stat.st_size:
                # On the theory bigger is better
                do_copy(True)
                REPLACEMENTS += 1
            else:
                IGNORED += 1
            return

        # source and target are actually different: rename and try again
        *rest, last = tfile.stem.split()
        if last.isnumeric():
            rest += (str(1 + int(last)),)
        else:
            rest += (last, '1')
        tfile = tfile.parent / (' '.join(rest) + tfile.suffix)

    COPIES += 1
    do_copy(False)


if __name__ == '__main__':
    merge_all(*sys.argv[1:])
