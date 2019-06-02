from . import itunes
from pathlib import Path
import collections
import itertools
import mutagen
import shutil
import sys
import yaml

LIBRARY_NAME = Path('iTunes Music Library.xml')
MEDIA_DIRECTORY = Path('iTunes Media')
AUDIO_SUFFIXES = '.aiff', '.aif', '.mp3', '.m4a'  #, '.wav', '.wave'


class Merger:
    def __init__(self, source, target, index=None, dry_run=True, move=True):
        self.source = Path(source)
        self.target = Path(target)
        self.index = index
        self.dry_run = dry_run
        self.move = move

        self.itunes_file = self.target / LIBRARY_NAME
        self.counter = collections.Counter()
        self.files = collections.defaultdict(list)

    def merge(self):
        file_actions = self._file_actions(self.source, self.target)
        for file, action in itertools.islice(file_actions, *self.index):
            self.files[action].append(file)

    def execute(self):
        for source in self.files['move']:
            target = self._relative(source)

            if self.dry_run:
                print('move' if self.move else 'copy', source, target)
            elif self.move:
                shutil.move(source, target)
            else:
                shutil.copy(source, target)

        if self.dry_run:
            dump = {}
            for k, v in self.files.items():
                dump[k] = [str(s) for s in v]
            yaml.dump(dump, sys.stdout)

        with itunes.context(self.itunes_file, not self.dry_run) as self.itunes:
            for source in self.files['add']:
                if not self.dry_run:
                    source = self._relative(source)
                self.itunes.add_new_track(source)

    def _relative(self, f, target=None):
        return (target or self.target) / f.relative_to(self.source)

    def _file_actions(self, source, target):
        for s in source.iterdir():
            if s.name.startswith('.'):
                continue
            t = target / s.name
            is_dupe = t.exists() or t.with_suffix('.m4a').exists()

            if not is_dupe:
                yield s, 'move'
                yield from self._move_actions(s)
            elif s.is_dir():
                yield from self._file_actions(s, t)
            else:
                yield s, 'dupes'

    def _move_actions(self, f):
        if f.name.startswith('.'):
            pass

        elif f.is_dir():
            for f in f.iterdir():
                yield from self._move_actions(f)

        elif f.suffix in AUDIO_SUFFIXES:
            try:
                if mutagen.File(f):
                    yield f, 'add'
                else:
                    yield f, 'ignore'
            except mutagen.MutagenError:
                yield f, 'error'

        else:
            yield f, 'ignore'


if __name__ == '__main__':
    index = [None if i == 'None' else int(i) for i in sys.argv[1:]]
    while len(index) < 3:
        index.append(None)
    merger = Merger('/Volumes/Matmos/Media', '/Volumes/Matmos/iTunes', index)
    merger.merge()
    merger.execute()
