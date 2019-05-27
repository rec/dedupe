import json
import math

BEGIN = '[\n'
SAMPLE = '    {"this": "is", "sixty four": "bytes", "wide": "why not???"},\n'
END = '      0]\n'
LENGTH = 40000000


def write_big_file(fp, length):
    fp.write(BEGIN)

    sample_length = length - len(BEGIN) - len(END)
    sample_count = int(math.ceil(sample_length / len(SAMPLE)))

    for i in range(sample_count):
        fp.write(SAMPLE)

    fp.write(END)


with open('bigfile.json', 'w') as fp:
    write_big_file(fp, LENGTH)


with open('bigfile-out.json', 'w') as fp_out:
    with open('bigfile.json') as fp_in:
        json.dump(json.load(fp_in), fp_out)
