# Printer Buddy UI: panel API reference

Source: `core/core.js` (the `PB` object), `core/home-panels.js`, `core/builder.js`, and `index.html` (inline page script). Line numbers refer to the `print-buddy-ui` `main` checkout at 1368e19.

## Registering a panel

`PB.panel(type, def)` adds a panel to the printer page. `PB.homePanel(type, def)` adds one to the home dashboard. Both fill in defaults: `title`, `icon`, `cls`, `single: false`.

| Field | Meaning |
|---|---|
| `title` | Heading shown on the panel and in the Edit layout picker. |
| `desc` | One-line description shown in the picker. |
| `icon` | Inline SVG from `PB.icon('<path ...>')`, or `""`. |
| `cls` | Extra card class. `"adv"` hides the panel in the basic UI. |
| `single` | `true` allows only one copy of the panel in the layout. |
| `gear` | `true` keeps the ⚙ settings button visible outside Edit layout. |
| `flush` | Removes card padding (used by full-bleed panels). |
| `settings` | Array of setting descriptors (below). Shown under the ⚙ button. |
| `edit(cfg, save)` | Alternative to `settings`: the ⚙ button opens the panel's own setup box and calls `save(newCfg)`. |
| `create(host, cfg)` | Required. Builds the panel body inside `host` and returns the lifecycle object. `cfg` already has defaults filled in. |

### Settings descriptors
`settings: [{ k, label, type, options, def }]`
- `type: "check"` renders a checkbox. The value is a boolean.
- `type: "select"` renders a dropdown. `options` is `[[value, label], ...]`. The dialog keeps numeric values as numbers.
- `k` is the key in `cfg`. `def` is the default.

## Lifecycle returned from `create`
All methods are optional.
- `open(id)`: a printer page was opened. Reset per-printer state here.
- `update(p)`: new data for the open printer. Called several times a second. On the home page the argument is the full printer list.
- `shown()`: the panel's tab just became visible. Reload lists and resize charts here.
- `log(kind, text)`: a console line arrived for the open printer.
- `destroy()`: the panel was removed from the layout.

Panel code runs inside `try/catch`. An exception in one panel is logged and does not stop the others.

## Helpers on `PB`
- `PB.icon(paths)`, `PB.ic` (named icons such as `x`, `cog`, `download`, `refresh`, `pencil`, `eye`, `grip`, `more`).
- `PB.el(tag, cls, html)`: create an element.
- `PB.store.get(key, default)` / `PB.store.set(key, value)`: JSON in `localStorage`.
- `PB.current()`: the open printer object, or `null`.
- `PB.rpc(method, params)`: POST `/api/printers/<pid>/rpc`. Only methods in the core `RPC_ALLOW` table work.
- `PB.kv.get(key)` / `PB.kv.set(key, value)`: per-printer key/value store at `/api/printers/<pid>/kv`.
- `PB.gcode(script)`: send G-code to the open printer.
- `PB.confirmGcode(text, script, doneMessage)`: `confirm()` first, then send G-code.
- `PB.printFile`, `PB.thumbUrl(pid, file)`, `PB.fileUrl(root, path, download)`: file helpers. Roots include `gcodes`, `config` and `logs`.
- `PB.settings(def, cfg, save)`: open the settings dialog for a definition.
- `PB.take(selector)` / `PB.park(node)`: move a server-rendered node out of or back into the hidden parking element.
- `PB.reveal(host)`: dispatches `pb-reveal` on `host`.
- `PB.onRoute(fn)`: call `fn(printer)` on each route change.
- `PB.mount`, `PB.unmount`, `PB.shown`: used by the layout builder. Panel code rarely needs them.

## Page globals from the inline script in `index.html`
- `api(path, opts)` (index.html:696): fetch JSON. Throws `Error` with the server's `error` text, or `HTTP <status>`. A 204 returns `null`.
- `esc(s)` (index.html:661): HTML-escape. Use it on every server string you put in `innerHTML`.
- `toast(msg)` (index.html:663).
- `gcode(script)` (index.html:1350): the page-level G-code sender that `PB.gcode` wraps.
- Formatters: `fmtTemp`, `fmtDur`, `fmtDate`, `fmtSize`, `fmtClock`, `fmtFil`.

## Example: the shape of a small panel
A minimal panel has one `PB.panel` call. `create` writes markup into `host`, keeps references to its nodes, and returns `update` (and `open` if it keeps per-printer state). `panels/control/fans/fans.js` follows this shape: `settings` declares a check box, `create` builds the body, and `update(p)` reads `p.sensors` and `p.outputs`.

## Overrides done by `core/core.js`
`core.js` wraps `renderPage`, `render`, `route` and `conAdd` to fan out events to mounted panels, and sets `showTab` to a no-op. It also removes the original `hashchange` listener and adds its own. Do not wrap these again from a panel file.
