from pathlib import Path
import shutil


def merge(source, target):
    source, target = Path(source), Path(target)

    def merge(s):
        if s.is_dir():
            for i in s.iterdir():
                merge(i)
        else:
            t = target / s.relative_to(source)
            if not t.exists():
                # t.parent.mkdir(exist_ok=True, parents=True)
                print('move', s, t)
                shutil.move(s, t)

    merge(source)


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
    if True:
        # print(rmdir_empty(Path('/Volumes/Matmos/iTunes-move')))
        print(rmdir_empty(Path('/Volumes/Matmos/iTunes-dupes')))

    if False:
        source = '/Volumes/Matmos/iTunes-move'
        target = '/Volumes/Matmos/Media'
        merge(source, target)

    if True:
        source = '/Volumes/Matmos/iTunes-dupes'
        target = '/Volumes/Matmos/Media'
        merge(source, target)
