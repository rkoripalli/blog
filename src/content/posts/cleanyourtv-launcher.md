---
title: "Cleaning Up My TV, Then Making It Mine"
date: 2026-11-13
description: "How I took the open-source CleanYourTV launcher, gave it my own design system, and wired it to Home Assistant for doorbell, bedtime and game-day cards, without putting a single token on the TV."
draft: false
tags: ["home automation", "home assistant", "design", "projects"]
cover:
  image: "images/cleanyourtv-launcher/cover.jpg"
  alt: "Same launcher, same TV, a day apart: CleanYourTV as it ships on the left, my Walnut Night version on the right"
---

My SHIELD's home screen had slowly turned into a billboard. There was a sponsored banner at the top, then "Free Live TV" rows, then a carousel of shows I'd never watch. The apps I actually use were one row out of six.

![The stock Google TV home: a sponsored banner, free live TV and trending rows](/images/cleanyourtv-launcher/stock-home.jpg)

## Step 1: CleanYourTV

In October a project called [CleanYourTV](https://github.com/Gathin23/cleanyourtv) by Gathin went viral. It started as a before-and-after tweet of his parents' TV. The idea is clever. You turn on network debugging, paste one prompt into a coding assistant like Claude Code, and the assistant does the work over Wi-Fi:

* it backs up the package list
* it disables the ad, telemetry and preload packages, without uninstalling anything
* it builds and installs a small native launcher that looks a lot more like an Apple TV

You don't need root or a cable, and a one-line command restores everything. It's MIT licensed, and the community has since added well over a hundred TV models.

I ran it on my SHIELD TV Pro. It disabled 26 packages, and the stock launcher was gone in an evening.

![The CleanYourTV launcher as it ships](/images/cleanyourtv-launcher/upstream-launcher.jpg)

That alone would have been worth a post. But the upstream launcher's cool, glassy look didn't match anything else in my house. Because the whole thing is a small Java app, I could change whatever I wanted. So I did, quite a lot.

**One gotcha:** on the SHIELD, the stock launcher's HOME filter outranks any new one. `set-home-activity` happily prints "Success" and changes nothing until the stock launcher is disabled.

## Step 2: A Design System Called Walnut Night

My Home Assistant dashboards use a warm, dark walnut palette, and I wanted the TV to feel like part of the same house, not a generic Apple TV clone. Working with Claude, I wrote down how it should differ from upstream before touching any code:

| | CleanYourTV | Walnut Night |
|---|---|---|
| Palette | cool graphite, sky blue, white glass | warm walnut browns, amber focus |
| Surfaces | translucent glass, glow behind the dock | solid layered surfaces, no glow |
| Type | Outfit | Barlow and Barlow Semi Condensed |
| Tiles | full app banners | square logo tiles, 7 across |
| Header | clock, date, Inputs and network pills | greeting and clock, date and weather, three round icon pills |
| Focus | glass highlight and glow | amber ring set just off the tile, other tiles slightly faded |
| Feedback | toasts | hints and errors inline under the title |

Then the colours became a proper set of tokens:

| Token | Hex | Role |
|---|---|---|
| ground | `#13100E` | background |
| surface | `#1D1916` | dock band |
| raised | `#28221E` | idle pills |
| text | `#F0E9E0` | primary text |
| muted | `#BFB3A5` | secondary text |
| accent | `#F2B46B` | focus only |
| copper | `#C9844E` | moving an app |
| rust | `#E07154` | failures |

A few rules did most of the work:

* **A ring always means focus, work in progress or failure.** It never means "on". "On" is a neutral fill with a small dot.
* **Flat everything.** No glow, no glass, no gradients.
* **Barlow** for body text and **Barlow Semi Condensed** for the big title, replacing upstream's Outfit.
* **The hero line is never empty.** The big title names whatever has focus, and the line under it always says something useful, like "Last opened yesterday, 11:11 PM". Errors go there too, in rust ("Couldn't open Netflix · OK to retry"), instead of a toast that vanishes.

One detail I'm unreasonably happy with: the clock column is sized to the widest time for the current number of hour digits, so the divider next to it never shifts when the minute ticks over. Tabular figures would have done the same job, but they made "11" look gappy.

## Step 3: Mock First, Then Score It

Every change started as a mock in FigCraft, a Figma-style design tool that Claude can drive directly. I approved the mock before any code was written. Then the mock went through Impeccable, a design-review skill. It scores against Nielsen's usability heuristics out of 40 and runs a native Android audit out of 20, with a separate reviewer grading exported screenshots each round. Fix, re-mock, re-score, and stop when the score stops climbing.

Plenty didn't survive. The early mocks had a blurred banner of the focused app's art behind everything, which was very "cinematic home". I didn't like it, and it went.

![An early mock with the blurred banner hero, which I rejected](/images/cleanyourtv-launcher/rejected-banner-mock.jpg)

The Inputs pill also went, because a streaming box has no inputs. The ambient glow went too, because it was off-palette. The home screen ended at 37/40 and 17/20. The reviews also called out the scores that a D-pad TV can't reach, so I didn't chase those.

The biggest lesson came from a screensaver I built for a second TV: the mocks scored 31 to 34, but a real screenshot from the TV scored 28 to 30. **Always score a photo of the real screen, not just the mock.**

![The finished Walnut Night home screen on the TV](/images/cleanyourtv-launcher/walnut-night-home.jpg)

Because it's all tokens, the same spec now runs on a second TV in the house as well. The only change there is a blue accent instead of amber.

## Step 4: Home Assistant, With No Token on the TV

I wanted the launcher to know about the house: weather, the inside temperature, whether movie mode is on, and the doorbell. I didn't want a long-lived Home Assistant token sitting on a TV box, or a TV box listening on a port. So the link runs in two directions without either:

* **Pull:** Home Assistant writes a small status file into its own static web folder, and the launcher polls it every five minutes while the home screen is visible. If anything fails, the line just hides, so Home never waits on the network.
* **Push:** Home Assistant already talks to the SHIELD through its Android TV integration. It sends broadcasts to receivers in the launcher, and those receivers are locked down so only the debugging shell can reach them.
* **Answers:** when you press a button on a card, the launcher posts a tiny answer like `{"answer":"yes"}` back to a Home Assistant webhook.

The "Up next" row works the same way. Home Assistant asks my Jellyfin server what I'm partway through and writes a file, so the TV doesn't need a Jellyfin token either. The rule there was "24 min left must never lie": data older than six hours hides the row. It uses series art, never episode stills, because stills are unreadable as tiles and can spoil the episode.

## Step 5: The Cards

Everything that pops up over an app shares one slot in the bottom-right corner, with a strict pecking order. The doorbell beats the bedtime card, which beats a game prompt, which beats a "game is on" toast. A higher card hides a lower one, and a lower card waits its turn.

![Up next row and the doorbell card's slot in the corner](/images/cleanyourtv-launcher/up-next-doorbell-slot.jpg)

**Doorbell.** When someone rings, a small live camera card appears over whatever's playing. Version one paused the show and sat in the top corner for 30 seconds. After living with it for two days, I changed it to never pause, close after 10 seconds, shrink, and move to the bottom-right. It also stays invisible until the video is actually smooth, so you never see a stuttering stream. It can't take focus, so the remote keeps driving the app underneath.

**Wind down.** Once a night, late, the TV asks whether I want to wind down for bed. Yes warms the lights behind the TV to amber and starts a 30-minute sleep timer for the TV and receiver. OK and Back are ignored for the first second, so a press meant for the show doesn't answer the card by accident. There's a five-second "Back to cancel" undo. It went from 28 to 35 out of 40 over three review rounds.

![The wind-down card over a show](/images/cleanyourtv-launcher/wind-down-card.jpg)

**Game day.** Home Assistant already started my teams' games automatically and sent a phone notification. My question was "why not tell me on the TV as well?" If the TV is already in use, it now shows a "Start?" card with the matchup, the channel and kickoff time. If the TV was off and the game just started itself, it shows a short "On now" toast.

![The sports Start? card mock](/images/cleanyourtv-launcher/sports-card-mock.jpg)

**The one I deleted.** I also built a whole-house music card with play/pause and a "play here" button. It scored well, and I removed it the same afternoon. Pressing play switched the receiver off the SHIELD's input, so the card made itself disappear. Some ideas are only bad once they're on the actual TV.

## What I'd Do Differently

* **Fork, don't download a zip.** I started from a zip, so I have 21 archived builds and handoff notes but no clean history of what I changed versus upstream. CleanYourTV has moved on a lot since I copied it, and merging that back in will hurt.
* **Score the real screen.** The mocks were always a little kinder than the TV.
* **Decide the interruption order early.** One shared corner and one priority list made every later card easy to add.

Huge thanks to Gathin for CleanYourTV. If your TV's home screen has turned into an ad, [start there](https://github.com/Gathin23/cleanyourtv).
