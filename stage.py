#!/usr/bin/env python3
"""Stage monthly web/email editions and preserve established URLs after reorganization."""
import html
import json
import re
import shutil
import sys
import time
from issue_dirs import ROOT, issue_dirs

site = ROOT/'site'
site.mkdir(exist_ok=True)
stamp = str(int(time.time()))
folders = sys.argv[1:] or list(issue_dirs())
latest = None
for folder in folders:
    source = ROOT/folder
    dest = site/folder
    web = source/'raindrop.html'
    if not web.is_file():
        raise SystemExit(f'{folder}: run ./render.sh first')
    dest.mkdir(parents=True, exist_ok=True)
    text = web.read_text().replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"')
    text = re.sub(r'((?:src|href)="assets/[^"?]+)"', lambda m:m.group(1)+'?v='+stamp+'"', text)
    (dest/'index.html').write_text(text)
    (dest/'assets').mkdir(exist_ok=True)
    for name in set(re.findall(r'(?:src|href)="(assets/[^"?]+)',web.read_text())):
        shutil.copyfile(source/name, dest/name)
    if (source/'raindrop.pdf').is_file():
        shutil.copyfile(source/'raindrop.pdf',dest/'raindrop.pdf')
    email = source/'email'
    if not (email/'raindrop-email.html').is_file():
        raise SystemExit(f'{folder}: missing email edition; run ./render.sh first')
    target = dest/'email'
    target.mkdir(exist_ok=True)
    for name in ('raindrop-email.html','raindrop-email.txt'):
        shutil.copyfile(email/name,target/name)
    shutil.copytree(email/'assets',target/'assets',dirs_exist_ok=True)
    if '/' not in folder:
        latest = folder

# Serve legacy URLs directly: query parameters and editor paths remain functional.
for alias, canonical in json.loads((ROOT/'url-aliases.json').read_text()).items():
    source = site/canonical
    if not (source/'index.html').is_file():
        continue
    dest = site/alias
    dest.mkdir(exist_ok=True)
    shutil.copyfile(source/'index.html',dest/'index.html')
    shutil.copytree(source/'assets',dest/'assets',dirs_exist_ok=True)
    if (source/'raindrop.pdf').is_file():
        shutil.copyfile(source/'raindrop.pdf',dest/'raindrop.pdf')
    shutil.copytree(source/'email',dest/'email',dirs_exist_ok=True)

if latest:
    (site/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><meta http-equiv="refresh" content="0; url={html.escape(latest)}/"><title>Raindrop of the Month</title><a href="{html.escape(latest)}/">Raindrop of the Month</a>')
(site/'.nojekyll').touch()
print(f'site/ staged: {len(folders)} editions, web + email, with legacy URL aliases')
