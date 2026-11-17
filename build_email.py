#!/usr/bin/env python3
"""Build an email-safe visual match of the original one-page Raindrop.
Usage: python3 build_email.py <issue-folder> [--asset-base https://cdn.example.com/raindrops]
The email uses linked PNG sections, presentation tables, and a plain-text companion.
"""
import argparse
import html
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote,urlsplit
from build import parse,norm,rows

ROOT=Path(__file__).resolve().parent
HOST='https://benmartinrainmaker.github.io/rainmaker-raindrop'
TABLE='role="presentation" cellpadding="0" cellspacing="0" border="0"'


def build_email(folder,asset_base=HOST):
    if urlsplit(asset_base).scheme!='https' or not urlsplit(asset_base).netloc:
        raise ValueError('--asset-base must be an absolute HTTPS URL')
    issue=(ROOT/folder).resolve()
    rel=issue.relative_to(ROOT).as_posix()
    meta,sections=parse((issue/'content.md').read_text())
    out=issue/'email'
    out.mkdir(exist_ok=True)
    subprocess.run(['node',str(ROOT/'render_email_artwork.mjs'),str(issue)],check=True,timeout=90)
    layout=json.loads((out/'artwork-layout.json').read_text())
    web_url=HOST+'/'+quote(rel,safe='/')+'/'
    asset_url=asset_base.rstrip('/')+'/'+quote(rel,safe='/')+'/email/assets/'
    company,month=meta['company'],meta['month']
    display_width=680
    ratio=display_width/layout['width']
    def picture(part,alt,url):
        w=round(part['width']*ratio)
        h=round(part['height']*ratio)
        return (f'<a href="{html.escape(url,quote=True)}" style="text-decoration:none;">'
                f'<img src="{asset_url}{part["file"]}" width="{w}" height="{h}" border="0" '
                f'alt="{html.escape(alt,quote=True)}" style="display:block;border:0;width:100%;height:auto;max-width:{w}px;"></a>')
    bands=''.join('<tr><td style="padding:0;font-size:0;line-height:0;">'+
                  picture(band,f'{company} · {month} Raindrop, section {i+1}. View the full accessible web edition.',web_url)+
                  '</td></tr>' for i,band in enumerate(layout['bands']))
    footer_cells=[]
    allocated=0
    for i,part in enumerate(layout['footer']):
        w=round(part['width']*ratio) if i<len(layout['footer'])-1 else display_width-allocated
        allocated+=w
        percent=part['width']/layout['width']*100
        footer_cells.append(f'<td width="{w}" valign="top" style="padding:0;width:{percent:.6f}%;font-size:0;line-height:0;">'+
                            picture(part,part['alt'],part['href'] or web_url)+'</td>')
    footer=f'<table {TABLE} width="680" style="width:100%;table-layout:fixed;border-collapse:collapse;"><tr>'+''.join(footer_cells)+'</tr></table>'
    email=(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{html.escape(company)} · {html.escape(month)} Raindrop</title></head>'
           '<body style="margin:0;padding:0;background-color:#dfe7ef;">'
           f'<table {TABLE} width="100%" style="width:100%;border-collapse:collapse;"><tr><td align="center" style="padding:0;">'
           '<!--[if mso]><table role="presentation" width="680" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->'
           f'<table {TABLE} width="680" align="center" style="width:100%;max-width:680px;table-layout:fixed;border-collapse:collapse;background-color:#eef5fb;">'+
           bands+'<tr><td style="padding:0;font-size:0;line-height:0;">'+footer+'</td></tr></table>'
           '<!--[if mso]></td></tr></table><![endif]--></td></tr></table></body></html>')
    validate_email(email)
    (out/'raindrop-email.html').write_text(email)
    (out/'preview.html').write_text(email.replace(asset_url,(out/'assets').as_uri()+'/'))
    plain=[f'{company} | {month} Raindrop',f'View online: {web_url}']
    for name,sec in sections.items():
        plain.extend(['',sec['options'].get('title',sec['title'])])
        if name==norm('Photos'):
            plain.append(rows(sec['lines'])[0][2])
        else:
            plain.extend(line for line in sec['lines'] if line.strip())
        for sub in sec['subs']:
            plain.append(re.sub(r'\s*\([a-z]+\)\s*$','',sub['title']))
            plain.extend(line for line in sub['lines'] if line.strip())
        if sec['options'].get('reported'):
            plain.append('Reported, unconfirmed: '+sec['options']['reported'])
        if sec['options'].get('caption'):
            plain.append(sec['options']['caption'])
    plain.extend(['','Trade on Rainmaker X: https://www.rainmaker-x.com/login','Rainmaker Securities: https://www.rainmakersecurities.com/'])
    plain_text='\n'.join(plain).replace('**','')
    plain_text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',plain_text)
    (out/'raindrop-email.txt').write_text(plain_text+'\n')
    print(f'{rel}/email/raindrop-email.html: {len(email.encode()):,} bytes; original composition preserved')


def validate_email(email):
    from html.parser import HTMLParser
    class Check(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag in ('script','svg','iframe','form','input','link'):
                raise ValueError(f'Forbidden email element: {tag}')
            if any(k.startswith('on') or k.startswith('data-ed') or k.lower()=='contenteditable' for k in a):
                raise ValueError('Browser editing or event handler found in email')
            if tag == 'table' and any(a.get(k) != v for k,v in [('role','presentation'),('cellpadding','0'),('cellspacing','0'),('border','0')]):
                raise ValueError('Table missing email presentation attributes')
            if tag == 'img':
                if not a.get('src','').startswith('https://') or any(k not in a for k in ('width','height','border','alt')):
                    raise ValueError('Image needs HTTPS URL, dimensions, border, and alt text')
                if not a['src'].endswith('.png'):
                    raise ValueError('Email images must be PNG')
    Check().feed(email)
    for pattern in (r'display\s*:\s*(?:grid|flex)',r'var\(',r'position\s*:',r'object-fit',r'@page',r'@media\s+print',r'localStorage',r'content-md',r'edit-cfg',r'gradient\(',r'\d(?:d?vh|in)\b'):
        if re.search(pattern,email,re.I):
            raise ValueError(f'Forbidden browser feature: {pattern}')
    if len(email.encode()) > 100_000:
        raise ValueError('Email HTML exceeds 100KB; reduce markup before sending')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder')
    parser.add_argument('--asset-base',default=os.environ.get('EMAIL_ASSET_BASE',HOST))
    args=parser.parse_args()
    build_email(args.folder,args.asset_base)
