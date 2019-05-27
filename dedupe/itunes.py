import datetime
import plistlib
from . import data


class iTunesData(data.Data):
    loader = plistlib.load
    dumper = plistlib.load
    BINARY = 'b'
    LOAD_KWDS = DUMP_KWDS = {'fmt': plistlib.FMT_XML}


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET
