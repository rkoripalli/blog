# Blog notes: taking CleanYourTV and making it ours (raw, 2026-11-13)

Angle: CleanYourTV is a great open-source starting point. This is how we took its launcher and rebuilt the look and feel around our own design system, with a design-review loop, instead of using it as shipped.
Public post: these notes have no IPs, hostnames, tokens, webhook IDs, HA entity IDs or camera details. Numbers are rough.

---

## 1. The starting point: CleanYourTV

- **What it is:** an open-source kit that strips the bloat from an Android TV / Google TV over Wi-Fi using a coding assistant. It then replaces the ad-filled home screen with a small native launcher "that looks like an Apple TV". No root, no cable, nothing uninstalled (`pm disable-user`), and a one-line restore.
- **How you use it:** turn on network debugging, paste `PROMPT.md` into Claude Code (or Codex / Gemini CLI) and name your TV model. The assistant:
  1. backs up the package list,
  2. finds the telemetry, ad services and preloads,
  3. asks before touching anything you might use,
  4. builds and installs the launcher,
  5. checks each step with screenshots pulled from the TV.

  Takes about 15 minutes.
- **Author / origin:** Gathin (GitHub `Gathin23`, X `@gathint`).
  - 17 Oct 2026: he posted a before/after of his parents' TV, cleaned up by Claude Code.
  - The tweet reached 7.4M views, and people's replies turned into the model lists.
  - It became the #1 trending repo of the week.
  - The repo was called `tv-vibehack` until 19 Oct.
- **Repo:** https://github.com/Gathin23/cleanyourtv (site: cleanyour.tv). MIT licence. First commit 2026-10-17. By 13 Nov it had over 6,100 commits, and the README claims 190 TV models, 56 brands and 24 languages.
- **The launcher it ships (`com.gathin.tvhome`):**
  - Java + AndroidX, about 429 KB, about 151 MB resident, about 0.8 s cold start.
  - Look: cool graphite (`#161618` / `#1C1C1E`), sky-blue accent `#6EC1FF`, translucent white "glass" pills and panels, the Outfit typeface.
  - An ambient glow behind the dock, coloured from the app banner, and full app banners as tiles.
  - Pills for Inputs, network and Settings.
- **Built to be customised:**
  - A `config.xml` with dozens of flags: columns, dock row, cinematic hero, sky gradient, glow, greeting, clock screensaver.
  - Themes you push without rebuilding (`aurora`, `dussehra`, `six-columns`).
  - A small, readable Java codebase. We relied on that a lot.
- **Credit line for the post:** everything below sits on top of Gathin's work. The debloat method, the HOME handover, the build/install scripts and the launcher's bones are upstream.

## 2. Step one: use it as intended (21 Oct)

- NVIDIA SHIELD TV Pro (2019): 26 packages disabled, nothing uninstalled.
- The ads came from one package, `com.google.android.tvrecommendations`: the sponsored hero banners and the "Free Live TV / Top Selling" rows.
- The upstream launcher went in with **only four config edits**:
  - our four dock apps,
  - an emptied hidden-apps list (upstream's defaults are packages a SHIELD doesn't have),
  - the Live TV package,
  - true-colour wallpaper.
- It looked good (`img/02`). Same evening we decided it should look like the rest of our house instead.
- Two places where we departed from upstream's SHIELD list:
  - GeForce NOW lives inside the package the list disables as the dead "NVIDIA Games" row, so we kept it.
  - Live Channels stays, because the HDHomeRun tuner goes through it.

## 3. Step two: our own design, "Walnut Night" (21–22 Oct)

**Why:** our Home Assistant dashboards already use a warm, dark "walnut" palette. The TV should feel like part of the same home, not a generic Apple TV clone. Rules: flat, and no glass, glow or gradients.

### Upstream vs ours

| | Upstream CleanYourTV | Walnut Night |
|---|---|---|
| Palette | cool graphite + sky blue `#6EC1FF`, white glass | warm walnut browns, amber `#F2B46B` focus |
| Surfaces | translucent glass panels, ambient glow behind the dock | solid layered surfaces, no glow |
| Type | Outfit | Barlow body + Barlow Semi Condensed 600 headings |
| Tiles | full app banners | square logomark tiles (real icons pulled off the device), 7 columns |
| Hero | app name, optional blurred banner art | big 64sp name of whatever has focus, plus a subline that's never empty |
| Header | clock, date, Inputs / network / Settings pills | greeting + clock │ date + weather and inside temp │ 3 round icon pills |
| Focus | glass highlight, glow | 3dp amber ring set 3dp off the tile; unfocused tiles slightly desaturated |
| Feedback | toasts | hints and failures inline in the hero subline (copper / rust) |

### Tokens

| Token | Hex | Role |
|---|---|---|
| ground | `#13100E` | background |
| surface | `#1D1916` | dock band |
| raised | `#28221E` | idle pills |
| line | `#3A322B` | borders |
| text | `#F0E9E0` | primary text |
| muted | `#BFB3A5` | secondary text |
| faint | `#93887B` | tertiary text |
| ACCENT | amber `#F2B46B` on SHIELD, blue `#86AFD1` on our Fire TV port | focus only |
| copper | `#C9844E` | moving an app |
| rust | `#E07154` | failures |

### Rules we wrote down (good quotable material)

- **Focus rings:** a ring means focus, work in progress or failure, never "on". Movie mode "on" is a neutral fill, an amber glyph and a small dot.
- **Never an empty subline:**
  - an app you've used: "Last opened yesterday, 11:11 PM"
  - an app you haven't: "OK to open · Hold OK to move" for the first 20 views, then "Not opened yet"
- **No toasts:** failures read in rust where the eye already is, e.g. "Couldn't open Netflix · OK to retry". The tile keeps a small rust corner badge until the app opens again.
- **Moving apps:** hold OK to pick up a tile. It gets a dashed copper ring, the others dim, and the subline reads "◀ ▶ to move · OK to drop · Back to cancel". Back puts the tile back where it was.
- **Typography detail:** the clock column is sized to the widest time *for the current number of hour digits*, so the divider never jumps on a minute tick. We tried tabular figures and rejected them because "11" looked uneven.
- **Header detail:** up from the dock always lands on the first pill (Doorbell), so a reflexive Up+OK can't trigger Movie mode.

### Things we tried and threw away

- Blurred banner art behind the hero (upstream's "cinematic" look, our early mock `img/05`): o didn't like the banner look.
- The ambient glow and the glass: off-palette.
- The Inputs pill: a streaming box has no inputs.
- Toasts.
- A focus scale: the box runs with animations off.

### One spec, two TVs

The spec was written once and ported to a Panasonic Fire TV the same week. **Only the accent changes**, amber on the SHIELD and blue on the Fire TV.

## 4. How we designed it: mock first, review, repeat

- **The loop:**
  1. Every UI change starts as a mock in **FigCraft**, a Figma-class design tool Claude drives over MCP.
  2. o approves the mock before anything is built.
  3. The mock goes through **Impeccable**, a design-review skill: a Nielsen-heuristics critique out of 40 plus a native Android audit out of 20. Each round is scored by an isolated reviewer agent that only sees the exported PNGs and the spec.
  4. Fix, update the mock, re-score. Stop when the score stops climbing.
- **Home screen:** 36 → 37/40, audit 15 → 17/20 between 21 and 22 Oct. The reviewer judged the rest "capped" by things that are structural on a D-pad TV and not worth chasing.
- **Mock vs real:** score a real TV screenshot, not only the mock. On the Fire TV screensaver, mocks scored 31–34 but the real screen scored 28–30.
- **Typical catches:**
  - A doorbell view left open would burn in its static labels, so it now closes itself.
  - The colours were hard-coded hex everywhere.
  - A pending ring widened a button and pushed its neighbour off the card.
  - A reflexive OK could answer a prompt meant for later.
- **One design file:** all versions (v12 to v25 and every card) live in a single `walnut-night.figcraft`, and new mocks start from its "as installed" frame.
- **Mock caveat:** FigCraft doesn't have Barlow, so the mocks use a fallback face. Barlow is narrower, so the real build has more room than the mock shows.

## 5. Then we kept going: features upstream doesn't have (29 Oct – 8 Nov)

Each one followed the same mock → review → build loop, in the same visual language. All overlays share one bottom-right slot. Keep this section short in the post. (Plumbing for anyone curious: the TV holds no Home Assistant token. HA writes a small JSON file the launcher reads, and pushes cards over the TV's existing debug link.)

- **Wind-down card:** after 23:00, "Wind down for bed? Lights warm to amber, TV off in 30 min", with [Yes] [Not tonight]. Has a 1 s guard against stray presses and a 5 s undo. Impeccable 28 → 33 → 35/40.
- **Sports "Start?" / "On now":** "#17 Florida at #3 Georgia · ABC · kicks off 2:30 PM", with [Watch] [Not now]. Priority in the shared slot: doorbell > wind-down > Start? > On now. Impeccable 32 → 35/40.
- **Doorbell picture-in-picture:** a small live card over whatever's playing. Version 1 paused the show and sat top-right for 30 s. After living with it: never pause, 10 s, smaller, bottom-right.
- **Up next:** a Jellyfin Continue Watching row under the dock, with "24 min left". It uses series art, not episode stills, because stills are unreadable at tile size and can spoil the episode. Stale data hides the row: "31 min left must never lie."
- **Cast block:** "Cast · SHIELD / AirPlay · receiver / Wi-Fi · guest" plus the guest Wi-Fi QR. It replaced a guest mode that stripped the home screen down, which o rejected: "don't remove functionality".
- **The one we deleted:** a Now Playing music card. It was designed, scored 35/40 and installed, then removed the same afternoon, because pressing play switched the receiver away from the TV's input. Good beat: the review loop can't tell you a feature is pointless; using it can.

## 6. Scale (rough)

- **Timeline:** 21 Oct (stock upstream) → 22 Oct (Walnut Night final) → 29 Oct–8 Nov (cards).
- **No git history:** it started from a zip of the repo, not a fork, so there are no commit counts.
- **Diff size:** about 7,000 changed lines in the launcher source against upstream as of 21–22 Oct. That's an overestimate, because upstream kept moving after the snapshot.
- **Code:**
  - about 660 lines added to `MainActivity.java`
  - about 12 new classes
  - 6 Barlow font files replacing Outfit
  - about 15 new drawables
- **Builds:** about 21 archived APKs and pre-change backups in three weeks.

## 7. Images (in `img/`, 4K shots downscaled to 1920 wide)

Suggested order for a before → upstream → ours story:

| File | What | Privacy |
|---|---|---|
| `01-stock-home-ads.png` | Stock Google TV home with a sponsored banner and "Free Live TV" rows | **Flag:** a local TV-station tile names the metro area. Crop or blur it. Third-party show art. |
| `02-upstream-cleanyourtv-default.png` | The upstream launcher as shipped | Clean |
| `05-figcraft-walnut-mock.png` | Early Walnut mock with the blurred banner we threw away | Clean |
| `04-figcraft-before-after.png` | FigCraft board: before, after and palette swatches | Clean, small text |
| `03-walnut-night-on-tv.png` | Final Walnut Night home, real TV screenshot | Clean (weather + inside temp only) |
| `08-up-next-doorbell-mock.png` | Home with the Up next row and the doorbell slot (grey placeholder) | Clean; posters are third-party art |
| `06-wind-down-on-tv.png` | Wind-down card on the real TV | Clean |
| `07-sports-start-card-mock.png` | Sports Start? card mock | Clean |

**The money shot is 02 next to 03:** the same launcher, same TV, a day apart.

Not copied but usable: `personal-artifacts/tv-launchers/firetv/home/v15-online.png`, which shows the same spec with a blue accent on the Fire TV. Good for the "one spec, two TVs" point.

**Avoid:**
- real doorbell camera frames (`tv/shots/shield/doorbell-*.png`)
- the v16–v22 guest/cast mocks (guest Wi-Fi name, QR)
- `01-stock-home.png` (third-party screensaver photo)
- anything showing terminal or ADB output
