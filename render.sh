#!/bin/bash
# Renders a month's raindrop.html to raindrop.pdf and preview.png, checks the PDF is one page,
# and writes share/<name>.html with all images embedded (send that one, not raindrop.html).
# Usage:  ./render.sh 2026-10-anduril
# If the folder has a content.md, raindrop.html is rebuilt from it first (build.py + template.html).
set -e
DIR="${1:?usage: ./render.sh <month-folder>}"
# Chrome: the Mac app locally, google-chrome on the GitHub Actions runner (Linux needs --no-sandbox).
CHROME="${CHROME:-$(command -v google-chrome || command -v google-chrome-stable || echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")}"
FLAGS=(--headless=new --disable-gpu --virtual-time-budget=6000); [ "$(uname)" = Linux ] && FLAGS+=(--no-sandbox)
cd "$(dirname "$0")"
[ -f "$DIR/content.md" ] && python3 build.py "$DIR"   # words live in content.md; design in template.html
cd "$DIR"
"$CHROME" "${FLAGS[@]}" --no-pdf-header-footer --print-to-pdf="$PWD/raindrop.pdf" "file://$PWD/raindrop.html" 2>/dev/null
"$CHROME" "${FLAGS[@]}" --hide-scrollbars --window-size=1120,1500 --screenshot="$PWD/preview.png" "file://$PWD/raindrop.html" 2>/dev/null
PAGES=$(python3 -c "import re;print(len(re.findall(rb'/Type\s*/Page[^s]',open('raindrop.pdf','rb').read())))")
echo "raindrop.pdf: $PAGES page(s)   preview.png written"
(cd .. && python3 inline.py "$DIR")   # standalone share copy with images embedded
cp raindrop.pdf "share/Rainmaker-Raindrop-$DIR.pdf"
# Website zip: page + images + PDF only (nothing else from the project), built from site/ if published, else from here.
rm -f "share/Rainmaker-Raindrop-$DIR-web.zip"
if [ -d "../site/$DIR" ]; then (cd ../site && zip -q -r -X "../$DIR/share/Rainmaker-Raindrop-$DIR-web.zip" "$DIR" -x '*.DS_Store'); \
else (cd .. && zip -q -X "$DIR/share/Rainmaker-Raindrop-$DIR-web.zip" "$DIR/raindrop.html" "$DIR/raindrop.pdf" $(grep -o 'src="assets/[^"]*' "$DIR/raindrop.html" | sed "s#src=\"#$DIR/#" | sort -u)); fi
[ "$PAGES" = "1" ] || { echo "WARNING: PDF is longer than one page. Trim text or spacing."; exit 1; }
