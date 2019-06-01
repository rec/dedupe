from . import itunes
from pathlib import Path
import collections
import mutagen
import shutil
import sys
import yaml

LIBRARY_NAME = 'iTunes Music Library.xml'
AUDIO_SUFFIXES = '.aiff', '.aif', '.wav', '.wave', '.mp3', '.m4a'


class Merger:
    def __init__(self, source, target, dry_run=True, itunes=None, move=True):
        self.itunes_file = itunes or Path(target) / LIBRARY_NAME
        self.source = Path(source)
        self.target = Path(target) / 'iTunes Media'
        self.dry_run = dry_run
        self.counter = collections.Counter()
        self.files = collections.defaultdict(list)
        self.move = move

    def merge(self):
        try:
            self._move_or_mark_dupe(self.source, self.target)
            self._add_files(self.files['to_move'])
        finally:
            for k, v in self.counter.items():
                print(k, v, sep=' = ')

    def execute(self):
        for source in self.files['to_move']:
            target = self._relative(source)

            if self.dry_run:
                print('move' if self.move else 'copy', source, target)
            elif self.move:
                shutil.move(source, target)
            else:
                shutil.copy(source, target)

        if self.dry_run:
            yaml.dump(dict(self.files), sys.stdout)

        with itunes.context(self.itunes_file, not self.dry_run) as self.itunes:
            for source in self.files['add']:
                self.itunes.add_new_track(self._relative(source))

    def _relative(self, f, target=None):
        return (target or self.target) / f.relative_to(self.source)

    def _append(self, action, filename):
        self.files[action].append(filename)

    def _move_or_mark_dupe(self, source, target):
        for s in source.iterdir():
            if s.name.startswith('.'):
                continue

            t = target / s.name
            is_dupe = t.exists() or t.with_suffix('.m4a').exists()

            if not is_dupe:
                self._append('to_move', s)
            elif s.is_dir():
                self._move_or_mark_dupe(s, t)
            else:
                self._append('dupes', s)

    def _add_files(self, files):
        for f in files:
            if f.name.startswith('.'):
                continue

            if f.is_dir():
                self._add_files(f.iterdir())
                continue

            if f.suffix in AUDIO_SUFFIXES:
                try:
                    if mutagen.File(f):
                        self._append('add', f)
                    else:
                        self._append('ignore', f)
                except mutagen.MutagenError:
                    self._append('error', f)
            else:
                self._append('ignore', f)


if __name__ == '__main__':
    merger = Merger('/Volumes/Matmos/Media', '/Volumes/Matmos/iTunes')
    merger.merge()
    merger.execute()
