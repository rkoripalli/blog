# Blog — rkoripalli.github.io/blog

Personal blog: engineering, woodworking, and home automation build logs. Public site — this is the
one project in the workspace that is **not** on the homelab.

Live: `https://rkoripalli.github.io/blog/` (GitHub Pages project site — the root
`rkoripalli.github.io` intentionally 404s). Repo: `github.com/rkoripalli/blog`, branch `main`.

## Stack

- **Hugo** (extended) + **PaperMod** theme as a git submodule at `themes/PaperMod`.
  Run `git submodule update --init --recursive` after a fresh clone or local builds fail.
- No Node, no build deps. Local preview: `hugo server` → serves at `http://localhost:1313/blog/`
  (note the `/blog/` path — root 404s locally too).
- Config: `hugo.toml`. Homepage is PaperMod **profileMode** (avatar + bio + buttons), rendered
  entirely from config — `content/_index.md` is a frontmatter stub.

## Deploy

`git push main` → `.github/workflows/hugo.yml` → GitHub Pages. **Every push to main publishes
immediately.** CI overrides `--baseURL` from the Pages API, so the site works even if `hugo.toml`
drifts — but keep `baseURL = 'https://rkoripalli.github.io/blog/'` for local/CI parity.

## Theming — dark aurora

All customization lives in `assets/css/extended/custom.css` (PaperMod's supported override path;
loads after theme CSS). Matches the homelab app family:

- bg `#0f1117`, surface/cards `#1a1d27`, borders `#262a38`
- accent indigo: links `#818cf8`, hover `#a5b4fc`, selection `#6366f1`
- fonts: Manrope (body, 800-weight tight headings) + JetBrains Mono (code), via Google Fonts
- light mode is a first-class counterpart (near-white + `#4f51d8` indigo); default is dark

Template overrides (kept minimal, re-sync when updating the theme submodule):
- `layouts/_partials/footer.html` — copy of the theme footer with "Powered by" removed
- `layouts/_markup/render-image.html` — rewrites root-absolute image paths (`/images/...`)
  through `relURL` so they resolve under `/blog/`. **Gotcha:** Hugo's `relURL` ignores the
  baseURL path for leading-slash inputs, hence the `TrimPrefix "/"`.

## Writing posts

- `hugo new posts/<slug>.md` (archetype gives title/date/draft/tags/cover skeleton), or copy an
  existing post's frontmatter. Posts need `title`, `date`, `tags`, and optionally
  `cover.image` — a post without frontmatter breaks RSS/sorting (lumber-rack shipped that way once).
- Images: `static/images/<post-slug>/`, referenced as `/images/<post-slug>/name.png`.
- Voice: first-person, humble maker/engineer build logs. Write like `posts/lumber-rack.md`.
- **Privacy rule — posts are public.** Never include internal IPs, hostnames, VLAN layouts,
  tokens/keys, camera positions, or floor-plan-level home-security detail. Projects can be
  described architecturally ("an LXC on Proxmox") without the specifics in the homelab KB.

## Email subscriptions (Buttondown)

End-of-post subscribe box in `layouts/_partials/comments.html` (rendered via PaperMod's comments
hook, `params.comments = true`). It only appears when `params.buttondownUsername` is set in
`hugo.toml` — uncomment and set it once the Buttondown account exists. New-post emails are sent by
Buttondown's RSS-to-email automation watching `https://rkoripalli.github.io/blog/index.xml`
(configured in the Buttondown dashboard, not in this repo).

## Backlog

`blog-kb/TODO.md` (Approved Queue + Proposed). Post ideas: `blog-kb/post-ideas.md`.
