# Bundled Jost fonts

These are the original Jost weights used in the Raindrops: normal 400, 500, 600, 700, and italic 400, downloaded from Google Fonts (Jost v20). The SIL Open Font License is included in `OFL.txt`.

`build.py` copies these files into each issue's generated assets, adds local font faces and preload links, and removes the external Google Fonts request. The issue copies are generated and gitignored; staging includes them through their preload references.

The email artwork renderer explicitly loads every required weight before capturing. It fails rather than silently capturing a fallback font. The email itself contains PNG artwork, with no web-font dependency.

Original font stylesheet: https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap
