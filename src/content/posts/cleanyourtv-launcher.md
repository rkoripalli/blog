---
title: "Cleaning Up My TV, Then Making It Mine"
date: 2026-11-13
description: "How I took the open-source CleanYourTV launcher, ran it on my NVIDIA SHIELD, and gave it my own design and Home Assistant smarts."
draft: false
tags: ["home automation", "home assistant", "design", "projects"]
cover:
  image: "images/cleanyourtv-launcher/cover.jpg"
  alt: "Same launcher, same TV, a day apart: CleanYourTV as it ships on the left, my Walnut Night version on the right"
---

My SHIELD's home screen had slowly turned into a billboard: a sponsored banner, "Free Live TV" rows, and carousels of shows I'd never watch. The apps I actually use were one row out of six.

![The stock Google TV home: a sponsored banner, free live TV and trending rows](/images/cleanyourtv-launcher/stock-home.jpg)

## Step 1: CleanYourTV on the SHIELD

In October, Gathin's [CleanYourTV](https://github.com/Gathin23/cleanyourtv) went viral. You turn on network debugging, paste one prompt into a coding assistant like Claude Code, and it does the rest over Wi-Fi. It disables the ad and telemetry packages without uninstalling anything, then builds and installs a small, clean launcher. You don't need root, and one command restores everything. It's MIT licensed.

I ran it on my SHIELD TV Pro, and it disabled 26 packages in an evening. I kept GeForce NOW, which the SHIELD list treats as dead weight. One SHIELD gotcha: the stock launcher outranks any new one, so switching the home app reports "Success" and changes nothing until the stock launcher is disabled.

![The CleanYourTV launcher as it ships](/images/cleanyourtv-launcher/upstream-launcher.jpg)

## Step 2: Walnut Night

The stock launcher is cool blue glass. My Home Assistant dashboards are warm, dark walnut, and I wanted the TV to feel like the same house. With Claude, I wrote the look down as a small design system before touching code:

* **Warm browns, amber only for focus.** No glass, glow or gradients.
* **Barlow type** and square app tiles, seven across.
* **A big title naming whatever has focus**, with a line under it that's never empty: "Last opened yesterday, 11:11 PM", or an error like "Couldn't open Netflix · OK to retry" instead of a toast.
* **A ring means focus or a problem, never "on".**

Every change started as a mock in FigCraft, a design tool Claude can drive. I approved each mock before any code, then a design-review pass scored it until the score stopped improving. Plenty got thrown out along the way, like this blurred-banner hero.

![An early mock with the blurred banner hero, which I rejected](/images/cleanyourtv-launcher/rejected-banner-mock.jpg)

The biggest lesson: a screenshot of the real TV always scored a little worse than the mock, so score the real screen.

![The finished Walnut Night home screen on the TV](/images/cleanyourtv-launcher/walnut-night-home.jpg)

## Step 3: The Receiver Follows Along

The SHIELD feeds my Denon receiver directly, so movies keep lossless surround. The launcher itself has no volume or input buttons; Home Assistant drives the receiver around it instead:

* **Sound follows the app.** Jellyfin puts the receiver in Direct mode, YouTube gets a music mode, and everything else plays in Dolby surround.
* **Movie mode** dims the lights when a movie plays and brings them up on pause.
* **It cleans up after me.** The receiver drops to standby after 30 idle minutes, and late at night a few minutes of screensaver puts the whole stack to sleep.

## Step 4: Home Assistant on the Home Screen

The header shows the weather and inside temperature, and a pill toggles movie mode. The TV holds no Home Assistant token and opens no port. Home Assistant publishes a small status file the launcher reads, and pushes cards to it over the connection it already has to the SHIELD.

Those cards all share one corner, with a fixed pecking order:

* **Doorbell:** a small live camera card over whatever's playing. It doesn't pause the show and closes after 10 seconds.
* **Wind down:** once a night it asks if I'm heading to bed. Yes warms the lights and starts a 30-minute sleep timer.
* **Game day:** if one of my teams kicks off while the TV is in use, it asks before switching.

![Up next row and the doorbell card's slot in the corner](/images/cleanyourtv-launcher/up-next-doorbell-slot.jpg)

I also built a whole-house music card and deleted it the same afternoon. Pressing play switched the receiver away from the TV's input, so the card made itself disappear. Some ideas only turn out bad on the real TV.

## What I'd Do Differently

Fork it instead of downloading a zip. CleanYourTV has moved fast since I copied it, and I have no clean diff to merge back from.

Huge thanks to Gathin. If your TV's home screen has turned into an ad, [start there](https://github.com/Gathin23/cleanyourtv).
