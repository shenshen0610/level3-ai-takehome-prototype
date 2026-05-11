"""Small configuration helpers for the toy demo."""

from __future__ import annotations

from pathlib import Path


def load_local_env() -> None:
    """Load .env when python-dotenv is installed; otherwise keep environment as-is."""
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    load_dotenv(Path(__file__).with_name(".env"))
