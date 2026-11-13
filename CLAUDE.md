# Blog — rkoripalli.github.io/blog

Personal blog: engineering, woodworking, and home automation build logs. Public site — this is the
one project in the workspace that is **not** on the homelab.

Live: `https://rkoripalli.github.io/blog/` (GitHub Pages project site — the root
`rkoripalli.github.io` intentionally 404s). Repo: `github.com/rkoripalli/blog`, branch `main`.

## Stack

- **Astro** (static output) with a custom **Blueprint** theme. Node 22+, `npm ci` after a fresh clone.
  Migrated from Hugo + PaperMod on 2026-11-13; the old Hugo files are parked in
  `_Delete-me-2026-11-13/hugo/` (not built, safe to delete once o confirms).
- Local preview: `npm run dev` → `http://localhost:4321/blog/` (note the `/blog/` base).
  `npm run build` writes `dist/`.
- Config: `astro.config.mjs` (`site`, `base: '/blog'`, `trailingSlash: 'always'`). Site-wide text
  (title, tagline, Buttondown username, social links) lives in `src/lib/site.ts`.

### Layout of the repo

- `src/content/posts/*.md|.mdx` — posts (content collection, schema in `src/content.config.ts`).
- `src/pages/` — `index.astro` (home), `posts/` (index + `[slug]`), `tags/`, `search.astro`,
  `index.xml.ts` (RSS), `search.json.ts`, `404.astro`.
- `src/layouts/Base.astro` — head/meta/OG, header, footer. `src/components/` — `PostCard`,
  `Subscribe` (Buttondown), `FrameDecoder` (interactive figure).
- `src/styles/blueprint.css` — the whole theme; tokens at the top.
- `src/lib/remark-base-path.mjs` prefixes `/images/...` with `/blog`;
  `src/lib/rehype-figures.mjs` turns image-only paragraphs into numbered `FIG n` figures (alt = caption).
- `public/` — images, favicon set, `og-default.png` (default link preview), `robots.txt`.

### URLs that must not change

- Posts: `/blog/posts/<file-name>/` (same as Hugo). Tags: `/blog/tags/<slug>/`.
- RSS: `/blog/index.xml` — **Buttondown's RSS-to-email automation watches this exact URL.**

## Deploy

`git push main` → `.github/workflows/deploy.yml` (npm ci, astro build, Pages) → GitHub Pages.
**Every push to main publishes immediately.** Work on a branch and get o's OK before merging.

## Theming — Blueprint

Navy drafting sheet (`#0b2545`) with a two-scale grid, cyan linework (`#8cbeff`), yellow markups
(`#ffd166`). Barlow Condensed (uppercase display), IBM Plex Sans (body), IBM Plex Mono (labels,
title blocks). Posts are "sheets" numbered oldest = 001; cards and post headers carry an
engineering title block (date / read time / sheet). Single dark theme by design.

## Interactive figures

Write the post as `.mdx` and import components, e.g.
`import FrameDecoder from '../../components/FrameDecoder.astro';` then `<FrameDecoder ... />`.
Components ship plain HTML plus a small script; keep them working without JS where possible.

## Writing posts

- Copy an existing post's frontmatter into `src/content/posts/<slug>.md` (or `.mdx` for interactive
  figures). Posts need `title`, `date`, `tags`; `description` (one sentence, used for cards, RSS
  and link previews) and `cover.image` / `cover.alt` are strongly recommended. The build fails on
  missing/invalid frontmatter, which is intended.
- Images: `public/images/<post-slug>/`, referenced as `/images/<post-slug>/name.png`.
- Voice: first-person, humble maker/engineer build logs. Write like `posts/lumber-rack.md`.
- **Privacy rule — posts are public.** Never include internal IPs, hostnames, VLAN layouts,
  tokens/keys, camera positions, or floor-plan-level home-security detail. Projects can be
  described architecturally ("an LXC on Proxmox") without the specifics in the homelab KB.

## Email subscriptions (Buttondown)

`src/components/Subscribe.astro`, shown on the home page, post pages and the log index when
`SITE.buttondownUsername` is set in `src/lib/site.ts`. New-post emails come from Buttondown's
RSS-to-email automation watching `https://rkoripalli.github.io/blog/index.xml` (configured in the
Buttondown dashboard, not in this repo).

## Backlog

`blog-kb/TODO.md` (Approved Queue + Proposed). Post ideas: `blog-kb/post-ideas.md`.
