#!/usr/bin/env python3
"""Builds a standalone share copy of a month's raindrop.html with every local image
embedded as base64, so the file renders correctly when emailed or opened elsewhere.
Usage:  python3 inline.py 2026-10-anduril  ->  writes <folder>/share/<folder>.html
"""
import base64, mimetypes, os, re, sys
folder = sys.argv[1].rstrip('/')
src = os.path.join(folder, 'raindrop.html')
html = open(src, encoding='utf-8').read()
mimetypes.add_type('image/svg+xml', '.svg')
def embed(m):
    attr, path = m.group(1), m.group(2)
    full = os.path.join(folder, path)
    if path.startswith(('http', 'data:', '#')) or not os.path.exists(full):
        return m.group(0)
    mime = mimetypes.guess_type(full)[0] or 'application/octet-stream'
    data = base64.b64encode(open(full, 'rb').read()).decode()
    return f'{attr}="data:{mime};base64,{data}"'
out = re.sub(r'\b(src|href|xlink:href)="([^"]+)"', embed, html)
out = re.sub(r"url\((['\"]?)(assets/[^'\")]+)\1\)",
             lambda m: 'url("data:%s;base64,%s")' % (mimetypes.guess_type(m.group(2))[0],
                 base64.b64encode(open(os.path.join(folder, m.group(2)), 'rb').read()).decode()), out)
os.makedirs(os.path.join(folder, 'share'), exist_ok=True)
dest = os.path.join(folder, 'share', f'Rainmaker-Raindrop-{folder}.html')
open(dest, 'w', encoding='utf-8').write(out)
left = re.findall(r'(?:src|href)="assets/[^"]+"', out)
print(f'{dest}: {os.path.getsize(dest)//1024} KB, {len(left)} unresolved asset refs')
