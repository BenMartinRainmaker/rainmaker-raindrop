# Production workflow

## New month

1. Create `YYYY-MM-company/` and its README, `content.md`, `assets/`, and original `template.html`.
2. Use the prior content schema and tooling, but create a new company-specific composition. Preserve brand identity, footer links, responsive behavior, browser editing metadata, and exactly one US Letter PDF page.
3. Select and license the images, verify facts and quotations for the edition, and record the research cutoff in the fine print. Existing facts are not re-verified merely by rebuilding a format.
4. Preserve that original composition in the email using the visual-match artwork workflow. Do not independently rearrange or redesign the email. Common output logic lives in `build_email.py` and `render_email_artwork.mjs`; the source page supplies its exact visual composition.

## Edit and build

Edit words in `content.md`, web design in the issue’s `template.html`, and email markup in `build_email.py`. Use `python3 build.py <issue>` for web HTML only. Use `./render.sh <issue>` for the complete web/PDF/share/email build. Use `./render.sh <issue> --web-only` when email work is deferred; it rebuilds the normal HTML, PDF, preview, and browser share exports without changing the email draft. The artwork renderer captures the complete `.page` in screen mode, unrolling scrolling without altering typography or widths, using `.foot .cta a` as the footer link hooks. Preserve those hooks or update the renderer with the design. Chrome and Node.js 22+ are required; `CHROME` may override its executable. Nested versions use their full relative path.

The build captures the unchanged normal desktop browser composition as linked PNG sections and builds a 680px email from those exact sections. It rejects forbidden email features and HTML over 100KB. Rebuild after any content, image, or design change.

Inspect `preview.png`, render the PDF to an image and check the footer, and review `email/preview.html` at desktop and phone widths. Use vision-based inspection to compare actual renders of the normal and email editions at the same size; iterate until visually identical or as close as technically possible. Automated checks alone are insufficient. When Ben explicitly defers an email edition, work only on the normal edition and retain existing email files as drafts until requested. The PDF must be exactly one page with no clipped content. Email must scale the original composition without rearranging it. Confirm its logos, raindrop, static photo, chart, source links, cards, and CTAs. Review November’s two content options when changing shared facts.

## Publish and send

Run `./stage.sh` to prepare `site/`, including email assets and old public-path aliases. The GitHub Action renders all issues/versions and stages them on push to main. A render or email-generation failure stops deployment. `./publish.sh` commits all local changes and pushes; inspect the full diff first. Use the Rainmaker account `BenMartinRainmaker`, not a personal account.

Deploy before importing production email HTML, then verify all absolute asset URLs load. The default host is the existing GitHub Pages site. Set `EMAIL_ASSET_BASE` to an approved Rainmaker CDN root if chosen, and upload assets under `<root>/<issue>/email/assets/`. Rebuild emails when the host changes.

Import `email/raindrop-email.html` and its text companion into the sending platform. Sender identity, subject/preheader, platform footer/unsubscribe settings, and test recipients are configured there. Preserve the issue’s disclosure text. Do not append Ken’s personal signature just because his technical feedback was supplied.

Run actual Outlook desktop, Gmail, and mobile client test sends before distribution. The local browser preview checks composition and local images only. No email is sent by the build or staging tools. Sending requires explicit user authorization.

Browser editing remains available at the web URL plus `?edit=1`. It edits `content.md` and triggers the same build for both formats after deployment. The email has no editor or credentials. Browser-only embedded `share/` files are not email bodies.
