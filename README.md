# Rainmaker Raindrops

Rainmaker Securities’ monthly company feature. Each month has an original web layout and two delivery formats: an interactive web edition with a one-page PDF, and a separate email-safe edition that preserves the original composition as linked PNG artwork.

## Project map

```text
AGENTS.md                       instructions for coding agents
CLAUDE.md                       entry point for Claude; points to the same guidelines
mainguidelines/                 shared organization, workflow, design, and email rules
brand/                          shared Rainmaker brand assets
2026-11-anduril/                 November company issue, with commentary
  README.md                     issue notes and output paths
  content.md                    editable content shared by web and email
  template.html                 original issue-specific web design
  assets/                       source logos and photos
  raindrop.html / raindrop.pdf   generated normal edition
  preview.png                   generated normal edition preview
  email/                        generated email HTML, text, PNGs, and local preview
  share/                        generated browser/PDF exports
  versions/
    without-market-commentary/  alternate November take; same output structure
2026-12-ramp/                   December issue; same structure, distinct design
build.py / build_email.py       normal and email generators
render_email_artwork.mjs         captures the original composition without redesign
render.sh                      builds both formats and checks one-page PDF
issue_dirs.py                  lists monthly issues and nested content versions
stage.sh / stage.py             stages both formats for hosting
url-aliases.json                established public URLs retained after moves
.github/workflows/publish.yml   renders and stages all editions on push
```

Read [the main guidelines](mainguidelines/README.md) for the full workflow. New months go in new `YYYY-MM-company/` folders; use `versions/` only for alternate takes of that same issue.

## Build and review

```sh
./render.sh 2026-11-anduril
./render.sh 2026-11-anduril/versions/without-market-commentary
./render.sh 2026-12-ramp --web-only  # email work currently deferred
./stage.sh
```

Open `<issue>/raindrop.html` for the normal edition, `<issue>/raindrop.pdf` for print, and `<issue>/email/preview.html` for a local email review with local images. Import `<issue>/email/raindrop-email.html` into the email platform; it uses absolute HTTPS image URLs. Its images must be deployed before a test send. The email preserves the original one-page composition and scales it proportionally. Visible text is part of the artwork; the text file is its accessible companion.

`EMAIL_ASSET_BASE=https://cdn.example.com/raindrops ./render.sh <issue>` changes the email image host. Upload the generated `<issue>/email/assets/` under the same issue path on that host. The default host is the existing GitHub Pages site, pending any production CDN choice.

The existing November public addresses remain available through staging aliases. Files are prepared locally until published. Browser previews have not been certified in Outlook/Gmail; use a test send through the actual email platform before distribution.
