from .data import Data
from .track import file_to_track
import attr
import datetime
import plistlib
import random
import sys

KWDS = {'fmt': plistlib.FMT_XML}


class iTunesLibrary:
    def __init__(self, data=None):
        self.data = data
        self.playlists = self.data['Playlists']
        master, = (p for p in self.playlists if p.get('Master'))
        self.master_playlist = master['Playlist Items']

        self.id_to_track = data['Tracks']
        self.max_track_id = max(int(i) for i in self.id_to_track)
        self.persistent_ids = {
            i['Persistent ID'] for i in self.id_to_track.values()
        }

        # self.tracks[use_name][is_canonical]
        self.tracks = [[{}, {}], [{}, {}]]

        for track in self.id_to_track.values():
            artist = track['Artist']
            album = track['Album']
            name = track['Name']
            track_number = track['Track Number']

            add(self.tracks[False][False], track, artist, album, track_number)
            add(self.tracks[True][False], track, artist, album, name)

            cartist = canonical(artist)
            calbum = canonical(album)
            cname = canonical(name)

            add(self.tracks[False][True], track, cartist, calbum, track_number)
            add(self.tracks[True][True], track, cartist, calbum, cname)

    def add_new_track(self, filename):
        self.max_track_id += 1
        pid = None
        while (not pid) or pid in self.persistent_ids:
            pid = ''.join(random.choices('0123456789ABCDEF', k=16))
        self.persistent_ids.add(pid)
        track = file_to_track(filename, self.max_track_id, pid)
        self.data['Tracks'][self.max_track_id] = track
        self.master_playlist.append({'Track ID': self.max_track_id})
        return self.max_track_id, pid

    def update_date(self, date=None):
        self.data['Date'] = date or datetime.datetime.utcnow()

    def update_track(self, track):
        pass


def add(tracks, track, artist, album, index):
    artist_albums = tracks.setdefault(artist, {})
    album_tracks = artist_albums.setdefault(album, {})
    album_tracks.setdefault(index, []).append(track)


@attr.dataclass
class iTunesLoader(Data):
    loader: object = plistlib
    binary: bool = 'b'
    load_kwds: dict = attr.Factory(lambda: KWDS)
    dump_kwds: dict = attr.Factory(lambda: KWDS)
    maker: object = iTunesLibrary


def canonical(name, strip_numeric_suffix=False):
    name = name.lower().strip()
    if strip_numeric_suffix:
        *rest, last = name.rsplit(maxsplit=1)
        if rest and last.isnumeric():
            name = ' '.join(rest)
    return name


if __name__ == '__main__':
    loader = iTunesLoader(write=True)
    with loader.file_context(sys.argv[1]) as il:
        il.update_date()
