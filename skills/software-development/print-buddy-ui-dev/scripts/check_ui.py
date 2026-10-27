#!/usr/bin/env python3
"""Check a print-buddy-ui checkout for wiring mistakes that fail silently.

Usage:  python3 check_ui.py <path-to-print-buddy-ui>      (stdlib only, read-only)

Exit 0 = clean, 1 = problems found. Checks:
  1. every panels/**.js and core/**.js is loaded by a <script> in index.html
  2. every panels/**.css, core/**.css and styles/*.css is linked in index.html
  3. core/core.js loads before every panel script
  4. tiers.json: notes when basic and advanced file lists are identical
  5. every PB.panel("type") name is unique
"""
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
index = (root / "index.html").read_text(encoding="utf-8")
problems, notes = [], []

scripts = re.findall(r'<script src="/static/([^"]+)"', index)
links = re.findall(r'<link rel="stylesheet" href="/static/([^"]+)"', index)


def files(dirs, suffix):
    out = []
    for d in dirs:
        out += [p.relative_to(root).as_posix() for p in (root / d).rglob(f"*{suffix}")]
    return sorted(out)


for f in files(["panels", "core"], ".js"):
    if f not in scripts:
        problems.append(f"not loaded by index.html (silently dead): {f}")
for f in files(["panels", "core", "styles"], ".css"):
    if f not in links:
        problems.append(f"CSS not linked in index.html: {f}")

pos = {s: i for i, s in enumerate(scripts)}
panel_scripts = [s for s in scripts if s.startswith("panels/")]
if "core/core.js" not in pos:
    problems.append("core/core.js is not loaded by index.html")
else:
    for s in panel_scripts:
        if pos[s] < pos["core/core.js"]:
            problems.append(f"panel loads before core/core.js: {s}")

types = {}
for f in files(["panels"], ".js"):
    for t in re.findall(r'PB\.panel\("([^"]+)"', (root / f).read_text(encoding="utf-8")):
        if t in types:
            problems.append(f'duplicate panel type "{t}": {types[t]} and {f}')
        types[t] = f

tiers_path = root / "tiers.json"
if tiers_path.exists():
    tiers = json.loads(tiers_path.read_text(encoding="utf-8"))
    lists = {k: json.dumps(v.get("files"), sort_keys=True) for k, v in tiers.items()}
    if len(set(lists.values())) == 1:
        notes.append("tiers.json: all tiers share one file list; basic/advanced differ only at runtime (body.ui-basic .adv)")

for n in notes:
    print("NOTE:", n)
for p in problems:
    print("PROBLEM:", p)
print(f"checked {len(scripts)} scripts, {len(links)} stylesheets, {len(types)} panel types: "
      f"{len(problems)} problem(s), {len(notes)} note(s)")
sys.exit(1 if problems else 0)
