"""
Lazy Supabase client.

Returns None if SUPABASE_URL / SUPABASE_KEY aren't set, so the rest of the app
can treat "no Supabase configured" as a normal, expected state rather than a
crash.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

_client = None
_attempted = False


def get_supabase_client():
    global _client, _attempted

    if _attempted:
        return _client

    _attempted = True

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        return None

    try:
        from supabase import create_client
        _client = create_client(url, key)
    except Exception:
        _client = None

    return _client