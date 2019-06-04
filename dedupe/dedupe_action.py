"""
Ascertain if two files with nearly equal names are actually the same.
"""

from . import files

SUFFIX = '.m4a'


def dedupe_action(src, target):
    """Return a tuple (action, *files) where action is one of
       'ignore', 'move', or 'replace'
    """
    if target.exists() or target.with_suffix(SUFFIX).exists():
        return ('ignore',)

    if not target.parent.exists():
        return ('move',)

    # There might be something in that directory that's the same file or better

    ct = canonical(target)
    matches = [f for f in target.parent.iterdir() if canonical(f) == ct]
    if not matches:
        return ('move',)

    if any(m.suffix == SUFFIX for m in matches):
        return ('ignore',)

    if target.suffix != SUFFIX:
        fs = files.size(src)
        if not all(fs > files.size(m) for m in matches):
            return ('ignore',)

    return ('replace', *matches)


def canonical(f):
    s = f.stem
    parts = s.split()
    if len(parts) > 1:
        if parts[-1].isnumeric():
            parts.pop()
        if parts[0].isnumeric():
            parts.pop(0)
    return ' '.join(parts)
