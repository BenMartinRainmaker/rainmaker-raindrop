# Raindrop project instructions

Read `mainguidelines/README.md` before editing. It links the current organization, workflow, brand/editorial rules, and email requirements. These instructions supersede historical notes.

## Monthly cadence and original design

- Ben produces one company Raindrop each month.
- Each month lives in one `YYYY-MM-company/` folder. Alternate content takes belong in its `versions/<name>/` subfolders, not separate month folders.
- Each monthly issue needs an original company-specific web layout in its own `template.html`. Reuse brand assets and build tools; create a fresh composition, section arrangement, and visual hierarchy.
- Preserve earlier issues’ designs. Keep Rainmaker Securities as publisher and Rainmaker X in the trade CTA.

## Two delivery formats for every issue and content version

- Normal edition: generated `raindrop.html`, exactly one-page US Letter `raindrop.pdf`, and `preview.png`.
- Email edition: generated `email/raindrop-email.html`, `email/raindrop-email.txt`, and raster `email/assets/`; `email/preview.html` is local review only.
- Both formats use the same `content.md`. Never hand-edit generated files.
- The email-safe version must be visually identical to the normal version, or as close as technically possible (Ben’s standing requirement). Use the normal desktop browser design as the visual reference, NOT the print/PDF layout. Preserve its screen fonts, sizes, spacing, and stacked Trade/Visit buttons as linked PNG sections inside presentation tables. Do not redesign it as a scrolling live-text newsletter. Fonts, spacing, photos, chart, and all other visible content come from the original artwork. Keep an accessible plain-text companion and link the artwork to the web edition.
- No email scripts, editor metadata, SVG, grid, flexbox, absolute/sticky positioning, CSS variables, web fonts, carousel controls, print CSS, or page-height constraints. Email scales the original screen artwork proportionally; only the PDF has a physical one-page requirement.
- Use each company’s existing original composition verbatim. Email contains static artwork, not browser share HTML. Keep the trade and Rainmaker website buttons as separate clickable image sections.
- Use bundled Jost fonts and verify all required weights have loaded before email artwork capture; never silently capture a fallback font. Browser email previews expand up to 1280px on wide screens while base email markup remains 680px.
- Keep root `index.html` current with local editions, public links, and draft/deferred labels.
- Use vision-based inspection of actual rendered screenshots to compare the email against the normal edition at the same display size. Check composition, typography, spacing, colors, images, chart, and footer; correct visible differences before delivery. Code checks and geometry checks alone are insufficient.
- Run `./render.sh <issue-folder>` and inspect the PDF plus desktop/mobile email previews. The builder checks email markup. Browser review does not establish Outlook/Gmail compatibility; actual client test sends are a delivery check.
- Stage with `./stage.sh`; keep old public URLs working through `url-aliases.json`. Deploy assets before using production email HTML. `EMAIL_ASSET_BASE` may point to an approved HTTPS CDN.
- Do not send emails or messages without explicit authorization.

## Current issues

- `2026-11-anduril/`: November 2026 with market commentary. Its old public path `2026-10-anduril/` remains a staging alias.
- `2026-11-anduril/versions/without-market-commentary/`: November without the Market note or “Amongst the mayhem,” with its refined company-first web design. Keep those intentional differences. Apply shared factual corrections to both takes. Its old public path remains an alias too.
- `2026-12-ramp/`: December 2026, with its own original design. Current work is on the normal edition only; defer email changes until Ben requests them. Keep existing email drafts, but do not treat them as current or approved while the normal design evolves.

Keep the root README, main guidelines, and affected issue READMEs current when changing the workflow or organization. Archive earlier takes within the issue instead of deleting them.
