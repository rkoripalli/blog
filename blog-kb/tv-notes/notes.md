# TV launcher blog notes (raw research, 2026-11-13)

Raw notes for a public post. Scrubbed of IPs, hostnames, tokens, webhook IDs, HA entity IDs and camera details. Numbers are rough.

## 1. Upstream: CleanYourTV

- **What it is:** an open-source kit for de-bloating Android TV / Google TV over Wi-Fi with a coding assistant, and replacing the ad-filled home screen with a small native launcher "that looks like an Apple TV". No root, no cable, nothing uninstalled (`pm disable-user`), one-line restore.
- **How it works:** turn on USB / network debugging, paste `PROMPT.md` into Claude Code (or Codex / Gemini CLI). The assistant backs up the package list, disables telemetry, ads and preloads, then builds and installs the launcher.
- **Author:** Gathin (GitHub `Gathin23`, X `@gathint`). It started on 17 Oct 2026 as a before/after tweet of his parents' TV. The tweet hit 7.4M views and the repo became the #1 trending repo of the week. It was called `tv-vibehack` until 19 Oct.
- **Repo:** https://github.com/Gathin23/cleanyourtv (site: cleanyour.tv). First commit 2026-10-17. Over 6,100 commits by 13 Nov 2026, because the community kept adding TV models (README: 190 models, 56 brands, 24 languages).
- **Licence:** MIT, "Copyright (c) 2026 Gathin".
- **Launcher:** package `com.gathin.tvhome`. Java + AndroidX, minSdk 26 / targetSdk 34, R8-minified. The APK is about 429 KB, uses about 151 MB resident and cold-starts in about 0.8 s. The upstream default look uses the Outfit typeface, glass pills, a blurred banner hero and an ambient glow behind the dock (see `img/02`).

## 2. What o changed

### Timeline (rough)

There is no git history: o started from a zip of the repo, not a fork. Dates below come from handoff docs, file dates and dated APK/backup names.

| Date | What |
|---|---|
| 2026-10-21 | NVIDIA SHIELD TV Pro (2019) de-bloated: 26 packages disabled, nothing uninstalled. Upstream launcher installed with 4 config edits, the dock set to o's apps. |
| 2026-10-21 (same evening) | Full "Walnut Night" restyle to match o's Home Assistant dashboards. Home Assistant link added: weather, inside temperature, Movie-mode pill, doorbell pill. |
| 2026-10-21/22 | Port to a Panasonic Fire TV, with the same spec and a blue accent instead of amber. |
| 2026-10-22 | Final design pass: Impeccable 37/40 heuristics, 17/20 native audit (judged the ceiling). Fixed a scroll glitch. |
| 2026-10-29 | A busy day. Doorbell picture-in-picture over any app. Jellyfin "Up next" row. Now Playing card (built, then removed the same day). Guest mode, reworked into an always-on Cast/AirPlay/Wi-Fi block. Bedtime wind-down card. All design threads merged into one FigCraft file. |
| 2026-10-31 | Doorbell PiP made smaller and moved to bottom-right. It no longer pauses playback and closes after 10 s. |
| 2026-11-01 | Sports "Start?" card and "On now" toast designed, scored and built. Installed around 2026-11-08. |

- **Scale:** the diff against upstream is very roughly 7,000 changed lines in `launcher/app/src/main`. That count is inflated, because upstream itself kept moving after the snapshot. About 660 lines were added to `MainActivity.java` alone.
- **New classes:** about 12 (Doorbell ×3, HaStatus, Sports ×3, UpNext ×2, WindDown ×2, plus tests).
- **Builds:** about 21 archived APKs and pre-change backups in about 3 weeks.

### Design system: "Walnut Night"

- **Why:** match o's Home Assistant dashboard palette (warm dark walnut, not the upstream cool glass look). Flat, with no glow, glass or gradients.
- **Tokens:**

  | Token | Hex | Role |
  |---|---|---|
  | ground | `#13100E` | background |
  | surface | `#1D1916` | dock band |
  | raised | `#28221E` | idle pills |
  | line | `#3A322B` | borders |
  | text | `#F0E9E0` | primary text |
  | muted | `#BFB3A5` | secondary text |
  | faint | `#93887B` | tertiary text |
  | ACCENT | amber `#F2B46B` on SHIELD, blue `#86AFD1` on Fire TV | focus only |
  | copper | `#C9844E` | moving an app |
  | rust | `#E07154` | failures |
  | sand | `#E6C77E` | weather glyph |

- **Rule:** a ring always means focus, work in progress or failure. It never means "on". "On" is a neutral fill, an accent glyph and a small dot.
- **Type:** Barlow for body text and Barlow Semi Condensed 600 for the hero name and headings, replacing upstream's Outfit. Hero name 64sp, clock 52sp light, date 22sp, all secondary text 18sp.
- **Clock detail:** the clock column is sized to the widest time with the current number of hour digits, so the divider never shifts on a minute tick. Tabular figures were tried and rejected because "11" looked uneven.
- **Layout:**
  - Header: greeting over clock | 1dp divider | date over weather | round icon pills on the right.
  - Below it, a big "hero" title naming whatever has focus, with a subline that is never empty ("Last opened yesterday, 11:11 PM").
  - Then a 7-app dock of square logomark tiles on a band, with one more row below it.
  - Design target is 960×540 dp. The SHIELD composes its UI at 1080p over 4K output.
- **Focus:** a 3dp amber ring drawn 3dp off the tile, with no glow. Unfocused tiles are slightly desaturated (0.7). Pills lift 1.12× on focus.
- **Removed or rejected:**
  - Blurred banner art ("cinematic home"): o disliked the banner look.
  - The Inputs pill: a streaming box has no inputs.
  - The glow: off-palette.
  - Toasts: failures and hints live in the hero subline in rust or copper ("Couldn't open Netflix · OK to retry").
- **Reorder:** hold OK to pick up a tile. It gets a dashed copper ring and copper hint text. Back cancels.

### Home Assistant integration: no token on the TV

The core design choice: **the TV holds no Home Assistant token and opens no listening port.**

- **Pull:** HA writes a small `status.json` (weather, inside temperature, movie-mode state, guest flag) into its static `/local` folder. The launcher polls it every 5 minutes while Home is visible. Any failure hides the line, so Home never waits on the network. Up next works the same way with an `upnext.json`. An HA script talks to Jellyfin, so the TV needs no Jellyfin token either. The rule: "31 min left must never lie", so stale data (over 6 h old) hides the row.
- **Push:** HA reaches the TV through its existing Android TV ADB integration, with `am broadcast` to receivers guarded by the `DUMP` permission. Only the shell (ADB) can send to them. This drives the doorbell, wind-down and sports cards.
- **Answers back:** card buttons POST to an HA webhook, for example `{"answer":"yes","minutes":30}`.
- **Movie pill:** toggles HA movie mode, where lights dim on play and come up on pause. It uses an optimistic toggle, a pending ring, roll-back on failure, and a rust "Home Assistant didn't respond · OK to retry".
- **House modes:** HA-side gating respects o's house modes. For example, no sports prompts at Night, Away or Vacation, and the doorbell popup skips while movie mode is on.

### The cards

All overlays share one bottom-right slot.

- **Doorbell PiP**
  - When the doorbell rings or a person is detected, a small live-camera card appears over whatever app is playing.
  - Version 1 (10-29) paused playback and sat top-right for 30 s. After living with it, o changed it (10-31): never pause, 10 s, smaller, bottom-right.
  - The card stays invisible until 600 ms after the first smooth video frame, so it never shows a stuttering stream. If no smooth video arrives within 8 s, it gives up quietly.
  - It is non-focusable, so the remote keeps driving the app underneath.
  - A separate Doorbell pill opens the full-screen live view, which closes itself after 3 min (burn-in).
- **Wind-down sleep timer**
  - Once a night after 23:00, HA asks "Wind down for bed? Lights warm to amber, TV off in 30 min", with [Yes] [Not tonight].
  - Yes warms the TV light strip and starts a sleep timer that turns off the SHIELD, TV and receiver.
  - OK and Back are ignored for 1 s after it appears, so a press meant for the player isn't taken as an answer. Media and volume keys pass through.
  - There is a 5 s "Back to cancel" undo. Equal-width locked buttons mean the pending ring can't reflow the layout.
  - Impeccable: 28 → 33 → 35/40 over 3 rounds.
- **Sports "Start?" and "On now"**
  - o's HA sports auto-start already pushed a phone notification. o asked "Why not notify on the TV as well?"
  - "Start?" card: "#17 Florida at #3 Georgia / ABC · kicks off 2:30 PM", with [Watch] [Not now]. It closes itself after about 15 s.
  - "On now" toast: about 8 s, non-focusable.
  - Priority in the shared slot: doorbell > wind-down > Start? > On now (o's call). A higher card hides a lower one. A lower card waits, and a queued Start? is dropped if kickoff is more than 2 min past.
  - Impeccable: 32 → 33 → 35/40.
- **Now playing:** a whole-house music card with play/pause and a "play here" action, built and scored 34 → 35/40 on 10-29, then **removed the same afternoon**. Pressing play switched the receiver off the SHIELD input, so the card defeated itself. This is a good honesty beat for the post.
- **Up next:** a Jellyfin Continue Watching / Next Up row under the dock, with progress bars and "24 min left". Series art is used, never episode stills, because stills are unreadable as tiles and can spoil the episode.
- **Cast block:** always-on header text, "Cast · SHIELD / AirPlay · receiver / Wi-Fi · guest network", plus the guest Wi-Fi QR code. It replaced a guest mode that stripped the home screen; o rejected that: "I'll be the primary user… don't remove functionality". No password is ever handled as text: the QR is a crop of the router app's share code.

### Design process

- **Rule:**
  1. Every UI change starts as a mock in **FigCraft**, a Figma-class design tool driven by Claude over MCP. o reviews the mock and approves it before any build.
  2. The mock then goes through **Impeccable** (a design-review skill): a Nielsen-heuristics critique /40 and a native Android audit /20. Each round is scored by an isolated reviewer subagent from exported PNGs.
  3. Fix, update FigCraft, re-score. Stop when the score stops improving.
- **One canonical file:** all frames (versions v12–v25 plus the cards) live in one `walnut-night.figcraft`.
- **Caps:** the reviews name scores that are structurally capped on a D-pad TV and not worth chasing. Examples: no undo for a single-OK toggle, icon-only pills, and the box runs with animations off.
- **Lesson from the Fire TV screensaver:** mocks scored 31–34 but the real on-TV screenshot scored 28–30. Always score a real TV screenshot, not just the mock.
- **Scores:**
  - Home screen: 36 → 37/40, audit 15 → 17/20 (10-21 to 10-22).
  - Wind-down: 35/40, 18/20.
  - Sports: 35/40, 18/20.
  - Doorbell PiP: 34–35/40.
  - Up next mock: 37/40.
- **Typical findings fixed:**
  - A reflexive OK fired "Yes": added a 1 s input guard.
  - The pending ring widened a button and clipped its neighbour.
  - A doorbell player left open could burn in its static chips.
  - "retry" was orphaned on its own line.
- **Mock caveat:** FigCraft doesn't have Barlow, so the mocks render in a fallback face. Barlow is narrower, so the real build has more slack.

### Other details worth a line

- The SHIELD's stock launcher HOME filter has priority 2 and the custom one has 0. `set-home-activity` prints "Success" and changes nothing until the stock launcher is disabled.
- GeForce NOW lives inside the package upstream's SHIELD list disables as dead. o kept it.
- Usage access is granted over ADB so that "Last opened" also counts apps started from remote buttons.

## 3. Images

Copied to `img/`. 4K shots were downscaled to 1920 wide.

| File | Source | Notes / privacy |
|---|---|---|
| `01-stock-home-ads.png` | `tv/shots/shield/03-after-ads-disabled.png` | Stock Google TV home with a sponsored banner and "Free Live TV" rows. **Flag:** a local TV-station tile names the metro area. Crop or blur it if location matters. Third-party show art. |
| `02-upstream-cleanyourtv-default.png` | `tv/shots/shield/04-new-launcher.png` | Upstream launcher as shipped (Outfit, glass pills). Pills read "Inputs / Ethernet". Clean. |
| `03-walnut-night-on-tv.png` | `tv/shots/shield/walnut-v29.png` | Final Walnut Night home, a real TV screenshot. Shows weather and inside temperature only. Clean. |
| `04-figcraft-before-after.png` | `personal-artifacts/tv-launchers/shield/walnut-night-before-after.png` | FigCraft board: before, after and palette swatches. Small text. Clean. |
| `05-figcraft-walnut-mock.png` | `.../shield/walnut-night-mock.png` | Early FigCraft mock (blurred banner hero, which was later rejected). Good for "what we threw away". Clean. |
| `06-wind-down-on-tv.png` | `.../shield/winddown/on-tv-ask.png` | Wind-down card on the real TV over a show. Third-party video behind it. Clean. |
| `07-sports-start-card-mock.png` | `.../shield/winddown/sports-start-card.png` | Sports Start? card mock on a placeholder scene. Clean. |
| `08-up-next-doorbell-mock.png` | `.../shield/v24-doorbell-bottom-right-mock.png` | Home with the Up next row and the doorbell PiP slot (a grey placeholder, no camera image). Movie posters are third-party art. Clean of private data. |

Other usable images, not copied:

- `personal-artifacts/tv-launchers/shield/winddown/`: `wind-down-mock.png`, `sports-on-now-toast.png`, `on-tv-confirm.png`, `on-tv-cancelled.png`.
- `.../shield/upnext/v15-onTV-*.png`
- `.../firetv/home/v15-online.png`
- `.../firetv/screensaver/on-tv-2026-10-22-final.png`

**Avoid:**

- `tv/shots/shield/doorbell-exo.png` and `doorbell-rtsp.png`: real doorbell camera frames.
- `v16`–`v22` guest/cast mocks: they show the guest Wi-Fi name and maybe a QR.
- `01-stock-home.png`: a Google screensaver photo, credited to a third-party photographer.
- Anything with a terminal or ADB output: IPs.
