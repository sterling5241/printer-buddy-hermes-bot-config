---
name: pb-pr-review
description: Printer Buddy PR checklist; use with gilfoyle.
---

# Printer Buddy review checklist

Use together with the gilfoyle skill when reviewing a Printer Buddy PR.

## Getting the PR
- Work in ~/.hermes/work/<repo>-pr-<N>. Clone https://github.com/sterling5241/<repo> there if missing, then `git fetch origin pull/<N>/head:pr-<N>` and `git checkout pr-<N>`.
- Diff locally against the PR's base branch (usually nightly). Never use the GitHub .diff endpoint.
- Run tests in that folder. Never touch ~/printer-buddy.
- Repos: printer-buddy (core), print-buddy-ui, print-buddy-notify, print-buddy-timelapse, print-buddy-streamer, printer-buddy-docs.

## Look hard at
- app/main.py route order: the POST catch-all /api/printers/{pid}/{action} must stay below specific POST routes.
- API and SSE changes the UI relies on (/api/events snapshot and per-printer events).
- updater.py and parts: reset --hard, part replacement, needs: lines, release tags.
- The API has no auth: anything that reboots, writes printer files or proxies Moonraker needs an Origin/Host check. TunnelGuard must keep /api off the tunnel.
- UI changes: compare with Fluidd and Mainsail in ~/.hermes/reference and say what they do.
- House style: comments only on complex code, one-line commit messages, flag unrequested extras.
