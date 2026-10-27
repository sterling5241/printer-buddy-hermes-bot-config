---
name: print-buddy-ui-dev
description: Edit Printer Buddy UI panels, wire them, build tarballs.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Printer Buddy, Frontend, Panels, Release]
---

# Printer Buddy UI development

The `print-buddy-ui` repo is the browser front end for Printer Buddy: the home dashboard, one page per printer, and a set of panels. It is plain JavaScript and CSS with no build step, served as static files by the core app at `/static/`. This skill covers adding or changing a panel, checking the wiring, and building the release tarballs. It does NOT cover the Python core (see the `printer-buddy` skill) and does not talk to any printer.

## When to Use
- "add a panel", "new panel", "change the fans / thermals / files panel"
- "why doesn't my panel show?" (usually an unregistered file)
- "build the UI", "make the ui tarball", "how is ui released"
- "which tier does this panel show in?"

## Prerequisites
- Local checkout at `~/.hermes/reference/print-buddy-ui` (branch `main`). It is an upstream reference copy that `update.sh` fast-forwards, so do not edit it. Work in a copy: `mkdir -p ~/.hermes/work/ui && cp -r ~/.hermes/reference/print-buddy-ui/. ~/.hermes/work/ui/`.
- `python3` (stdlib only) for `tools/build.py` and `scripts/check_ui.py`.
- No credentials. Release publishing needs a token held in GitHub secrets; never read or print it.

## How to Run
Invoke through the `terminal` tool, from the working copy:
```
python3 ~/.hermes/skills/software-development/print-buddy-ui-dev/scripts/check_ui.py ~/.hermes/work/ui
python3 tools/build.py dist
```
The checker is read-only. `tools/build.py` writes `dist/print-buddy-ui-basic.tar.gz` and `dist/print-buddy-ui-advanced.tar.gz`.

## Quick Reference
- Panel API and helpers: `skill_view(name="print-buddy-ui-dev", file_path="references/panel-api.md")`
- Panel file: `panels/<area>/<name>/<name>.js` and `<name>.css`. Areas: `print`, `control`, `machine`, `camera`.
- Page-wide features: `core/extras/<name>.js` (one file each, listed in `core/extras/README.txt`).
- Register in `index.html`: CSS `<link>` block around lines 318-349; script block after `core/core.js` (line 1798) and before `core/builder.js` / `core/home.js`.
- Panel-type list and tier data: `tiers.json`.
- Check wiring: `python3 scripts/check_ui.py <ui-dir>`
- Build: `python3 tools/build.py [outdir]` (default `dist`)
- Release workflow: `.github/workflows/release.yml`

## Procedure
1. Make a working copy (see Prerequisites). Do not edit `~/.hermes/reference/`.
2. Pick the area folder. `panels/machine/` holds host, config and console panels. `panels/control/` holds move, heat and tune panels. Each folder has a `README.txt` listing its contents; update it when you add a panel.
3. Create `panels/<area>/<name>/<name>.js` containing one `PB.panel("<name>", { ... })` call. Fields and lifecycle are in `references/panel-api.md`. Copy the shape of a small existing panel such as `panels/control/fans/fans.js`, not the largest one.
4. Create `panels/<area>/<name>/<name>.css`. Namespace classes (`pb-...`) so panels do not collide.
5. Register both files in `index.html`:
   - add `<link rel="stylesheet" href="/static/panels/<area>/<name>/<name>.css">` to the CSS block;
   - add `<script src="/static/panels/<area>/<name>/<name>.js"></script>` to the panel script block, which sits between `core/core.js` and `core/home-panels.js`.
6. Run `scripts/check_ui.py` on the copy. It must report `0 problem(s)`. Fix every PROBLEM line before going on.
7. Build and list the tarball. The tarball is the only artifact that reaches users, so check what is in it:
   ```
   python3 tools/build.py dist
   tar -tzf dist/print-buddy-ui-basic.tar.gz | grep -E 'TIER|panels/<area>/<name>/'
   ```
8. Release happens in GitHub Actions, not locally. Use `release.yml` as the reference for what it does (see Pitfalls).

## Pitfalls
- **An unregistered file fails silently.** A panel JS or CSS file that is not in `index.html` is never loaded, and nothing errors. `check_ui.py` catches this.
- **Tier gating is runtime, not packaging.** `tiers.json` lists the same files for `basic` and `advanced`. The basic UI hides panels with `cls: "adv"` through `body.ui-basic .adv { display: none !important; }` (index.html:118). A panel marked `adv` still ships in the basic tarball.
- **`core/core.js` monkey-patches page globals.** It wraps `renderPage`, `render`, `route` and `conAdd`, and swaps the `hashchange` listener. Panel code must not reassign those; use `PB.onRoute` and the lifecycle hooks instead. Script order matters for this reason.
- **Most main-page logic is inline.** `index.html` holds about 1,100 lines of inline JavaScript (roughly lines 658-1795). Changes there are not in any panel file. Search `index.html` before assuming a function lives in a `.js` file.
- **`share.html` is standalone.** It has its own inline script and does not load `core/core.js`. Do not use `PB.*` there.
- **Escape server data.** Interpolate printer and file names through `esc()`. Some existing templates skip it: `panels/machine/machine/machine.js` builds `kv.innerHTML` from labels and computed numbers, so it is safe only by accident. Check the source before copying a pattern.
- **`PB.rpc` only works for allowlisted Moonraker methods.** The core app's `RPC_ALLOW` table (`app/main.py`, around line 998 in the core repo) decides what passes. A method missing from that table returns an error to the UI. The same table includes `machine.reboot`, `machine.shutdown` and `printer.firmware_restart`. The `/rpc` route accepts a JSON body without checking Content-Type or Origin, so a cross-site page can reach it. Do not add more power methods to the allowlist without a confirm step. This risk is in the core app, not the UI.
- **`PB.kv.get` puts the key into the URL unencoded** (`core/core.js`, `kv` object). Safe only while keys are constants. Do not pass user input as a key.
- **`release.yml` reads `needs.txt`, which is not in this repo.** The `needs:` line in release notes is therefore never written. This is a known gap, not a build failure.
- **Release targets the core repo.** The workflow publishes to `MAIN_REPO` (`sterling5241/printer-buddy`) under release names `ui-nightly` and `ui-vX`, not to this repo's own releases.
- **Nightly is skipped when nothing changed.** The workflow compares `$GITHUB_SHA` with the body of the existing `ui-nightly` release. An unchanged commit publishes nothing.
- **The UI is not tracked in core git.** Core `.gitignore` excludes `ui/`; UI changes belong in this repo.

## Verification
Run both commands on the working copy. A clean run is `0 problem(s)`, and the tarball lists your new files:
```
python3 ~/.hermes/skills/software-development/print-buddy-ui-dev/scripts/check_ui.py ~/.hermes/work/ui && (cd ~/.hermes/work/ui && python3 tools/build.py dist >/dev/null && tar -tzf dist/print-buddy-ui-basic.tar.gz | grep -c panels/)
```
The build was checked on a clean export of `HEAD` (1368e19): 154 entries in each tarball, and both `TIER` files read `basic` and `advanced`.
