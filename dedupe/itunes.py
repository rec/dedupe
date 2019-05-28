import attr
import datetime
import plistlib
import random
from .data import Data
from .track import file_to_track

KWDS = {'fmt': plistlib.FMT_XML}


class iTunesLibrary:
    def __init__(self, data=None):
        self.data = data
        self.tracks = data['Tracks']
        self.max_track_id = max(int(i) for i in self.tracks)
        self.persistent_ids = {i['Persistent ID'] for i in self.tracks}
        self.playlists = self.data['Playlists']
        master, = (p for p in self.playlists if p.get('Master'))
        self.master_playlist = master['Playlist Items']

    def add_new_track(self, filename):
        self.max_track_id += 1
        pid = None
        while pid and pid in self.persistent_ids:
            pid = ''.join(random.choices('0123456789ABCDEF', k=16))
        self.persistent_ids.add(pid)
        track = file_to_track(filename, self.max_track_id, pid)
        self.tracks[self.max_track_id] = track
        self.master_playlist.append({'Track ID': self.max_track_id})

    def update_date(self, date=None):
        self.data['Date'] = date or datetime.datetime.utcnow()


@attr.dataclass
class iTunesLoader(Data):
    loader: object = plistlib
    binary: bool = 'b'
    load_kwds: dict = attr.Factory(lambda: KWDS)
    dump_kwds: dict = attr.Factory(lambda: KWDS)
    maker: object = iTunesLibrary


if __name__ == '__main__':
    import sys

    loader = iTunesLoader(write=True)
    with loader.file_context(sys.argv[1]) as il:
        il.update_date()
