from . import itunes
from pathlib import Path
import collections
import itertools
import shutil
import sys

LIBRARY_NAME = Path('iTunes Music Library.xml')
MEDIA_DIRECTORY = Path('iTunes Media')
AUDIO_SUFFIXES = '.aiff', '.aif', '.mp3', '.m4a', '.wav', '.wave'


class Merger:
    def __init__(
        self, source, target, index=None, dry_run=True, itunes_dir=None
    ):
        self.source = Path(source)
        self.target = Path(target)
        self.index = index
        self.dry_run = dry_run
        # assert self.dry_run

        self.itunes_file = Path(itunes_dir or self.target) / LIBRARY_NAME
        self.counter = collections.Counter()
        self.files = collections.defaultdict(list)

    def merge(self):
        with itunes.context(self.itunes_file, not self.dry_run) as self.itunes:
            actions = self._action(self.source)
            actions = itertools.islice(actions, *self.index)
            for i, (src, action) in enumerate(actions):
                print('%06d: %06s: %s' % (i, action, self._relative(src)))

    def _relative(self, src, action='move'):
        tdir = self.target
        if action:
            tdir = tdir.with_name('%s-%s' % (tdir.name, action))

        return tdir / src.relative_to(self.source)

    def _move(self, src, action='move'):
        target = self._relative(src, action)
        if not (self.dry_run or target.exists()):
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(src, target)
        return src, action

    def _dupes(self, src):
        return self._move(src, 'dupes')

    def _error(self, src):
        return self._move(src, 'error')

    def _ignore(self, src):
        return src, 'ignore'

    def _action(self, src):
        t = self._relative(src)
        if src.name.startswith('.'):
            pass

        elif src.is_dir():
            for s in src.iterdir():
                yield from self._action(s)

        elif t.exists() or t.with_suffix('.m4a').exists():
            yield self._dupes(src)

        elif src.suffix.lower() not in AUDIO_SUFFIXES:
            yield self._ignore(src)

        else:
            yield self._add(src)


if __name__ == '__main__':
    args = sys.argv[1:]
    dry_run = not True
    for flag in '-d', '--dry_run':
        try:
            dry_run = args.remove(flag) or True
        except ValueError:
            pass

    index = [None if i == 'None' else int(i) for i in args] or [None]

    source = '/Volumes/Matmos/Media'
    target = '/Volumes/Matmos/iTunes'
    itunes_dir = '/Users/tom/Music/iTunes'
    merger = Merger(source, target, index, dry_run, itunes_dir)
    merger.merge()
