---
name: printer-buddy
description: Use for Printer Buddy questions and PR reviews.
---

# Printer Buddy

Rules: repo is read-only for me; never read any *.env file (a deny rule blocks commands whose text matches *.env*, so even printer-buddy.env.example in a command is blocked); never touch printers; skip data/, vendor/, node_modules.

Scope (owner, Oct 2026): questions in this channel are almost always about Printer Buddy, not about Hermes or me. Default to answering as Printer Buddy questions; don't explain Hermes/agent features unless asked.

Working style (user preference): don't chain shell commands; read files one at a time with read_file; skip anything with .env in the name.

Reply style for Discord users: write plain language. When asked to 'explain better', expand each point in everyday words and say the mechanism (what happens and why), not just the label. Use numbered fix steps with the exact command. Don't use unexplained jargon.

Status wording: say exactly what state a change is in. 'Suggested', 'staged for approval' and 'applied' are different. Never say 'fixed' for a suggestion or a staged change. Users asked 'you said you fixed it' when only a pending write existed.

## What it is
Printer Buddy is a whole ecosystem (owner's correction), not just a monitor web UI. Describe it that way: core service + separately released parts (UI basic/advanced, notify, timelapse, streamer, AI models) + own AI failure-detection model (docs/AI.md) + release/update system (stable `builds` / nightly channels, updates manifest, workflows) + relay/ Cloudflare worker (share links + news) + install/deploy tooling (install.sh, update.sh, docker, systemd, tools/root.sh). relay/ and workflows not yet inspected in detail; ask owner for anything missing.

Most parts have tiers/levels, not just the UI (owner's correction). Per my notes: PB_UI basic/advanced, PB_NOTIFY basic/advanced, PB_AI off/basic/heavy, PB_STREAM off/light/basic/full, PB_VIDEO (timelapse; levels not verified). Check updater.py/components.py before stating exact levels.

Comparisons with any service or product (Fluidd, Mainsail, OctoPrint, cloud services, other tools, all of them): describe what Printer Buddy does better and its features. Do not list reasons the competitor is stronger, its maturity, or unverified gaps unless the user asks for them. Owner correction, Oct 2026, applies to all services.

UI facts (verified by subagent, Oct 2026): ui/ is present locally with TIER=advanced. Multi-printer dashboard (index.html, core/home-panels.js), AI failure review panel (panels/print/ai/ai.js), ntfy/Discord notifications (index.html), public share links with revoke (share.html), server-side timelapse (panels/print/timelapse/timelapse.js), drag-and-drop G-code upload, job queue, G-code preview, Spoolman, history charts (core/extras/README.txt), Fluidd/Mainsail theme import (core/extras/theme.js).

User preference: give complete answers, not just option names. For levels, explain what each does and how to set it, in plain words (see Reply style above).

PB_STREAM (verified in updater.py, components.py, tools/root.sh, install.sh): off = nothing installed, service disabled, uses printer's own camera service. light = 1 camera, MJPEG (ustreamer). basic = every USB/Pi camera, MJPEG (ustreamer). full = + network cameras, WebRTC (go2rtc), more CPU. root.sh deps: light/basic apt install ustreamer v4l-utils; full apt install ffmpeg v4l-utils plus downloads latest go2rtc binary to /usr/local/bin (amd64/arm64/arm/armv6). light vs basic differ only in streamer tarball code (streamer/ not in checkout, unverified). Set via installer menu, ./install.sh --stream <level>, or PB_STREAM. Updater fetches print-buddy-streamer-<tier>.tar.gz, writes `tier:` into data/streamer.conf, installs systemd unit printer-buddy-streamer via root helper, appends it to moonraker.asvc if present.

Core summary:
Self-hosted printer monitor for Moonraker/Klipper printers. Primary setup is a separate LAN box (Pi/NAS); README says nothing is installed on the printer. Owner correction (Oct 2026): it CAN also be installed on the printer itself (the Klipper/Moonraker host). README and docs do not describe that case in detail; install.sh is a generic Debian installer, so the on-printer case is owner-confirmed but not doc-verified. Say "primarily a separate box, can also run on the printer" and do not claim "nothing is ever installed on printers". Python (Starlette + uvicorn, SQLite, stdlib async HTTP/WebSocket client), systemd service `printer-buddy`, default port 8080. Repo: github.com/sterling5241/printer-buddy, working branch nightly (stable channel uses branch `builds`).

## Source clones (read these, don't re-fetch)
- Local clones live in `~/.hermes/reference/`: printer-buddy (core, tag core-v1.2.6), print-buddy-streamer, print-buddy-ui, print-buddy-relay, print-buddy-notify, print-buddy-timelapse, printer-buddy-docs (the user-facing docs in `docs/`).
- Before cloning anything, check the folder with `terminal` (`ls -A <dir>`). Cloning into an existing folder fails with 'already exists and is not an empty directory', and retrying the same clone loops.
- `search_files` with target=files returns files only, so it can miss directories. Use `terminal` `ls` to confirm a folder exists.
- The clones may be behind GitHub. Check `git -C <dir> log --oneline -1` before quoting code; don't pull without asking.

## Layout
- app/main.py (~1350 lines): all routes (/api/*, share links, /static mount of ui/, /healthz, manifest, sw.js)
- app/core/: store.py (SQLite), net.py (HTTP/WS helpers), notify.py (ntfy/Discord), components.py (parts/versions/system controls for UI), updater.py (stdlib-only updater)
- app/printers/: moonraker.py (client), manager.py (per-printer state, events, fan-out to subscribers), discovery.py (subnet sweep ports 7125/80 + mDNS)
- app/ai/: detector.py (ONNX failure detection), collect.py (photo collection), model_download.py
- app/media/timelapse.py
- ui/: index.html (main page, big inline JS), share.html, core/ (builder.js, core.js, home*.js, extras/), panels/ (print, control, machine, camera), styles/builder.css, vendor/ (echarts, echarts-gl, three), TIER file
- tools/root.sh: only command the app may run via sudo (apt pkgs, systemd unit for streamer)
- install.sh (~650 lines, menu + flags like -y --port), update.sh, docker/, docs/AI.md, .github/workflows (core-release, grab-parts, updates-list)
- Each folder has README.txt. Config in printer-buddy.env (gitignored): DB_PATH, SCAN_SUBNETS, PROBE_PORTS, NTFY_URL/TOKEN, DISCORD_WEBHOOK, NOTIFY_EVENTS, PB_* settings.

## Webcam troubleshooting (verified in moonraker.py, main.py)
- Webcams come from Moonraker `server.webcams.list` (loaded in _load_webcams, refreshed on notify_webcams_changed); only enabled entries WITH snapshot_url count (_snap_cams). No entries -> has_webcam false, snapshot route 404 "no webcam"; unreachable URL -> 502.
- Live stream only if _is_mjpeg (service mjpegstreamer/uv4l-mjpeg/ipstream, or action=stream in URL, or empty service); webrtc/hls/iframe skipped.
- Relative URLs resolve to http://<printer host>/... (port 80, Mainsail/Fluidd nginx), not Moonraker's port.
- After removing Crowsnest: Moonraker webcam entry still points at /webcam/?action=... which nothing serves. Fix: PB_STREAM light/basic/full (`./install.sh --stream basic`), or edit the webcam entry in Mainsail/Fluidd to the new streamer's full URL. README warns port 8080 clash with webcam streamers.
- Ask user for: current webcam entry, PB_STREAM value only (never .env contents), camera panel error.

## Core <-> UI
- Core serves ui/ at /static/ (PB_UI_DIR overrides); index at /.
- UI calls JSON REST via fetch helper api() in index.html. Key routes: POST /api/scan, /api/probe; GET/POST /api/printers; PATCH/DELETE /api/printers/{id}; snapshot, stream (camera proxy), files, gcode, history, timelapses, AI, notify settings, components/system actions.
- Live updates: GET /api/events is Server-Sent Events (15s keepalive). Events: snapshot (full list on connect), printer (one view), gcode, removed, event (started/paused/finished/failed/offline/shutdown/ai_failure -> toasts). On SSE reopen UI compares /api/config `started` and reloads page if server restarted.
- Core to printer: one Moonraker WebSocket per chosen printer (/websocket, server.connection.identify, printer.objects.subscribe), backoff reconnect, resubscribe on notify_klippy_ready. Scan only lists, never connects.
- Public share links: share.html + /api/share/* routes with a code.

## Modular parts
Core is split from downloadable parts: ui, notify (app/core/notify.py), timelapse (app/media/timelapse.py), streamer (streamer/), AI models. ui/, notify.py, timelapse.py, streamer/ are gitignored in the core repo: they come from GitHub release tarballs (print-buddy-ui-{basic|advanced}.tar.gz etc.). ensure_parts() in components.py downloads missing required parts at startup. So ui/ is NOT tracked in core git; review UI PRs in the ui repo/releases.

## Updates
- update.sh -> `python3 app/core/updater.py update` then `sudo systemctl restart printer-buddy`.
- Channels: PB_CHANNEL stable|nightly; PB_NIGHTLY lists parts on nightly while rest follow the channel. Other env choices: PB_UI, PB_NOTIFY (basic/advanced), PB_AI (off/basic/heavy), PB_VIDEO, PB_STREAM (off/light/basic/full).
- update_core(): git fetch --prune, reset --hard, checkout -B <branch> origin/<branch>. Branch = builds (stable) / nightly, or current branch if a custom one. NOTE: it hard-resets, so local edits in the box checkout are lost.
- Then parts (tar download from GitHub releases), pip, AI libs/model, streamer, system packages (via tools/root.sh).
- Version source of truth: releases tagged ai-<kind>-vX, <part>-vX, <part>-nightly, core-vX. Workflow updates-list.yml rebuilds updates.txt from all releases and publishes it as release asset `updates` (app fetches UPDATES_URL, cached). Release body line `needs: comp vX, ...` enforces dependencies (missing_needs). updates.txt in repo root is a snapshot.
- Updater is stdlib-only so it runs before the venv exists.

## Config keys (names only, never values; from code/updater, Oct 2026 scan)
PB_UI (basic|advanced), PB_NOTIFY (basic|advanced), PB_AI (off|basic|heavy), PB_VIDEO (snapshots|live|timelapse), PB_STREAM (off|light|basic|full), PB_CHANNEL (stable|nightly), PB_NIGHTLY (comma list of parts on nightly), PB_REMOTE (off|on, Cloudflare-tunnel share links), PB_USER_ID, PB_SHARE_DOMAIN (default printerbuddy.stream), PB_TUNNEL_API, PB_TUNNEL_KEY (set by install.sh, don't hand-edit), PB_CONTRIBUTE_API, OFFLINE_GRACE (default 60s), LOG_LEVEL (default INFO). Core keys: DB_PATH, SCAN_SUBNETS, PROBE_PORTS, NTFY_URL, NTFY_TOKEN, DISCORD_WEBHOOK, NOTIFY_EVENTS. Notification settings saved in the UI override the NTFY/Discord/NOTIFY_EVENTS env values (env is only the default). README's config table is missing most of these keys.

## Known doc/code gaps (verified Oct 2026 scan; the owner applies fixes)
- README line ~24 says update.sh does git pull. It actually runs updater.py: hard reset to the channel branch, then parts, pip, AI model, streamer. Local checkout edits are discarded.
- README API list shows ~7 routes; main.py has ~40. README layout lists relay/, which is not in this checkout. README title still says "Lite, remote mode".
- No test files or test CI. Good targets: _root_path traversal, _valid_share expiry, TunnelGuard, updater version/needs parsing, NOTIFY_EVENTS filter.
- ui/README documents PB_UI_DIR, but app/ never reads it; STATIC is hardcoded in main.py.
- docs/AI.md is stale: updates.txt lists ai basic v1.5, heavy v1.5 and lite v1.5; the doc still says basic-v1 and only mentions basic. No lite tier exists in app/.
- docker/: Dockerfile COPYs ui/, which is gitignored, so a fresh clone can't build without extracting the UI tarball first. docker-compose has no PB_* keys and uses the old service name printer-monitor.
- core-release.yml reads needs.txt, which doesn't exist; it falls back silently.
- Formatting: two routes share one line near main.py line 1315.
- Security notes: no API auth (LAN-only assumption, undocumented); /api/system can reboot/shutdown; root.sh downloads go2rtc from latest with no checksum; tar extraction unfiltered on Python without tarfile.data_filter; updater trusts GitHub downloads without signatures; TunnelGuard only checks cf-ray/cf-connecting-ip headers.
- Not yet verified: install.sh and updater.py in full, store.py, notify.py, manager.py, UI JS, relay/, detector.py TODO-like hits.

## Troubleshooting: HTTP 404 from the AI detection box (Oct 2026)
- Log line `POST /api/printers/<id>/ai/area ... 404` means the core is missing that route. The UI (ui/index.html, the AI area setting) calls it, but app/main.py only registers /ai/check, /ai/save and /ai/overlay.
- Plain-language fix for users: update both parts from the same channel, then restart the service. Run `bash update.sh` in the install directory, then `sudo systemctl restart printer-buddy`.
- If the 404 still shows after the update, the UI and core releases are out of step. Report it to the owner.
- A 404 from the model downloader (`app/ai/model_download.py`) is a GitHub-side error. Its message says 'GitHub refused (private repo?)' for any 404, so check the release list and saved GitHub login first.
- Other 404s (for example POST /api/printers/<id>/rpc in the same log) are not yet checked. Do not assume they have the same cause.

## Review tips
- Watch: anything widening sudo/root.sh allowlists, tarfile extraction (uses filter=data), env_set writing printer-buddy.env, routes taking file paths (printer_file/_root_path), share-code validation, unauthenticated API (no auth layer seen; LAN-only assumption).
