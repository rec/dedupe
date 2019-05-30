import collections
from pathlib import Path
from .itunes import iTunesLoader
import shutil
import traceback

LIBRARY_NAME = 'iTunes Music Library.xml'
AUDIO_SUFFIXES = '.mp3', '.m4a'


def merge(source, target, dry_run=True, itunes_file=None):
    source, target = Path(source), Path(target)
    itunes_file = itunes_file or target / LIBRARY_NAME
    target /= 'iTunes Media'
    loader = iTunesLoader(write=not dry_run)
    with loader.file_context(itunes_file) as itunes:
        _merge(itunes, source, target, dry_run)
        itunes.update_date()


def _merge(itunes, source, target, dry_run):
    counter = collections.Counter()
    try:
        for fsource in _missing_files(source, target):
            ftarget = target / fsource.relative_to(source)
            print('move', ftarget, fsource, sep=':')
            if dry_run:
                ftarget = fsource
            else:
                shutil.move(fsource, ftarget)

            for f in _files_beneath(ftarget):
                try:
                    track_id, pid, track = itunes.add_new_track(f)
                    print('add', track_id, pid, sep=':')
                    counter.update(track.keys())
                    counter.update([len(track)])
                except Exception as e:
                    print('ERROR', f)
                    traceback.print_exc()
                    counter[('ERROR', str(e))] += 1

    except KeyboardInterrupt:
        pass
    for k, v in counter.items():
        print(k, v, sep=' = ')


def _missing_files(source, target):
    for s in source.iterdir():
        if not s.name.startswith('.'):
            t = target / s.name
            if not (t.exists() or t.with_suffix('.m4a').exists()):
                yield s
            elif s.is_dir():
                yield from _missing_files(s, t)


def _files_beneath(f):
    if not f.name.startswith('.'):
        if f.suffix in AUDIO_SUFFIXES:
            yield f
        elif f.is_dir():
            for g in f.iterdir():
                yield from _files_beneath(g)


if __name__ == '__main__':
    source = Path('/Volumes/Matmos/Media')
    target = Path('/Volumes/Matmos/iTunes')
    merge(source, target)
