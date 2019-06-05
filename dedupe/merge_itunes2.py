# from pathlib import Path
import attr
from .track import filename_to_track
import mutagen
from pathlib import Path

SUFFIX = '.m4a'
TIME_DELTA = 1000


@attr.dataclass
class Merger:
    source: Path = Path()
    target: Path = Path()

    def merge(self):
        for source_dir in self.itunes_directories():
            yield from self.merge_one(source_dir)

    def relative(self, f):
        return self.target / f.relative_to(self.source)

    def get_track(self, t):
        track = self.tracks[t]
        if track is None:
            try:
                track = self.tracks[t] = filename_to_track(t)
            except mutagen.MutagenError:
                track = self.tracks[t] = False
        return track

    def merge_one(self, source_dir):
        td = self.relative(source_dir)
        tracks = td.iterdir() if td.is_dir() else ()
        self.tracks = {t: None for t in tracks if not t.name.startswith('.')}

        for sfile in source_dir.iterdir():
            yield self.file_action(sfile), sfile

    def file_action(self, sfile):
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

        tfile = self.relative(sfile)
        if tfile.with_suffix(SUFFIX).exists():
            return 'dupe'

        if tfile.exists():
            tdata = self.get_track(tfile)
            if not tdata:
                return 'move'
            if near(tdata):
                return 'different'
            return 'dupe'

        # Look for a very similar file
        for tfile in self.tracks:
            if canonical(tfile) != canonical(sfile):
                continue

            td = self.get_track(tfile)
            if td and near(td) and td.get('Name', '').lower() == sname:
                if tfile.suffix == SUFFIX:
                    return 'dupe'

                if sfile.suffix == SUFFIX or ssize > td['Size']:
                    return 'move'

                return 'dupe'
        return 'move'

    def itunes_directories(self):
        music = self.source / 'Music'
        if music.is_dir():
            for artist in music.iterdir():
                yield from subdirectories(artist)
        yield from subdirectories(self.source / 'Podcasts')


def subdirectories(f):
    if f.is_dir():
        for g in f.iterdir():
            if g.is_dir():
                yield g


def canonical(f):
    s = f.stem
    parts = s.split()
    if len(parts) > 2:
        if parts[-1].isnumeric():
            parts.pop()
        if parts[0].isnumeric():
            parts.pop(0)
    return ' '.join(parts).lower()


if __name__ == '__main__':
    source = Path('/Volumes/Matmos/Media')
    target = Path('/Volumes/Matmos/iTunes')

    merger = Merger(source, target)
    for i, (action, file) in enumerate(merger.merge()):
        print('%06d: %07s: %s' % (i, action, file))
