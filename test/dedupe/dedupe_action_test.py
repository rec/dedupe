from dedupe import dedupe_action
from pathlib import Path
import unittest


def canonical(f):
    return dedupe_action.canonical(Path(f))


class CanonicalTest(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(canonical('foo/bar/baz.mp3'), 'baz')
        self.assertEqual(canonical('foo/bar/10 baz.mp3 3'), 'baz')
        self.assertEqual(canonical('foo/bar/10 baz 1.mp3 3'), 'baz')
        self.assertEqual(canonical('foo/bar/baz 1.mp3 3'), 'baz')
        self.assertEqual(canonical('foo/bar/foo baz 1.mp3 3'), 'foo baz')
        self.assertEqual(canonical('foo/bar/foo 1 baz.mp3 3'), 'foo 1 baz')
        self.assertEqual(canonical('foo/bar/1 foo baz.mp3 3'), 'foo baz')
