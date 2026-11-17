# Email standard

Ken Anderson’s technical requirements still apply: email must contain presentation tables, literal inline styles, PNG images with HTTPS URLs and explicit dimensions, and no browser-only features.

Ben’s November 17 correction takes precedence over the earlier live-text newsletter design: **the email-safe version must be visually identical to the normal edition, or as close as technically possible.** Do not change its layout, type, density, colors, section order, or proportions to fit a generic email template.

## Visual-match implementation

`render_email_artwork.mjs` opens the normal edition in Chrome at a 1280px desktop viewport with SCREEN media and its original fonts. It unrolls the inner scroller without changing content widths, typography, or footer direction, then captures contiguous PNG sections at twice the screen pixel resolution. Never use print media or the PDF layout as the email reference. No image generation or restyling takes place. Section boundaries share the same pixel grid, so the artwork reassembles without gaps or overlaps.

`build_email.py` places those sections in a 680px fluid presentation table. Main artwork links to the full web edition. The footer is split into aligned columns and nested image rows so the original Trade on Rainmaker X and Visit Rainmaker Securities buttons retain their direct links AND their original orientation. For Anduril, Trade must be above Visit, never beside it. All other visible source and gallery links are reached through the web edition. No image map, overlay, JavaScript, SVG, CSS layout system, custom font request, gradient, or print CSS is delivered in email.

The single initial product photo remains visible as part of the artwork. Carousel controls are hidden in the temporary capture without changing their layout space. The original backgrounds, fonts, decorative graphics, valuation chart, captions, and disclosures are baked into the PNGs.

On mobile, scale the original composition proportionally; do not stack or rearrange its sections. This prioritizes Ben’s visual-match requirement. Visible artwork text is not selectable live HTML, and image blocking affects the entire composition. Provide meaningful image alt text, the plain-text MIME companion `raindrop-email.txt`, and the linked accessible web edition. Do not describe this as a live-text or fully accessible visual email.

## Outputs and verification

- `email/raindrop-email.html`: production HTML with absolute HTTPS PNG references.
- `email/preview.html`: local preview with local images; never send this version.
- `email/raindrop-email.txt`: readable text alternative.
- `email/assets/page-section-*.png` and `page-footer-*.png`: original artwork pieces.
- `email/artwork-layout.json`: generated geometry and source font metrics used to verify that sections reconstruct the normal screen design.

Mandatory visual QA: use vision-based inspection of actual rendered screenshots of the normal and assembled email editions at the same display size. Compare layout, fonts, text density, spacing, colors, image crops, chart, and footer. Fix visible differences and inspect again before delivery. HTML validation, pixel dimensions, and other automated checks alone do not satisfy this requirement. If a client limitation prevents a match, describe the specific remaining difference.

Validate the HTML, inspect desktop and phone previews, and verify direct CTA destinations. Compare the assembled email to the NORMAL BROWSER PAGE at the same viewport width, not to a print rendering or the retired newsletter layout. Inspect the header, paragraph wrapping, actual font sizes, and stacked footer explicitly. The exact artwork is retained, although final display scaling and image-loading behavior depend on the email client.

Deploy images before a test send. The existing GitHub Pages host remains the default; `EMAIL_ASSET_BASE` supports a Rainmaker-approved HTTPS CDN. Actual Outlook/Gmail test sends remain the final delivery check. Rendering and staging never send email.

## Fonts and browser sizing

The normal edition and captured artwork must use the bundled Jost font files in `brand/fonts/`. Load and verify normal 400/500/600/700 and italic 400 before capture; fail the build if a font is unavailable. Do not rely on external font-loading timing. The delivered email still contains PNG artwork and no web fonts.

The base presentation table and Outlook wrapper remain 680px. A progressive screen media query lets browser windows at least 900px wide display the same artwork up to 1280px wide, matching the normal edition’s desktop scale. Inside an email container it remains fluid to its available width; without the query it stays at 680px. PNGs use content hashes in their URLs so new artwork does not reuse a stale browser cache.
