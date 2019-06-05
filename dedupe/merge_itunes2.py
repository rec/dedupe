from .simple_merge import rmdir_empty
from .track import filename_to_track
from collections import Counter
from pathlib import Path
import attr
import mutagen
import shutil

SUFFIX = '.m4a'
TIME_DELTA = 1000


@attr.dataclass
class Merger:
    source: Path = Path()
    target: Path = Path()
    counter: Counter = attr.Factory(Counter)

    def run(self):
        try:
            self._gather()
        finally:
            print()
            print()
            print(self.counter)
            print()
            print()
        self._merge()
        print('Removed', rmdir_empty(self.source), 'directories')

    def _gather(self):
        self.actions = {}
        for source_dir in self._itunes_directories():
            for action, file in self._gather_directory(source_dir):
                self.counter.update([action])
                self.actions.setdefault(action, []).append(file)

    def _merge(self):
        for action, files in self.actions.items():
            tdir = self.source.with_name('%s-%s' % (self.source.name, action))
            for file in files:
                tfile = self._relative(file, tdir)
                tfile.parent.mkdir(exist_ok=True, parents=True)
                if not True:
                    print('move', file, tfile)
                else:
                    shutil.move(file, tfile)

    def _relative(self, f, target=None):
        return (target or self.target) / f.relative_to(self.source)

    def _track(self, t):
        track = self.tracks[t]
        if track is None:
            try:
                track = self.tracks[t] = filename_to_track(t)
            except mutagen.MutagenError:
                track = self.tracks[t] = False
        return track

    def _gather_directory(self, source_dir):
        td = self._relative(source_dir)
        tracks = td.iterdir() if td.is_dir() else ()
        self.tracks = {t: None for t in tracks if not t.name.startswith('.')}

        if self._relative(source_dir).exists():
            for sfile in source_dir.iterdir():
                if not sfile.name.startswith('.'):
                    yield self._file_action(sfile), sfile
        else:
            yield 'movedir', source_dir

    def _file_action(self, sfile):
        try:
            sdata = filename_to_track(sfile)
            if not sdata:
                return 'cannot_read'
        except mutagen.MutagenError:
            return 'error'

        stime = sdata['Total Time']
        sname = sdata.get('Name', '').lower()
        ssize = sdata['Size']

        def near(data):
            return abs(data['Total Time'] - stime) < TIME_DELTA

        tfile = self._relative(sfile)
        if tfile.with_suffix(SUFFIX).exists():
            return 'dupe'

        if tfile.exists():
            tdata = self._track(tfile)
            if not tdata:
                return 'move'
            if not near(tdata):
                return 'different'
            return 'dupe'

        # Look for a very similar file
        for tfile in self.tracks:
            if _canonical(tfile) != _canonical(sfile):
                continue

            td = self._track(tfile)
            if td and near(td) and td.get('Name', '').lower() == sname:
                if tfile.suffix == SUFFIX:
                    return 'dupe'

                if sfile.suffix == SUFFIX or ssize > td['Size']:
                    return 'move'

                return 'dupe'
        return 'move'

    def _itunes_directories(self):
        music = self.source / 'Music'
        if music.is_dir():
            for artist in music.iterdir():
                yield from _subdirectories(artist)
        yield from _subdirectories(self.source / 'Podcasts')


def _subdirectories(f):
    if f.is_dir():
        for g in f.iterdir():
            if g.is_dir():
                yield g


def _canonical(f):
    s = f.stem
    parts = s.split()
    if len(parts) > 2:
        if parts[-1].isnumeric():
            parts.pop()
        if parts[0].isnumeric():
            parts.pop(0)
    return ' '.join(parts).lower()


if __name__ == '__main__':

    source = Path('/Volumes/Matmos/dedupe/Media')
    target = Path('/Volumes/Matmos/iTunes')

    merger = Merger(source, target)
    merger.run()
