# Probing HTTP API handlers during a security review

Use this when a lens is Security and the target exposes HTTP routes (Starlette, FastAPI, Flask, Express, etc.).

## Checklist (read first, then probe)

1. **Which routes take mutating POSTs or PUTs?** List them. For each, note the methods allowed and what the body can trigger (power, firmware, file writes, gcode).
2. **How is the body parsed?** Find the helper that reads JSON. If it calls the framework's JSON reader without checking `Content-Type`, a cross-site form or `fetch(..., {mode:'no-cors'})` with `text/plain` reaches the handler without preflight.
3. **Is there an Origin or Host check, or a CSRF token?** Grep for `origin`, `referer`, `csrf`, `TrustedHost`, `CORSMiddleware`. Absence is a finding only if the route is reachable from a browser on the same network.
4. **Is there a reverse-proxy or tunnel path filter?** Check the ingress config (e.g. a `^/share/` path rule). A filter at the edge protects only the routes it names; read the proxy rule and the in-app middleware separately.
5. **Allowlists:** check that every method in the allowlist is safe to expose from the path it is reachable on. Power, firmware, reboot, and update methods need a separate gate.

## Probe recipe (copy the real function, do not retype it)

Extract the handler helper from the source at review time, mount it in a minimal app, and send the request that the browser would send:

```python
import json
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

src = open("<extracted_module>.py").read()
exec(src[src.index("async def body("):src.index("def _pid(")])   # the real helper

async def rpc(request: Request):
    b = await body(request)
    return JSONResponse({"method_seen": b.get("method")})

app = Starlette(routes=[Route("/api/x/rpc", rpc, methods=["POST"])])
r = TestClient(app).post("/api/x/rpc", content=json.dumps({"method": "<dangerous_method>"}),
                         headers={"content-type": "text/plain", "origin": "https://evil.example"})
print(r.status_code, r.text)
```

A 200 with the dangerous method echoed back is a reproduced finding. Quote the output in the finding.

Adapt the slice markers to the real helper names. Do not send the probe to a live device or host: run it against the TestClient only.

## Fix shapes to recommend

- Require `application/json` in the body helper and return 415 otherwise. This blocks simple cross-site POSTs without breaking the app's own `fetch` calls, which set the header.
- Reject requests whose `Origin` is present and not the app's own origin.
- Put confirmation tokens or a separate endpoint on destructive methods (reboot, shutdown, firmware restart, file overwrite of config).
- Keep the allowlist narrow by path: the edge tunnel should reach only the read-only share routes.
