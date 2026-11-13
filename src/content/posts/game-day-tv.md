---
title: "The TV That Knows It's Game Day"
date: 2026-11-13
description: "How my living room TV starts the right game on its own, gets out of the way for the doorbell, matches the lights to the team, and stopped turning itself off."
draft: false
tags: ["home automation", "home assistant", "projects"]
---

<!-- DRAFT for o: needs photos (the TV wall, the on-screen game card, the LED strip in team colours). Anything in a comment like this is a note for you, not post text. -->

I watch more live sports on YouTube TV than everything else combined. When I actually looked at the numbers, it wasn't close. So the living room TV is the part of the house I use most, and it was also the part with the most fiddly little rituals: wake the SHIELD, open YouTube TV, find the channel, realise kickoff was ten minutes ago.

This is the build log for getting rid of those rituals. Everything runs locally in Home Assistant. Nothing here needs a subscription beyond the TV service itself.

## The Hardware

* **NVIDIA SHIELD** running YouTube TV, with a custom launcher I can draw cards on.
* **Denon AV receiver** driving the speakers and a subwoofer behind the couch.
* **WLED strip** behind the TV for bias lighting and team colours.
* **Home Assistant** tying it together, with an AppDaemon app doing the sports logic.

<!-- o: add the TV make/size and speaker setup (5.1?) if you want them in. -->

## Step 1: Knowing What's On

The core is a small AppDaemon app that reads a public sports scoreboard feed and decides, a few minutes before kickoff, whether a game is worth starting. My list is short and personal:

* **Always:** Texas Longhorns football, Monday Night Football, Thursday Night Football, the Houston Texans, and Rockets games when they're on national TV.
* **Saturdays:** the Longhorns win every tie. Otherwise it picks the most important college football game on at that moment.
* **Sundays:** Sunday Night Football always. In the afternoon windows the Texans come first, then the matchup with the best combined record.

Once a Longhorns or Texans game is on, it's locked. Nothing switches away from it, no matter how good the other game gets.

Each channel maps to a fixed YouTube TV link, so starting a game is just sending the SHIELD a deep link. The catch is that Sunday afternoon FOX and CBS games are regional, so the channel can be showing a different game than the one the app picked. I haven't found a clean fix for that yet.

## Step 2: Asking Before It Takes Over

Auto-starting is great until it isn't. Nobody wants the TV to hijack the movie they're watching. The rules ended up as a short policy:

* **TV off, normal day:** turn it on and start the game. This happens even if I'm out, so it's on when I walk in.
* **TV already on, or friends over:** don't switch. Put a "Start?" card on screen and send a phone notification instead.
* **Night or Vacation mode:** do nothing.

The biggest lesson came from the first real test. My original approach force-closed YouTube TV and relaunched it on the right channel. That's fine if the TV is idle, and terrible if you're already watching the game. Now it checks what's playing first. If it's already on the right channel, it does nothing at all. If it can't tell what's playing, it sends the link without killing the app.

## Step 3: A Card That Knows Its Place

The "Start?" and "On now" cards live in the bottom-right corner of the custom launcher. That corner is shared with the doorbell picture-in-picture, and the rule there is simple: **the doorbell always wins**. If someone rings during a game prompt, the game card hides and waits its turn.

<!-- o: screenshot of the game card would be great here. -->

I mocked the card up and got it looking right before writing any launcher code. That ordering saved me from at least one rebuild.

## Step 4: Team Colours Behind the TV

The LED strip behind the TV switches to the team's colours when a game starts, then steps aside when it's over. That part was fun. The bug it caused was less fun.

Some team presets split the strip into several segments, one per colour. When the game ended, the app handed control back but left those extra segments in place. Home Assistant's light entity only talks to the first segment, so for two days the strip refused to turn off: Night mode, TV off and the manual switch all only reached a fraction of it.

The fix was to have the app collapse the strip back to a single segment whenever it steps aside. I also added a belt-and-braces step to Night mode, which now turns off the whole strip at the controller rather than trusting the light entity. If you use WLED segments, check for leftovers before blaming Home Assistant.

## Step 5: The TV That Kept Turning Itself Off

For a few days the TV would shut off mid-show, roughly every hour or so. I assumed HDMI-CEC, because it's always HDMI-CEC.

It wasn't. A wind-down sleep timer I'd added had a second trigger that fired when another streaming box in the room dropped off the network for 30 seconds. The check for "is a sleep timer actually running?" sat inside the wrong branch, so with no timer set it fell through and put the whole stack to sleep. That box drops its connection every hour or so, which explained the timing perfectly.

One condition moved, and the TV hasn't turned itself off since. The lesson I keep relearning: when something happens on a schedule you didn't set, read the automation traces before you blame the hardware.

## Step 6: Fixing the Thin Sub

The last piece was sound. The subwoofer had started sounding thin, and it turned out a receiver calibration re-run had quietly reset every speaker to "Large" with a 40 Hz crossover. That sends most of the bass to the main speakers and leaves the sub with very little.

I set the fronts and centre back to Small at 100 Hz, the surrounds to 80 Hz, and settled on the sub level by ear. I also pinned the receiver to a single calibrated preset, because switching between presets automatically caused more problems than it solved. The sub sits near a corner, so there's still some boom around 35 Hz. Moving it out of the corner is next.

**Note to future me:** re-running the room calibration resets all of this. Write the settings down first.

## What I'd Do Differently

* **Read the state before you act.** Every bad behaviour here, from killing a stream mid-game to the strip that wouldn't turn off, came from acting without checking what was already happening.
* **Give interruptions a priority order.** The doorbell beats the game card, and the game card beats nothing. Deciding that up front made the UI easy.
* **Default to asking.** The TV only takes over by itself when it's off. Everything else is a prompt.

<!-- o: anything else to cover? e.g. Saturday morning GameDay wake-up, voice control, the Fire TV's role. -->
