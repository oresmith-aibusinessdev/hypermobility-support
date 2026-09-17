# Hypermobility Support — Project Handoff

## What this is
An evidence-based hEDS/HSD reference site (hypermobilitysupport.com), hosted on Netlify
(project `glistening-jalebi-36c70e`), built as a static multi-page site generated from
JSON content files by a Python script. 61 content pages as of the last build: 30 hub pages
+ 30 spoke pages + Beighton tool, plus the affiliate-disclosure page (62 built page
directories total), plus robots.txt/sitemap.xml/llms.txt.

## Where everything lives
- Content (the actual page text, real citations): `/Users/orebsmith/Documents/hypermobility-support/site-copy/drafts/*.json`
  (pages_batch*_final.json = hub pages, spokes_batch*_final.json = spoke pages, beighton_score_page_final.json)
- Site generator + assets: `/Users/orebsmith/Documents/hypermobility-support/site-build-tooling/`
  - `build_multipage.py` — the script that reads the JSON and outputs the static site
  - `site_shell.html` — CSS source (the `<style>` block gets extracted from this)
  - `icon_data_uris.json` / `icon_bg_colors.json` — the 16 hand-cropped topic icons as base64
  - `assets_style.css` — pre-built CSS, fonts (Hanken Grotesk + Lora) baked in as base64
    directly in this file (regenerate from site_shell.html + fonts if it goes missing —
    there is no separate `fonts/font_data_uris.json`, despite an earlier version of this
    doc implying one)
  - `site_build/` — output of the most recent build, for reference

## To rebuild and deploy
```bash
cd /Users/orebsmith/Documents/hypermobility-support/site-build-tooling
python3 build_multipage.py
cd site_build && zip -rq -X ../hypermobility-site.zip . -x ".*"
```
Then drag `hypermobility-site.zip` into Netlify: project `glistening-jalebi-36c70e` → Deploys tab.

## Current state / what's in progress
- Domain, DNS, HTTPS, Netlify: all live and working.
- Internal linking: all 30 spoke pages now map to a hub page in `SPOKE_TO_HUB`
  (`build_multipage.py`) — previously 12 were orphaned and rendered unlinked placeholder
  text instead of a real link. Fixed.
- Affiliate product module: 9 pages now have Amazon product recommendations (Associates
  tag `hypermobil087-20`), all tied to cited evidence — 5 hub pages plus 4 spoke pages
  whose own text explicitly names the same intervention as an existing vetted hub
  product (spoke pages previously never rendered products at all; `render_spoke` now
  calls `render_products` like hub pages do). `/affiliate-disclosure/` page exists,
  linked from every page's footer. Expanding further to more spoke pages needs its own
  research pass to source and verify new products — don't invent ratings/ASINs without one.
- Reddit post is live, got 6,000+ views — real first traffic.
- Google Search Console: verified, sitemap submitted (property must be `hypermobilitysupport.com`,
  not any other property in the account).
- Google Tag Manager (GTM-BDJ349M9): confirmed published (fetching the live container
  script directly returns real tag/trigger config, not an empty draft), and it contains
  the GA4 measurement ID (`G-SEQFM8EMK5`) — the tag wiring is confirmed correct end to
  end at the code level. GA4 Realtime itself wasn't checked (needs Google account login),
  but with the container confirmed published and correctly configured, this is effectively
  resolved — a quick Realtime glance is just a sanity check at this point, not a debug step.
- Research loop (finding new hEDS/HSD topics, writing evidence-backed pages) was running via
  the `/loop` skill — currently stopped, was at 61 pages toward a 100-then-500 target. Every
  page uses real peer-reviewed citations only (no fabricated claims), verified anti-slop style
  (no em dashes, no AI-tell phrasing) — keep that bar if resuming.
- Backlink outreach (emailing cited researchers, patient-org resource pages) — discussed,
  scoped, never executed. Good next step now that there's real traffic to point to.
- Growth plan: see `/Users/orebsmith/.claude/plans/i-want-to-create-proud-pie.md` for the
  full traffic/ranking/referral-sales growth loop plan (content freshness + volume cadence,
  trust/authorship infrastructure, relationship-based backlink outreach cycle).

## Known gotchas
- The reference image the 16 hand-drawn-style icons were cropped from is at:
  `/Users/illina/Downloads/ChatGPT Image Aug 30, 2026, 07_12_48 PM.png` (on the old machine —
  not needed unless icons need to be regenerated from scratch).
- One icon (skin-fragility-easy-bruising) was replaced with a different reference image
  (6-finger AI-art defect in the original) — already baked into icon_data_uris.json, no action needed.

## This project is also backed up to Google Drive
Folder: "Hypermobility Support Project" (contains site-copy-drafts/ with all 21 content JSON
files, and site-build-tooling/ with build_multipage.py, site_shell.html, icon_data_uris.json,
icon_bg_colors.json, assets_style.css, and this HANDOFF.md — all present as of the last check).
