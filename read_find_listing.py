from pathlib import Path

IGNORE_DIRS = {
    'Backups.backupdb',
}

IGNORE_FILES = {
    '.DS_Store',
    '.DocumentRevisions-V100',
    '.Spotlight-V100',
    '.TemporaryItems',
    '.Trashes',
    '.VolumeIcon.icns',
    '.com.apple.timemachine.donotpresent',
    '.fseventsd',
}

IGNORE_OS_DIRECTORIES = {
    'Volumes',
    'bin',
    'dev',
    'etc',
    'home',
    'net',
    'opt',
    'private',
    'sbin',
    'tmp',
    'usr',
    'var',
}

USE_PATH = False


def split(path):
    path = path[:-1]
    if USE_PATH:
        path = list(Path(path))
    else:
        path = path.split('/')
    path = path[1:]
    if not path:
        return ['.']
    if not path[-1]:
        path = path[:-1]
    return path


def ignore(path):
    if path[-1] in IGNORE_FILES:
        return True

    if len(path) >= 3 and path[2] in IGNORE_OS_DIRECTORIES:
        return True

    for d in path[:-1]:
        try:
            if d in IGNORE_DIRS or d.startswith('.') or d.endswith('.app'):
                return True
        except:
            import sys
            print('error!', path, d, file=sys.stderr)
            raise

def names_and_depths(files):
    for f in files:
        path = split(f)
        if not ignore(path):
            print(len(path) - 1, path[-1])


if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as files:
        names_and_depths(files)
