import datetime
import mutagen
import os


MP3 = 'MPEG audio file'
AAC = 'Apple Lossless audio file'

KIND = {'audio/mp3': MP3, 'audio/mp4': AAC}
FILE_TYPE = 1295270176
TRACK_NUMBER = 'Track Number'
TRACK_COUNT = 'Track Count'
YEAR = 'Year'

FIELDS = {
    'Name': ('©nam', 'TIT2'),
    'Artist': ('©ART', 'TPE1'),
    'Album': ('©alb', 'TALB'),
    TRACK_NUMBER: ('trkn', 'TRCK'),
    YEAR: ('©day', 'TXXX:originalyear'),
}

TRACK_CONSTANTS = {
    'File Type': FILE_TYPE,
    'File Folder Count': 5,
    'Library Folder Count': -1,
    'Track Type': 'File',
    'Unplayed': True,
}


def audio_data(filename):
    mf = mutagen.File(filename)
    for m in mf.mime:
        kind = KIND.get(m)
        if kind:
            break
    else:
        raise ValueError('Cannot understand mime type', mf.mime[0])
    result = {
        'Kind': kind,
        'Bit Rate': mf.info.bitrate,
        'Sample Rate': mf.info.sample_rate,
        'Total Time': round(mf.info.length * 1000),
    }
    result.update(tag_data(mf.tags, kind))
    return result


def file_data(filename):
    stat = os.stat(filename)
    mtime = datetime.datetime.utcfromtimestamp(stat.st_mtime)
    return {
        'Date Added': datetime.datetime.utcnow(),
        'Date Modified': mtime,
        'Location': 'file:/' + filename,
        'Size': stat.st_size,
    }


def tag_data(tags, kind):
    result = {}

    for name, tag_names in FIELDS.items():
        value = tags.get(tag_names[kind is AAC])
        if value:
            if name == TRACK_NUMBER:
                if isinstance(value, str):
                    value = value.split('/')
                if not isinstance(value, (tuple, list)):
                    print('unexpected ONE', value)
                    continue
                if len(value) != 2:
                    print('unexpected TWO', value)
                    continue
                result[TRACK_NUMBER], result[TRACK_COUNT] = value
                assert 1 <= result[TRACK_NUMBER] <= result[TRACK_COUNT]

            elif name == YEAR:
                if isinstance(value, str):
                    value = int(value.split('-')[0])
                if isinstance(value, int):
                    result[YEAR] = value
            else:
                result[name] = value
    return result


def file_to_track(filename, track_id, persistent_id):
    filename = os.path.abspath(os.path.expanduser(filename))
    print(filename)

    result = audio_data(filename)
    result.update(TRACK_CONSTANTS)
    result.update({'Track ID': track_id, 'Persistent ID': persistent_id})
    result.update(file_data(filename))

    return result


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET
