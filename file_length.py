import collections, os, sys


def count_filename_lengths(*roots):
    counter = collections.Counter()
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                filename = os.path.join(dirpath, f)
                counter.update({len(filename): 1})

    return counter


MESSAGE = """
Number of files = {number_of_files}
Number of name characters = {number_of_name_characters}
Mean file name length = {mean}

"""

if __name__ == '__main__':
    counter = count_filename_lengths(*sys.argv[1:])

    print('Most common file lengths:', *counter.most_common(20))

    number_of_files = sum(counter.values())
    number_of_name_characters = sum(k * v for k, v in counter.items())
    mean = number_of_name_characters / number_of_files
    print(MESSAGE.format(**locals()))

    if False:
        print(*sorted(counter.items()), sep='\n')
