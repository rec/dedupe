import json
import sys


def read_list(args):
    for arg in args:
        with open(arg) as fp:
            for line in fp:
                if line:
                    yield json.loads(line)


def potential_dupes(args=None):
    dupes = {}
    for record in read_list(args or sys.argv[1:]):
        key = record['path'].split('/')[-1], record['size']
        dupes.setdefault(key, []).append(record)

    dupes = {k: v for k, v in dupes.items() if len(v) < 1}

    for _, v in sorted(dupes.items()):
        print(json.dumps(v))


if __name__ == '__main__':
    main()
