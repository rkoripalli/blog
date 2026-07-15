# Blog TODO

## Approved Queue

(empty — items here are ready for an agent to execute)

## Blocked on Rohan

- **Buttondown account** — create at buttondown.com (pick username, ideally `rkoripalli`), then in
  Settings → RSS automation add feed `https://rkoripalli.github.io/blog/index.xml`. Hand the
  username back → uncomment `buttondownUsername` in `hugo.toml` and the subscribe box goes live.

## Proposed

- Write next post — pick from `post-ideas.md` (top candidates: local-first AI agents, ZFS watchdog war story, lumber rack follow-up)
- Add a favicon set (currently 404s: favicon.ico, apple-touch-icon, etc. referenced by PaperMod head)
- Decide on a custom domain (e.g. `blog.rohan.house` CNAME → GitHub Pages) — needs Rohan (DNS + irreversible-ish URL change; current `/blog/` path URLs would move)
- Add an Archives page (PaperMod supports `layout: archives`)
- Add `description:` frontmatter to existing posts for better list summaries and SEO
- Social preview image (default og:image) — PaperMod `params.images`
- Consider giscus/utterances comments (GitHub-backed, static-friendly)

## Done

- 2026-07-14 — Migrated Hextra → PaperMod, dark aurora theme, baseURL fix, lumber-rack frontmatter fix, image render hook, docs + KB created
