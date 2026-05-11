"""Mission control parser for the Level 3 AI toy demo."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

from config import load_local_env


load_local_env()


KNOWN_OBJECTS = [
    "person",
    "cup",
    "bottle",
    "chair",
    "book",
    "laptop",
    "phone",
    "keyboard",
    "mouse",
    "backpack",
    "bus",
    "dog",
    "cat",
    "car",
]


@dataclass
class MissionPlan:
    raw_instruction: str
    intent: str
    target: str
    source_image: str | None
    confidence: float
    mode: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_instruction(instruction: str, source_image: str | None = None) -> MissionPlan:
    """Parse a natural language instruction into a simple action plan."""
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("Instruction cannot be empty.")

    mode = os.getenv("MISSION_CONTROL_MODE", "rules").strip().lower()
    if mode in {"openai", "api", "llm"}:
        try:
            return _parse_with_openai(instruction, source_image)
        except Exception as exc:  # Keep the demo running even when API config is absent.
            fallback = _parse_with_rules(instruction, source_image)
            fallback.notes.append(f"API parser unavailable; used rule fallback: {exc}")
            return fallback

    return _parse_with_rules(instruction, source_image)


def _parse_with_rules(instruction: str, source_image: str | None) -> MissionPlan:
    text = instruction.lower()
    target = _find_target(text)

    if re.search(r"\b(count|how many|number of)\b", text):
        intent = "count_objects"
    elif re.search(r"\b(check|see|detect|find|look for|is there|whether)\b", text):
        intent = "detect_object"
    elif re.search(r"\b(describe|summarize|what is in)\b", text):
        intent = "describe_scene"
    else:
        intent = "detect_object" if target != "object" else "unknown"

    return MissionPlan(
        raw_instruction=instruction,
        intent=intent,
        target=target,
        source_image=source_image,
        confidence=0.72 if target != "object" else 0.45,
        mode="rule_based",
        notes=["Parsed locally with deterministic rules."],
    )


def _parse_with_openai(instruction: str, source_image: str | None) -> MissionPlan:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    if not model:
        raise RuntimeError("OPENAI_MODEL is not set")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = (
        "Convert the user instruction into JSON for a Raspberry Pi robot demo. "
        "Return only JSON with keys: intent, target, confidence, notes. "
        "intent must be one of detect_object, count_objects, describe_scene, unknown."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": instruction},
        ],
        temperature=0,
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)

    notes = data.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]

    return MissionPlan(
        raw_instruction=instruction,
        intent=str(data.get("intent", "unknown")),
        target=str(data.get("target", "object")).lower(),
        source_image=source_image,
        confidence=float(data.get("confidence", 0.75)),
        mode="openai_api",
        notes=notes or ["Parsed with API mission control."],
    )


def _find_target(text: str) -> str:
    for obj in KNOWN_OBJECTS:
        if re.search(rf"\b{re.escape(obj)}s?\b", text):
            return obj
    return "object"
