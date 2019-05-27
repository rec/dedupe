import sys
from . import merge_media


def find_case_issues(source):
    files = {}
    for sfile in merge_media.walk(source):
        sfile = sfile.relative_to(source)
        if sfile.suffix.lower() in merge_media.SUFFIXES:
            files.setdefault(str(sfile).lower(), set()).add(str(sfile))

    for k, v in sorted(files.items()):
        if len(v) > 1:
            print(*sorted(v), sep='\n')
            print()


if __name__ == '__main__':
    issues = find_case_issues(sys.argv[1])
