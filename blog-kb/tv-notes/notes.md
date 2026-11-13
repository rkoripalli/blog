# Blog notes: CleanYourTV on the SHIELD, made ours (raw, 2026-11-13)

**Angle:** we took an open-source TV de-bloat project, ran it on our NVIDIA SHIELD, and rebuilt its launcher around our own design. We also tied it into the AV receiver and the house.

**Target length:** about 1,000–1,300 words and 5–6 images. Stay out of the weeds: no colour hex lists, class names or plumbing.

Public post: no IPs, hostnames, tokens, IDs or camera details.

---

## Suggested outline

1. **Hook:** the stock Google TV home is an ad board (`img/01`).
2. **CleanYourTV:** what it is, and credit to Gathin.
3. **Running it on the SHIELD:** the ads are gone, and the upstream launcher looks good (`img/02`).
4. **Making it ours: Walnut Night.** Show upstream next to ours (`img/02` next to `img/03`).
5. **How we designed it:** mock, review, repeat.
6. **Beyond the home screen:** receiver and house controls, the cards.
7. **What we threw away, and wrap-up.**

---

## 1. CleanYourTV (the starting point)

- An open-source project by Gathin (github.com/Gathin23/cleanyourtv, MIT licence).
- How it works: you hand a prompt to a coding assistant like Claude Code. Over Wi-Fi it switches off the TV's ads, tracking and preloaded junk, then installs a clean "Apple TV-style" home screen. No root, nothing uninstalled, one-line undo.
- Origin: a 17 Oct 2026 before/after tweet of his parents' TV went viral (7.4M views). It became the #1 trending repo of the week, and people have since added well over 100 TV models.
- Its launcher is small, readable and built to be customised. That's what made the rest of this possible.

## 2. Why the SHIELD, and what happened on it

- The SHIELD is the main streaming box. It feeds the receiver directly, so Jellyfin movies keep their full lossless surround audio.
- De-bloat: 26 things switched off, nothing uninstalled. One package alone produced the sponsored hero banners and the "Free Live TV / Top Selling" rows.
- The upstream de-bloat list for the SHIELD would have killed GeForce NOW: on this box, the "dead" NVIDIA Games package *is* GeForce NOW. Live Channels was kept too, for the antenna tuner. Worth one sentence: check the list against your own box.
- The SHIELD resists replacement launchers. Its stock home screen outranks any new one, so the "set as home" command reports success and changes nothing until the stock launcher is disabled. Possibly one line.
- On day one the upstream launcher went in almost untouched: just our apps in the dock. It looked good. The same evening we decided it should look like the rest of our house instead.

## 3. Making it ours: "Walnut Night"

- **Why:** our Home Assistant dashboards already use a warm, dark walnut palette. The TV should feel like part of the same home, not a generic Apple TV clone.
- **Upstream vs ours, at a glance:**
  - Cool graphite, sky blue and frosted glass → warm walnut browns, a single amber focus colour, flat solid surfaces with no glow.
  - Outfit font → Barlow, with a condensed face for headings.
  - Full app banners → square logo tiles.
  - Clock + pills → a header with greeting, clock, date, outdoor weather and indoor temperature, plus three round buttons (Doorbell, Movie mode, Settings).
  - Big name of whatever has focus, with a helpful line under it ("Last opened yesterday, 11:11 PM").
- **A few rules worth quoting:**
  - Amber means focus. Nothing else gets to be amber.
  - No pop-up toasts. Hints and errors appear right under the title where you're already looking ("Couldn't open Netflix · OK to retry").
  - Hold OK on an app to pick it up and move it.
- **One spec, two TVs:** the same design runs on our Panasonic Fire TV. The only difference is a blue accent instead of amber.

## 4. How we designed it

- Every change starts as a mock in FigCraft, a Figma-like design tool Claude drives. o approves the mock before anything is built.
- Each mock then goes through Impeccable, an automated design review: a usability score out of 40 plus a platform audit. We fix what it finds and score again, until the score stops climbing.
- The home screen finished at 37/40.
- Lessons:
  - Score a photo of the real TV, not just the mock. A mock that scored 34 came in around 30 on the actual screen.
  - The review can't tell you a feature is pointless; only using it can (see the Now Playing card in section 6).

## 5. Receiver and house controls

The launcher became the TV's remote for the house, not just an app grid.

- **Sound follows the app:** when the SHIELD opens Jellyfin, the receiver goes to Direct mode for lossless movie audio. YouTube gets a music mode, everything else a Dolby surround mode. Nobody touches the receiver remote.
- **Movie mode button:** one press on the home screen. The lights dim when you press play and come back up when you pause.
- **Fire TV source buttons:** the Fire TV's launcher has tiles for SHIELD, Switch and AirPlay. One press switches the receiver's input and points the TV at it.
- **Bedtime wind-down:** after 11 PM a small card asks "Wind down for bed?". Yes warms the lights to amber and turns off the SHIELD, TV and receiver 30 minutes later.
- **"How do I play to this?" corner:** Cast → SHIELD, AirPlay → receiver, plus a guest Wi-Fi QR code.
- **Privacy note for the post:** the TV holds no Home Assistant password or key. One sentence is enough.

## 6. Other cards (keep to a line each)

- **Doorbell:** a small live video card in the corner over whatever's playing, for 10 seconds. The first version paused the show and sat in the corner for 30 s. It was too much, so we toned it down.
- **Sports:** "#17 Florida at #3 Georgia · kicks off 2:30 PM · [Watch] [Not now]".
- **Up next:** your Jellyfin shows to continue, under the dock.
- **The one we deleted:** a Now Playing music card. It was built, scored well and installed, then removed the same afternoon, because pressing play switched the receiver away from the TV.

## 7. Wrap-up material

- Timeline: stock upstream on 21 Oct, our design finished 22 Oct, extras through early November.
- Credit Gathin again. Point readers at the repo, and encourage them to make it their own rather than run it as shipped.

---

## Images (`img/`)

Use 5–6 of these.

| File | Use | Privacy |
|---|---|---|
| `01-stock-home-ads.png` | Hook: the stock home with ads | **Crop or blur** the local TV-station tile, which names the metro area |
| `02-upstream-cleanyourtv-default.png` | CleanYourTV as shipped | Clean |
| `03-walnut-night-on-tv.png` | Our final home screen (real TV) | Clean |
| `04-figcraft-before-after.png` | The design board | Clean |
| `06-wind-down-on-tv.png` | Wind-down card on the TV | Clean |
| `08-up-next-doorbell-mock.png` | Up next + doorbell corner (placeholder) | Clean; posters are third-party art |
| `05-figcraft-walnut-mock.png` | Optional: early mock with the blurred banner we dropped | Clean |
| `07-sports-start-card-mock.png` | Optional | Clean |

**Avoid:**
- real doorbell camera frames
- the guest Wi-Fi mocks
- anything with terminal output
