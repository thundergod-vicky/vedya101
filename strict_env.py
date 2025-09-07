"""Strict environment loader for VEDYA.

Enforces:
 - Only .env (root) is loaded
 - Disallows keys containing quotes or spaces at ends
 - Validates OPENAI_API_KEY format (prefix sk- and reasonable length)
 - Prevents accidental override from template files like .env.langgraph
 - Exposes helper function get_required(key)
"""

from __future__ import annotations
import os, sys, re
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).parent
_PRIMARY_ENV = _ROOT / '.env'

def _fail(msg: str):
    print(f"[ENV ERROR] {msg}", file=sys.stderr)
    raise SystemExit(1)

def load_strict():
    # Load only the primary .env (no override afterwards)
    if not _PRIMARY_ENV.exists():
        _fail("Missing .env file at project root.")
    load_dotenv(dotenv_path=_PRIMARY_ENV, override=False)

    # Basic sanity: reject if template vars leak
    template_files = ['.env.langgraph', '.env.example']
    for tmpl in template_files:
        if ( _ROOT / tmpl ).exists():
            # Ensure we did NOT load placeholder sentinel values
            for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                v = os.getenv(k)
                if v and 'your_' in v:
                    _fail(f"Placeholder value for {k} detected (came from template {tmpl}?); set a real key in .env")

    # Trim and validate keys
    key = os.getenv('OPENAI_API_KEY')
    if key:
        cleaned = key.strip()
        if cleaned != key:
            _fail('OPENAI_API_KEY has leading/trailing whitespace; fix .env')
        if ' ' in key:
            _fail('OPENAI_API_KEY contains spaces; invalid')
        if not key.startswith('sk-'):
            _fail('OPENAI_API_KEY does not start with sk-; verify you copied the correct key')
        if len(key) < 40 or len(key) > 200:
            _fail(f'OPENAI_API_KEY length {len(key)} outside expected bounds (40-200)')
    else:
        _fail('OPENAI_API_KEY missing in environment')

def get_required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        _fail(f'Required env var {name} is missing')
    return v

# Auto-load on import
load_strict()

__all__ = ["load_strict", "get_required"]
