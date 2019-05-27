import hashlib
import os
import sys


def filesize(filename):
    return os.path.isfile(filename) and os.stat(filename).st_size or 0


def filehash(filename):
    hasher = hashlib.sha1()
    hasher.update(open(filename, 'rb').read())
    return hasher.hexdigest()


def are_same(f1, f2):
    return filesize(f1) == filesize(f2) and filehash(f1) == filehash(f2)


def remove_empty_directories(root):
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for f in filenames:
            if f == '.DS_Store':
                os.remove(os.path.join(dirpath, f))

        for d in dirnames:
            directory = os.path.join(dirpath, d)
            if not os.listdir(directory):
                try:
                    os.rmdir(directory)
                    removed += 1
                except Exception:
                    print('ERROR: cannot remove directory', directory)

    return removed


EXTENSIONS = '.mp3', '.wav', '.aif', '.aiff', '.wave', '.flac', '.m4a'


def merge_directories(
    source, target, trash, *, rename=os.rename, makedirs=os.makedirs
):
    results = {}
    for dirpath, dirnames, filenames in os.walk(source, topdown=False):
        relative_path = os.path.relpath(dirpath, source)
        target_path = os.path.join(target, relative_path)
        trash_path = os.path.join(trash, relative_path)
        makedirs(target_path, exist_ok=True)

        for file in filenames:
            if os.path.splitext(file)[1].lower() not in EXTENSIONS:
                continue
            source_file = os.path.join(dirpath, file)
            target_file = os.path.join(target_path, file)
            trash_file = os.path.join(trash_path, file)

            if not os.path.exists(target_file):
                rename(source_file, target_file)
                result = 'rename'

            elif are_same(source_file, target_file):
                makedirs(trash_path, exist_ok=True)
                rename(source_file, trash_file)
                result = 'trash '

            else:
                result = 'ERROR '

            fname = os.path.join(relative_path, file)
            results[result] = 1 + results.get(result, 0)
            try:
                print(result, fname)
            except UnicodeEncodeError:
                try:
                    print(result, fname.encode('utf-8'))
                except UnicodeEncodeError:
                    print('***', result, '<cannot read unicode>')

    print()
    print('Removed', remove_empty_directories(source), 'empty directories')
    for result, count in sorted(results.items()):
        print(result, count)


def fake_rename(source, target):
    print('rename', source, target)


def fake_makedirs(name, exist_ok=False):
    pass


if __name__ == '__main__':
    if not True:
        merge_directories(
            *sys.argv[1:], rename=fake_rename, makedirs=fake_makedirs
        )
    else:
        merge_directories(*sys.argv[1:])
