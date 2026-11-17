#!/bin/bash
# Renders a month's raindrop.html to raindrop.pdf and preview.png, checks the PDF is one page,
# and writes browser share exports plus a separate table-based email edition.
# Usage: ./render.sh <issue-folder> [--web-only]
# --web-only preserves any existing email draft while rendering the normal edition.
# If the folder has a content.md, raindrop.html is rebuilt from it first (build.py + template.html).
set -e
DIR="${1:?usage: ./render.sh <issue-folder>}"
DIR="${DIR%/}"
SLUG="${DIR//\//-}"
WEB_ONLY=false
if [ "${2:-}" = "--web-only" ]; then WEB_ONLY=true; elif [ -n "${2:-}" ]; then echo "Unknown option: $2" >&2; exit 2; fi
# Chrome: the Mac app locally, google-chrome on the GitHub Actions runner (Linux needs --no-sandbox).
CHROME="${CHROME:-$(command -v google-chrome || command -v google-chrome-stable || echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")}"
FLAGS=(--headless=new --disable-gpu --virtual-time-budget=6000); [ "$(uname)" = Linux ] && FLAGS+=(--no-sandbox)
cd "$(dirname "$0")"
ROOT="$PWD"
export CHROME
[ -f "$DIR/content.md" ] && python3 build.py "$DIR"   # words live in content.md; design in template.html
cd "$DIR"
"$CHROME" "${FLAGS[@]}" --no-pdf-header-footer --print-to-pdf="$PWD/raindrop.pdf" "file://$PWD/raindrop.html" 2>/dev/null
"$CHROME" "${FLAGS[@]}" --hide-scrollbars --window-size=1120,1500 --screenshot="$PWD/preview.png" "file://$PWD/raindrop.html" 2>/dev/null
PAGES=$(python3 -c "import re;print(len(re.findall(rb'/Type\s*/Page[^s]',open('raindrop.pdf','rb').read())))")
echo "raindrop.pdf: $PAGES page(s)   preview.png written"
(cd "$ROOT" && python3 inline.py "$DIR")   # standalone share copy with images embedded
cp raindrop.pdf "share/Rainmaker-Raindrop-$SLUG.pdf"
# Package current outputs, including SVG-referenced logo images.
python3 - "$ROOT" "$DIR" "$SLUG" <<'PACKAGE'
from pathlib import Path
import re, sys, zipfile
root, folder, slug = sys.argv[1:]
issue = Path(root)/folder
refs = re.findall(r'(?:src|href)="(assets/[^"?]+)', (issue/'raindrop.html').read_text())
with zipfile.ZipFile(issue/'share'/f'Rainmaker-Raindrop-{slug}-web.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name in ['raindrop.html', 'raindrop.pdf'] + sorted(set(refs)):
        z.write(issue/name, f'{folder}/{name}')
PACKAGE
if [ "$WEB_ONLY" = false ]; then (cd "$ROOT" && python3 build_email.py "$DIR"); fi
[ "$PAGES" = "1" ] || { echo "WARNING: PDF is longer than one page. Trim text or spacing."; exit 1; }
