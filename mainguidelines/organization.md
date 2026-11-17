# Organization

Use one root `YYYY-MM-company/` folder for each month’s company Raindrop. The date describes the issue month, not when production began. November’s Anduril source was previously named `2026-10-anduril`; it now lives in `2026-11-anduril`.

Each month contains `content.md`, its original `template.html`, source `assets/`, and a README. Alternate takes belong in `versions/<descriptive-name>/`, with the same source/output structure. They are not additional monthly issues.

Generated normal outputs are `raindrop.html`, `raindrop.pdf`, and `preview.png`. Browser attachment exports live in `share/`. Email outputs live in `email/`: production `raindrop-email.html`, plain-text companion `raindrop-email.txt`, local-only `preview.html`, and PNG assets. Generated outputs are gitignored and rebuilt in CI. Keep earlier takes in `archive/` (also ignored).

Shared guidance lives in `mainguidelines/`, shared brand assets in `brand/`, and build/staging tools in the root. `issue_dirs.py` lists canonical month folders and their nested versions; both CI and staging use that inventory.

`url-aliases.json` maps old public paths to canonical sources. Staging emits pages, assets, email files, and PDFs at both paths. Browser editing at an alias writes to the canonical content path. Do not create duplicate editable source folders to preserve an old URL. The site root selects the newest main month, not a content version.

Root `index.html` is the local project links page. It includes both Anduril content options in normal/email formats, Ramp’s local normal draft and earlier email draft, PDFs, and guidelines. It is separate from the hosted site root, which retains its newest-issue redirect.
