import datetime
import mutagen
import os


MP3 = 'MPEG audio file'
AAC = 'Apple Lossless audio file'

KIND = {'audio/mp2': MP3, 'audio/mp3': MP3, 'audio/mp4': AAC}
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
    if not mf:
        return None

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
    if mf.tags:
        tags = tag_data(mf.tags, kind)
        result.update(tags)

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
        tag_name = tag_names[kind is MP3]
        value = tags.get(tag_name)
        if value:
            value = value[0]
            if name == TRACK_NUMBER:
                if isinstance(value, str):
                    try:
                        value = [int(i) for i in value.split('/')]
                    except Exception:
                        continue
                tn, *tc = value
                if tn > 0:
                    result[TRACK_NUMBER] = tn
                    if tc:
                        tc = tc[0]
                        if tc >= tn:
                            result[TRACK_COUNT] = tc

            elif name == YEAR:
                if isinstance(value, str):
                    value = int(value.split('-')[0])
                if isinstance(value, int):
                    result[YEAR] = value
            else:
                result[name] = value

    return result


def filename_to_track(filename):
    filename = os.path.abspath(os.path.expanduser(filename))
    result = audio_data(filename)
    if result is not None:
        result.update(TRACK_CONSTANTS)
        result.update(file_data(filename))
    return result


def file_to_track(filename, track_id, persistent_id):
    result = filename_to_track(filename)
    if result is not None:
        result.update({'Track ID': track_id, 'Persistent ID': persistent_id})
    return result


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET
