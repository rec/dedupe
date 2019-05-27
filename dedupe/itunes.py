import attr
import datetime
import plistlib
from .data import Data

KWDS = {'fmt': plistlib.FMT_XML}


class iTunesLibrary:
    def __init__(self, data=None):
        self.data = data
        self.max_track_id = max(int(i) for i in data['Tracks'])

    def update_date(self, date=None):
        self.data['Date'] = date or datetime.datetime.utcnow()


@attr.dataclass
class iTunesLoader(Data):
    loader: object = plistlib
    binary: bool = 'b'
    load_kwds: dict = attr.Factory(lambda: KWDS)
    dump_kwds: dict = attr.Factory(lambda: KWDS)
    maker: object = iTunesLibrary


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET


if __name__ == '__main__':
    import sys

    loader = iTunesLoader(write=True)
    with loader.file_context(sys.argv[1]) as il:
        il.update_date()
