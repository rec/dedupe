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


if __name__ == '__main__':
    if False:
        source = '/Volumes/Matmos/iTunes-move'
        target = '/Volumes/Matmos/Media'
        merge(source, target)

    if True:
        source = '/Volumes/Matmos/iTunes-dupes'
        target = '/Volumes/Matmos/Media'
        merge(source, target)
