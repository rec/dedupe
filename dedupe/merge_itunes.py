from .dedupe_action import dedupe_action
from pathlib import Path
import collections
import itertools
import shutil
import sys

LIBRARY_NAME = Path('iTunes Music Library.xml')
MEDIA_DIRECTORY = Path('iTunes Media')
AUDIO_SUFFIXES = '.aiff', '.aif', '.mp3', '.m4a', '.wav', '.wave'
DRY_RUN = True


class Merger:
    def __init__(
        self, source, target, index=None, dry_run=True, itunes_dir=None
    ):
        self.source = Path(source)
        self.target = Path(target)
        self.index = index
        self.dry_run = dry_run
        assert self.dry_run == DRY_RUN

        self.itunes_file = Path(itunes_dir or self.target) / LIBRARY_NAME
        self.counter = collections.Counter()
        self.files = collections.defaultdict(list)

    def merge(self):
        actions = self._action(self.source)
        actions = itertools.islice(actions, *self.index)
        for i, (src, action) in enumerate(actions):
            print('%06d: %07s: %s' % (i, action, self._relative(src)))

    def _relative(self, src, action='move'):
        tdir = self.target
        if action:
            tdir = tdir.with_name('%s-%s' % (tdir.name, action))

        return tdir / src.relative_to(self.source)

    def _move(self, src, action='move'):
        target = self._relative(src, action)
        if not self.dry_run or target.exists():
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
        if src.name.startswith('.'):
            return

        if src.is_dir():
            for s in src.iterdir():
                yield from self._action(s)

        elif not True and '/Matmos/Matmos/' not in str(src):
            return

        elif src.suffix.lower() not in AUDIO_SUFFIXES:
            yield self._ignore(src)

        else:
            t = self._relative(src, '')
            action, *files = dedupe_action(src, t)
            if action == 'dupe':
                yield self._dupes(src)
            else:
                if action == 'replace':
                    print('      : replace:', *files)
                yield self._move(src)


if __name__ == '__main__':
    args = sys.argv[1:]
    dry_run = DRY_RUN
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
