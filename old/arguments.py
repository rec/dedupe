import argparse
import files

ADD_HELP = 'A comma-separated list of file roots to add'
HEADER_HELP = 'Compute file headers hashes from sizes'
CONTENTS_HELP = 'Compute contents hashes headers from header hashes'


def parse_arg(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', help=ADD_HELP, default=None)
    parser.add_argument('--header', help=HEADER_HELP, action='store_true')
    parser.add_argument('--contents', help=CONTENTS_HELP, action='store_true')
    parser.add_argument(
        '-v', '--verbose', help='Print each file', action='store_true'
    )
    parser.add_argument(
        '--data', help='Name of data directory', default=files.DATA_DIR
    )
    parser.add_argument('--exclude', help=HEADER_HELP, default='')
    parser.add_argument(
        '-c',
        '--clear',
        help='Clear files before starting',
        action='store_true',
    )

    return parser.parse_args(argv)
