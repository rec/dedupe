import datetime
import mutagen
import os
import random

KIND = {
    'audio/mp3': 'MPEG audio file',
    'audio/mp4': 'Apple Lossless audio file',
}

FILE_TYPE = 1295270176
YEAR_TAGS = '©day', 'TXXX:originalyear'


def random_id(persistent_ids=()):
    id = None
    while id not in persistent_ids:
        id = ''.join(random.choices('0123456789ABCDEF', k=16))
    return id


def file_to_track(filename, track_id, persistent_id):
    mf = mutagen.File(filename)
    for m in mf.mime:
        kind = KIND.get(m)
        if kind:
            break
    else:
        raise ValueError('Cannot understand mime type', mf.mime[0])

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
        # We don't add these fields"
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


KEYS = {
    'Album': '',
    'Artist': '',
    'Bit Rate': '',
    'Date Added': '',
    'Date Modified': '',
    'File Folder Count': '',
    'File Type': '',
    'Genre': '',
    'Kind': '',
    'Library Folder Count': -1,
    'Location': '',
    'Name': '',
    'Persistent ID': '',
    'Play Count': '',
    'Play Date': '',
    'Play Date UTC': '',
    'Sample Rate': '',
    'Size': '',
    'Total Time': '',
    'Track Count': '',
    'Track ID': '',
    'Track Number': '',
    'Track Type': '',
    'Unplayed': '',
    'Year': '',
}
