from pathlib import Path


def fix_directory_structure(source):
    items = albums = 0
    for artist in (source / 'Music').iterdir():
        for album in artist.iterdir():
            sub = album / album.name
            if sub.exists():
                albums += 1
                # print('Found', album.relative_to(source))
                for f in sub.iterdir():
                    print('Renaming', f, 'to', album / f.name)
                    f.rename(album / f.name)
                    items += 1
                sub.rmdir()
    print('items', items, 'albums', albums)


if __name__ == '__main__':
    fix_directory_structure(Path('/Volumes/Matmos/dedupe/Media-move'))
