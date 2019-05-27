import attr
import contextlib
import json
import os
import shutil
import sys


@attr.dataclass
class Data:
    load_kwds: dict = attr.Factory(dict)
    dump_kwds: dict = attr.Factory(dict)
    binary: bool = False
    backup: bool = True
    write: bool = False
    loader: object = json
    output_file: object = sys.stdout
    maker: object = lambda x: x

    def load(self, filename):
        with open(filename, 'rb' if self.binary else 'r') as fp:
            return self.loader.load(fp, **self.load_kwds)

    def dump(self, data, filename):
        with open(filename, 'wb' if self.binary else 'w') as fp:
            self.loader.dump(data, fp, **self.dump_kwds)

    @contextlib.contextmanager
    def file_context(self, filename):
        data = self.load(filename)
        yield self.maker(data)
        if not self.write:
            return

        if self.backup:
            bak_name = nonexistent_filename(filename + '.bak')
            shutil.move(filename, bak_name)
            self._print('Backed up as', bak_name)
        else:
            bak_name = None

        try:
            self.dump(data, filename)
            self._print('Written', filename)
        except Exception:
            self._print('Failed to write', filename)
            try:
                os.remove(filename)
            except Exception:
                self._print('Failed to remove', filename)
            if self.backup:
                try:
                    shutil.move(bak_name, filename)
                    self._print('Restored from', bak_name)
                except Exception:
                    self._print('Failed to restore', bak_name)
            else:
                self._print('No backup for', filename)

            raise

    def _print(self, *args):
        print(*args, file=self.output_file)


def nonexistent_filename(filename):
    result = filename
    tries = 1
    while os.path.exists(result):
        tries += 1
        result = '%s-%d' % (filename, tries)

    return result
