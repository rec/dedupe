from pathlib import Path
import shutil


def rmdir_empty(f):
    """Returns a count of the number of directories it has deleted"""
    if not f.is_dir():
        return 0
    removable = True
    result = 0
    for i in f.iterdir():
        if i.is_dir():
            result += rmdir_empty(i)
            removable = removable and not i.exists()
        else:
            removable = removable and (i.name == '.DS_Store')
    if removable:
        items = list(f.iterdir())
        assert not items or items[0].name == '.DS_Store'
        print(f)
        shutil.rmtree(f)
        result += 1

    return result


if __name__ == '__main__':
    rmdir_empty(Path('/Volumes/Matmos/dedupe'))
