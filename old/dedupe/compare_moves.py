from pathlib import Path
import shutil
import webbrowser


def compare_moves(source, target):
    keep_dir = source.with_name('%s-keep' % source.name)
    discard_dir = source.with_name('%s-discard' % source.name)
    for i in (source / 'Music').iterdir():
        if i.name.startswith('.'):
            continue
        for sfile in i.iterdir():
            if sfile.name.startswith('.'):
                continue
            srel = sfile.relative_to(source)
            tfile = target / srel
            webbrowser.open('file://%s' % tfile)
            webbrowser.open('file://%s' % sfile)

            prompt = 'Keep %s? (yN) ' % srel
            keep = (input(prompt).strip().lower() or 'n')[0]
            mfile = (keep_dir if keep != 'n' else discard_dir) / srel
            if not True:
                print('move', sfile, mfile)
                return
            else:
                mfile.mkdir(exist_ok=True, parents=True)
                shutil.move(str(sfile), str(mfile))


if __name__ == '__main__':
    source = Path('/Volumes/Matmos/dedupe/Media-move')
    target = Path('/Volumes/Matmos/iTunes')
    compare_moves(source, target)
