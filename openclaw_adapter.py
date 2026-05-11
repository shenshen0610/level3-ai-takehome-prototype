"""Lightweight Open Claw adapter for the Level 3 AI toy demo."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from typing import Any

import requests

from config import load_local_env


load_local_env()


DEFAULT_PI_SERVICE_URL = "http://127.0.0.1:8000"


def send_instruction(
    instruction: str,
    source_image: str | None = None,
    service_url: str | None = None,
) -> dict[str, Any]:
    """Send an Open Claw-style instruction to the Raspberry Pi service."""
    base_url = (service_url or os.getenv("PI_SERVICE_URL") or DEFAULT_PI_SERVICE_URL).rstrip("/")
    payload = {
        "instruction": instruction,
        "source_image": source_image,
        "correlation_id": str(uuid.uuid4()),
    }
    response = requests.post(f"{base_url}/task", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a natural language instruction through the toy Open Claw adapter."
    )
    parser.add_argument("instruction", help="Natural language instruction from the user.")
    parser.add_argument("--image", dest="source_image", help="Optional image path for the vision task.")
    parser.add_argument(
        "--url",
        dest="service_url",
        default=None,
        help="Raspberry Pi service URL. Defaults to PI_SERVICE_URL or localhost:8000.",
    )
    args = parser.parse_args()

    result = send_instruction(args.instruction, args.source_image, args.service_url)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
