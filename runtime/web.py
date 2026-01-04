"""Web helpers for Jusu++

Provides a lightweight `http` module with:
- get(url, timeout=5) -> {'status': int, 'text': str}
- async_get(url, timeout=5) -> coroutine returning same dict (requires aiohttp)

Falls back to stdlib urllib if `requests` or `aiohttp` are missing.
"""
from __future__ import annotations

try:
    import aiohttp as _aiohttp
    HAS_AIOHTTP = True
except Exception:
    _aiohttp = None
    HAS_AIOHTTP = False

try:
    import requests as _requests
    HAS_REQUESTS = True
except Exception:
    _requests = None
    HAS_REQUESTS = False

import urllib.request as _urllib

class WebModule:
    def get(self, url: str, timeout: float = 5.0):
        """Synchronous GET helper returning a dict with 'status' and 'text'."""
        if HAS_REQUESTS:
            r = _requests.get(url, timeout=timeout)
            return {'status': r.status_code, 'text': r.text}
        # Fallback to urllib
        with _urllib.urlopen(url, timeout=timeout) as resp:
            b = resp.read()
            try:
                text = b.decode('utf-8')
            except Exception:
                text = b.decode('latin1')
            return {'status': resp.getcode(), 'text': text}

    async def async_get(self, url: str, timeout: float = 5.0):
        """Asynchronous GET helper (requires aiohttp)."""
        if not HAS_AIOHTTP:
            raise RuntimeError('aiohttp is not installed; async_get unavailable')
        async with _aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=timeout) as resp:
                text = await resp.text()
                return {'status': resp.status, 'text': text}

    def __repr__(self):
        parts = [f"aiohttp={'yes' if HAS_AIOHTTP else 'no'}", f"requests={'yes' if HAS_REQUESTS else 'no'}"]
        return f"<WebModule {' '.join(parts)}>"
