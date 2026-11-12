#!/bin/bash
# Assembles the website folder site/ from every rendered month: the page with a noindex tag and
# version-stamped image URLs, its assets, and its PDF. The root redirects to the newest month.
# Run by the GitHub Action after render.sh; you can run it locally to check the output.
# Usage:  ./stage.sh            (all months)      ./stage.sh 2026-10-anduril   (just one, into an existing site/)
set -e
cd "$(dirname "$0")"
V=$(date +%s)
DIRS=("$@"); [ ${#DIRS[@]} -eq 0 ] && DIRS=($(ls -d 20*-*/ | sed 's#/$##' | sort))
for DIR in "${DIRS[@]}"; do
  [ -f "$DIR/raindrop.html" ] || { echo "skip $DIR: no raindrop.html (run ./render.sh $DIR first)"; continue; }
  mkdir -p "site/$DIR/assets"
  sed -e 's#<meta name="viewport"#<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"#' \
      -e "s#\(\(src\|href\)=\"assets/[^\"]*\)\"#\1?v=$V\"#g" "$DIR/raindrop.html" > "site/$DIR/index.html"
  # every local image: <img src=...> and the SVG <image href=...> that holds the logo inside the raindrop
  for f in $(grep -o '\(src\|href\)="assets/[^"?]*' "$DIR/raindrop.html" | sed 's#.*="##' | sort -u); do [ -f "$DIR/$f" ] && cp "$DIR/$f" "site/$DIR/assets/"; done
  [ -f "$DIR/raindrop.pdf" ] && cp "$DIR/raindrop.pdf" "site/$DIR/raindrop.pdf"
  LATEST="$DIR"
done
cat > site/index.html <<HTML
<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><meta http-equiv="refresh" content="0; url=$LATEST/"><title>Raindrop of the Month</title><a href="$LATEST/">Raindrop of the Month</a>
HTML
touch site/.nojekyll
echo "site/ staged (latest: $LATEST)"
