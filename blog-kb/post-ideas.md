# Post ideas

Drawn from real projects. All must pass the privacy rule in `../CLAUDE.md` (no internal IPs,
hostnames, VLAN maps, keys, camera positions). Voice: first-person build log, like lumber-rack.

## Homelab / AI (strongest current material)

1. **My AI agents run at home now** — the local-first coaching loop: a 31B model on a workstation
   GPU does the work, a frontier model reviews and patches its skills/hooks until it graduates to
   unattended. The "trust ratchet" concept is the hook. Flagship post.
2. **The watchdog that watched the watchman** — an AI monitoring agent missed a 6-day ZFS pool
   outage; a small deterministic shell script now does that job. Honest lessons about where LLMs
   don't belong. Pairs with #1 as the counterweight.
3. **How I almost lost 130 GB of family photos** — the Immich ZFS mountpoint-shadowing incident:
   what happened, how it was recovered, and the 3-2-1 backup rules it forced.
4. **Building a smarter Slickdeals** — the wishlist deal-watcher: local embeddings for matching,
   a vision model verifying listings against their photos, self-built price history.
5. **De-clouding the doorbell** — Reolink doorbell + Frigate NVR with local face recognition;
   why cameras live on an isolated network (keep architecture-level only).
6. **A disc ripper that files its own movies** — the ARM auto-rip → Jellyfin pipeline and its
   many gotchas (tray udev events, TMDB auto-ID, the mover).
7. **Homelab tour 2026** — Proxmox + LXC + reverse proxy + SSO architecture; the "why self-host"
   essay that anchors the whole category.
8. **I let an AI manage my smart home** — Claude managing Home Assistant dashboards/automations
   under a tiered-trust policy; what it's allowed to touch and why.

## Home / workshop

9. **Lumber rack: six months of load later** — natural sequel to the existing post: what held,
   what sagged, what I'd change. Cheap to write, great continuity.
10. **CAD faster with an AI copilot** — the Onshape + LLM ideation/structural-sanity workflow
    already hinted at in the lumber-rack post, expanded into a method.
11. **F150 build log kickoff** — the 1996 OBS truck series opener; homepage promises truck
    content and there are zero posts.

## People / meta

12. **Wiring a church** — volunteering as network admin for a camera-heavy campus; designing for
    a building that's empty on weekdays and packed on Sundays. Extra privacy care (it's a real,
    identifiable site — keep it anonymous and architectural).
13. **Tracking macros without a subscription** — replacing a paid macro app with a self-built
    tracker calibrated against watch TDEE data.
14. **How this blog works** — Hugo + PaperMod + GitHub Actions + the dark aurora theme; the
    meta-post, links back to "A New Foundation".
