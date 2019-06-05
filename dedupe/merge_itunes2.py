# from pathlib import Path
from .track import filename_to_track
import mutagen

SUFFIX = '.m4a'
TIME_DELTA = 1000


def merge(source, target):
    def relative(f):
        return target / f.relative_to(source)

    for source_dir in itunes_directories(source):
        yield from merge_one(source_dir, relative)


def merge_one(source_dir, relative):
    td = relative(source_dir)
    tracks = td.iterdir() if td.is_dir() else ()
    tracks = {t: None for t in tracks if not t.name.startswith('.')}

    def get_track(t):
        track = tracks[t]
        if track is None:
            try:
                track = tracks[t] = filename_to_track(t)
            except mutagen.MutagenError:
                track = track[t] = False
        return track

    for sfile in source_dir:
        yield file_action(sfile, tracks, get_track, relative), sfile


def file_action(sfile, tracks, get_track, relative):
    sdata = get_track(sfile)
    if not sdata:
        return 'error'

    stime = sdata['Total Time']
    sname = sdata.get('Name', '').lower()
    ssize = sdata['Size']

    def near(data):
        return abs(tdata['Total Time'] - stime) < TIME_DELTA

    tfile = relative(sfile)
    if tfile.with_suffix(SUFFIX).exists():
        return 'dupe'

    if tfile.exists():
        tdata = get_track(tfile)
        if not tdata:
            return 'move'
        if near(tdata):
            return 'different'
        return 'dupe'

    # Look for a very similar file
    for tfile in tracks:
        if canonical(tfile) != canonical(sfile):
            continue

        td = get_track(tfile)
        if td and near(td) and td.get('Name', '').lower() == sname:
            if tfile.suffix == SUFFIX:
                return 'dupe'

            if sfile.suffix == SUFFIX or ssize > td['Size']:
                return 'move'

            return 'dupe'
    return 'move'


def canonical(f):
    s = f.stem
    parts = s.split()
    if len(parts) > 2:
        if parts[-1].isnumeric():
            parts.pop()
        if parts[0].isnumeric():
            parts.pop(0)
    return ' '.join(parts).lower()


def itunes_directories(source):
    def dir1(f):
        if f.is_dir():
            for g in f.iterdir():
                if g.is_dir():
                    yield g

    music = source / 'Music'
    if music.is_dir():
        for artist in music.iterdir():
            yield from dir1(artist)
    yield from dir1(source / 'Podcasts')
