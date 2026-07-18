# ============================================================================
# Nambikkai local API guard (FOUNDATIONS add-now item 2).
#
# Binding 127.0.0.1 is NOT enough on its own. Two known attack classes reach a
# localhost-only API from an ordinary web page the user has open:
#
#   1. DNS rebinding — attacker.com re-resolves to 127.0.0.1, so the browser
#      sends same-origin requests to this server. Defence: the Host header will
#      still read attacker.com, so we reject any Host that isn't loopback.
#   2. CSRF / drive-by POST — any page can fire a cross-origin POST. Defence:
#      a per-session token in a CUSTOM header. Custom headers force a CORS
#      preflight, we run no CORS middleware, so the preflight fails and the
#      browser never sends the real request. The token also means a non-browser
#      local process can't blind-POST into the journal.
#
# The token is generated fresh per server start and written to data/.session-
# token (0600, gitignored). The browser never holds it: in dev, Vite's proxy
# reads the file and injects the header server-side. Packaging-era fix is
# single-origin serving (backend serves the built frontend), which removes the
# proxy hop entirely.
# ============================================================================
import os
import secrets

from fastapi import HTTPException, Request

TOKEN_HEADER = "x-nambikkai-token"
TOKEN_FILE = ".session-token"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}

_token: str = ""


def issue_token(data_dir: str) -> str:
    """Mint this run's token and drop it where the dev proxy can read it."""
    global _token
    _token = secrets.token_urlsafe(32)
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, TOKEN_FILE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(_token)
    os.chmod(path, 0o600)
    return _token


def current_token() -> str:
    return _token


def guard(request: Request) -> None:
    """Reject anything that isn't this machine's app talking to itself."""
    host = (request.headers.get("host") or "").split(":")[0]
    if host not in LOOPBACK_HOSTS:
        raise HTTPException(403, "This app only answers on your own computer.")

    sent = request.headers.get(TOKEN_HEADER, "")
    if not _token or not secrets.compare_digest(sent, _token):
        raise HTTPException(401, "This request didn't come from your journal app.")
