import attr
import datetime
import plistlib
from . import data

KWDS = {'fmt': plistlib.FMT_XML}


@attr.dataclass
class iTunesData(data.Data):
    loader: object = plistlib
    binary: bool = 'b'
    load_kwds: dict = attr.Factory(lambda: KWDS)
    dump_kwds: dict = attr.Factory(lambda: KWDS)


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET
