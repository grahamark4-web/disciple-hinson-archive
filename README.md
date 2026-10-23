# Disciple Hinson Podcast Archive

Independent searchable archive for Disciple Hinson, built for embedding on Hinson Baptist Church's Squarespace website. Repository: grahamark4-web/disciple-hinson-archive. This repository and Cloudflare Worker are separate from the sermon archive.

## Cloudflare Workers setup

Create a new Worker from this GitHub repository. Use project name `disciple-hinson-archive`, production branch `main`, no build command, root `/`, and deploy command `npx wrangler deploy`. Wrangler reads wrangler.jsonc and uploads only dist as static assets, alongside worker.mjs for audio downloads. Enable the workers.dev URL after deployment if Cloudflare leaves it disabled. No API keys, database or external npm dependencies are required by the app.

Do not attach this to the existing sermon Worker or change its routes. Preview deployments are optional; the production branch for this separate app is main. The app itself must be publicly reachable to work in a public church-page iframe; the GitHub source repository can remain private.

## Features

All 288 index entries at initial import (2019-02-04 through 2026-10-14), including supplementary unnumbered classes. Search titles, guests, speaker metadata, series, themes and explicit Scripture citations. There is no theme dropdown. Themes use weighted, boundary-aware matches in titles, unique episode notes and publisher tags, with repeated boilerplate excluded; podcast transcripts have not been created. Filters include individual speakers and year. Series and Scripture remain searchable but have no dropdown filters. Desktop search describes the available options; mobile says Search. The persistent audio player supports seek, 15-second skip and pause. Episode notes expand in place. Episode and timestamp URLs work on the app's own hostname. Apple/Spotify episode links are shown only for verified matches; show-follow links are always available.

Speakers are taken from audio metadata, never the Squarespace publishing-account author. Multiple speakers are split with limited explicit name normalization. Guest names in titles/notes are searchable even when not included in the audio's speaker metadata. Initial platform coverage: 100 Apple episode links and 12 Spotify links. All 288 entries have HTTPS audio URLs.

## Embedding

Use the EMBED.html snippet after replacing APP_ORIGIN with the deployed app origin (no trailing slash). Paste the snippet into a Squarespace Code Block with Display Source off. Keep the existing podcast collection public: it remains the audio and metadata source. The iframe uses ?embed=1 to hide duplicate headings; embed-resize.js adjusts its height so the church page owns scrolling. The app and parent verify message origins and iframe identity. Test signed out on desktop and phone before replacing the current index.

Sharing currently links to the app's own origin. If a final church page should be the share destination, set that only after the embed is installed and verified on that page. This avoids links opening the old index without playing the intended episode.

## Automatic refresh

The GitHub workflow runs daily at 10:37 UTC and supports manual dispatch under Actions → Refresh Disciple Hinson catalog. It follows every collection page, rejects pagination loops and unexpected shrinkage, regenerates topics, refreshes verified platform links, runs checks and commits data to main. Cloudflare Git integration then deploys the commit. Scheduled GitHub jobs can be delayed or disabled for inactive repositories; inspect Actions and Cloudflare deployment history when troubleshooting.

Run locally: `python refresh.py` with Python 3.10+ and Node.js 22+. No third-party Python dependencies. Caches expire after five minutes. Review catalog-report.json and platform warnings. No secrets are required for refresh.

## Checks

`node test_subjects.cjs`, `node test_catalog.cjs`, `node test_worker.cjs`, `node --check dist/app.js`, and `node --check dist/interactions.js`.

Browser QA verified topic synonyms, combined filters, audio playback, 15-second skip, immediate pause, and a 390px phone iframe with Search placeholder and no horizontal overflow. The Worker download route restricts recordings to catalog IDs and approved Squarespace hosts, streams responses with byte-range support, and adds attachment headers.

Subject indexing v2 covers all 288 episodes. The vocabulary includes mental health, OCD, hospice/end-of-life care, disability, biblical theology, church history, missions strategy, spiritual gifts and other specific subjects. Inspect theme-index-report.json for title/note/tag evidence. Tags are metadata-supported classifications, not transcript summaries.
