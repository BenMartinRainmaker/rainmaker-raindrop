# November 2026 · Anduril

This is the November issue, formerly stored as `2026-10-anduril`. The main content includes market commentary. The alternate take in `versions/without-market-commentary/` omits the Market note and “Amongst the mayhem,” and keeps its refined company-first web layout.

Each take has both normal and email editions. Edit its `content.md` once for both delivery formats. Keep shared factual changes synchronized across the two takes while preserving their intentional introduction/design differences.

```sh
./render.sh 2026-11-anduril
./render.sh 2026-11-anduril/versions/without-market-commentary
```

Normal: `raindrop.html`, `raindrop.pdf` (one page), `preview.png`. Email: `email/raindrop-email.html`, `email/raindrop-email.txt`, raster `email/assets/`. Open `email/preview.html` locally to review images before deployment. Send only production HTML after hosting the assets and client testing.

The email preserves the original one-page print composition, including the initial Fury/AMRAAM photo, as linked PNG sections. Main artwork links to the web edition; the two footer CTAs keep their direct destinations. The separate text file provides the text alternative.

Old URLs are staged as aliases through `url-aliases.json`. Shared instructions are in `../mainguidelines/README.md`.

## Four public HTML editions

| Market sentiment | Normal edition | Email-friendly HTML |
| --- | --- | --- |
| With sentiment | [Web](https://benmartinrainmaker.github.io/rainmaker-raindrop/2026-11-anduril/) | [Email](https://benmartinrainmaker.github.io/rainmaker-raindrop/2026-11-anduril/email/raindrop-email.html) |
| Without sentiment | [Web](https://benmartinrainmaker.github.io/rainmaker-raindrop/2026-11-anduril/versions/without-market-commentary/) | [Email](https://benmartinrainmaker.github.io/rainmaker-raindrop/2026-11-anduril/versions/without-market-commentary/email/raindrop-email.html) |

The email-friendly versions preserve the matching original artwork, including the sentiment paragraph only in the with-sentiment take. These URLs serve the production HTML with hosted PNGs; do not share the local `preview.html`.
