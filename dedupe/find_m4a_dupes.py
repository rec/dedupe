import json, os, pathlib, sys


def move_m4a_dupes(source, target):
    for dirpath, dirs, filenames in os.walk(source):
        dirpath = pathlib.Path(dirpath)
        lower_filenames = {f.lower() for f in filenames}
        for f in filenames:
            f = pathlib.Path(f)
            if f.suffix.lower() == '.mp3':
                # Get canonical name
                *rest, last = f.stem.split()
                if rest and last.isnumeric():
                    g = f.parent / (' '.join(rest))
                else:
                    g = f
                m4a = g.with_suffix('.m4a')
                if str(m4a).lower() in lower_filenames:
                    s = dirpath / f
                    t = target / s.relative_to(source)
                    t.parent.mkdir(parents=True, exist_ok=True)
                    print(s, '->', t)
                    s.rename(t)


if __name__ == '__main__':
    issues = move_m4a_dupes(*sys.argv[1:])
