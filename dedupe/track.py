import datetime
import mutagen
import os

KIND = {
    'audio/mp3': 'MPEG audio file',
    'audio/mp4': 'Apple Lossless audio file',
}

FILE_TYPE = 1295270176
YEAR_TAGS = '©day', 'TXXX:originalyear'


def file_to_track(filename, track_id, persistent_id):
    filename = os.path.abspath(os.path.expanduser(filename))

    mf = mutagen.File(filename)
    for m in mf.mime:
        kind = KIND.get(m)
        if kind:
            break
    else:
        raise ValueError('Cannot understand mime type', mf.mime[0])

    # I discovered this by trial and error - I don't know if it's
    # guaranteed to work or not
    name, artist, _, album = [v[0] for v in mf.values[:4]]
    stat = os.stat(filename)
    mtime = datetime.datetime.utcfromtimestamp(stat.st_mtime)

    result = {
        'File Type': FILE_TYPE,
        'Library Folder Count': -1,
        'Track Type': 'File',
        'Unplayed': True,
        'Track ID': track_id,
        'Persistent ID': persistent_id,
        'Name': name,
        'Album': album,
        'Artist': artist,
        'Kind': kind,
        'Bit Rate': mf.info.bitrate,
        'Sample Rate': mf.info.sample_rate,
        'Total Time': round(mf.info.length * 1000),
        'Date Added': datetime.datetime.utcnow(),
        'Date Modified': mtime,
        'Location': 'file:/' + filename,
        'Size': stat.st_size,
        # We don't add these fields
        #   'File Folder Count'
        #   'Genre'
        #   'Play Count'
        #   'Play Date UTC'
        #   'Play Date'
        #   'Track Count'
        #   'Track Number'
    }

    for yt in YEAR_TAGS:
        year = mf.tags.get(yt)
        if year:
            result['Year'] = int(yt)
        break
    return result


# See http://www.joabj.com/Writing/Tech/Tuts/Java/iTunes-PlayDate.html
# This is record['Play Date'] - record['Play Date UTC'].timestamp()
PLAY_DATE_OFFSET = 2082852000


def set_play_date(track, date):
    assert isinstance(date, datetime.datetime)
    track['Play Date UTC'] = date
    track['Play Date'] = date.timestamp() + PLAY_DATE_OFFSET
