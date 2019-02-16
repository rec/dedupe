from . import files
import mutagen, pathlib, shutil

SUFFIXES = {'.aif', '.aiff', '.m4a', '.mp3', '.wav', '.wave'}


def merge(target, source):
    source = pathlib.Path(source)
    for sfile in files.walk(source):
        if sfile.suffix.lower() not in SUFFIXES:
            continue

        tfile = target / sfile.relative_to(source)
        if not tfile.exists():
            tfile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(sfile, tfile)
            continue

        sinfo = mutagen.File(sfile).info
        tinfo = mutagen.File(tfile).info

        # Cases:
        # 1. source and target are actually different
        #    rename and try again
        #
        # 2. they're the same, but source is higher quality than target
        #    replace target with source
        #
        # 3. the same, source is less than or equal quality
        #    do nothing.


def rename(file, source, target):
    global FILES
    FILES += 1

    tfile = target / file.relative_to(source)
    while tfile.exists():
        global RENAMES
        RENAMES += 1
        *rest, last = tfile.stem.split()
        if last.isnumeric():
            rest += (str(1 + int(last)),)
        else:
            rest += (last, '1')
        tfile = tfile.parent / (' '.join(rest) + tfile.suffix)

    # file.rename(tfile)


def merge_from_directory(base, target_name):
    base = Path(base)
    sources, target = [], None
    for p in base.iterdir():
        if p.stem == target_name:
            target = p
        else:
            sources.append(p)

    merge(target, sources)


if __name__ == '__main__':
    merge_from_directory('/Volumes/McLuhan/Media/', 'Newton')
    print(FILES, RENAMES)
