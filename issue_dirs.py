#!/usr/bin/env python3
"""List monthly issues and their explicitly named content versions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def issue_dirs():
    for month in sorted(ROOT.glob('20??-??-*')):
        if (month / 'content.md').is_file():
            yield month.relative_to(ROOT).as_posix()
        for content in sorted(month.glob('versions/*/content.md')):
            yield content.parent.relative_to(ROOT).as_posix()

if __name__ == '__main__':
    print('\n'.join(issue_dirs()))
