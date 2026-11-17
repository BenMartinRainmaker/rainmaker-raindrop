# Email standard

Ken Anderson’s technical requirements still apply: email must contain presentation tables, literal inline styles, PNG images with HTTPS URLs and explicit dimensions, and no browser-only features.

Ben’s November 17 correction takes precedence over the earlier live-text newsletter design: **the email-safe version must be visually identical to the normal edition, or as close as technically possible.** Do not change its layout, type, density, colors, section order, or proportions to fit a generic email template.

## Visual-match implementation

`render_email_artwork.mjs` opens the normal edition in Chrome with its existing print styles and fonts. It captures contiguous PNG sections of that original Letter-page composition at twice the source pixel resolution. No image generation or restyling takes place. Section boundaries share the same pixel grid, so the artwork reassembles without gaps or overlaps.

`build_email.py` places those sections in a 680px fluid presentation table. Main artwork links to the full web edition. The footer is split into aligned cells so the original Trade on Rainmaker X and Visit Rainmaker Securities buttons retain their direct links. All other visible source and gallery links are reached through the web edition. No image map, overlay, JavaScript, SVG, CSS layout system, custom font request, gradient, or print CSS is delivered in email.

The single initial product photo remains visible as part of the artwork. Carousel controls are absent because the source is captured in print mode. The original backgrounds, fonts, decorative graphics, valuation chart, captions, and disclosures are baked into the PNGs.

On mobile, scale the original composition proportionally; do not stack or rearrange its sections. This prioritizes Ben’s visual-match requirement. Visible artwork text is not selectable live HTML, and image blocking affects the entire composition. Provide meaningful image alt text, the plain-text MIME companion `raindrop-email.txt`, and the linked accessible web edition. Do not describe this as a live-text or fully accessible visual email.

## Outputs and verification

- `email/raindrop-email.html`: production HTML with absolute HTTPS PNG references.
- `email/preview.html`: local preview with local images; never send this version.
- `email/raindrop-email.txt`: readable text alternative.
- `email/assets/page-section-*.png` and `page-footer-*.png`: original artwork pieces.
- `email/artwork-layout.json`: generated geometry used to verify that sections reconstruct one page.

Mandatory visual QA: use vision-based inspection of actual rendered screenshots of the normal and assembled email editions at the same display size. Compare layout, fonts, text density, spacing, colors, image crops, chart, and footer. Fix visible differences and inspect again before delivery. HTML validation, pixel dimensions, and other automated checks alone do not satisfy this requirement. If a client limitation prevents a match, describe the specific remaining difference.

Validate the HTML, inspect desktop and phone previews, and verify direct CTA destinations. Compare the assembled email to the source print composition, not to the retired newsletter layout. The exact artwork is retained, although final display scaling and image-loading behavior depend on the email client.

Deploy images before a test send. The existing GitHub Pages host remains the default; `EMAIL_ASSET_BASE` supports a Rainmaker-approved HTTPS CDN. Actual Outlook/Gmail test sends remain the final delivery check. Rendering and staging never send email.
