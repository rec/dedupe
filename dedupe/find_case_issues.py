import pprint
from . import merge_media


def find_case_issues(root):
    files = {}
    for sfile in merge_media.walk(source):
        if sfile.suffix.lower() in merge_media.SUFFIXES:
            files.setdefault(str(sfile).lower(), set()).add(str(sfile))

    return {k: v for k, v in files.items() if len(v) > 1}


if __name__ == '__main__':
    pprint.pprint(find_case_issues(sys.argv[1]))
