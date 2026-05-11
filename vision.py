"""Vision model wrapper for the Level 3 AI toy demo."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from config import load_local_env


load_local_env()


@dataclass
class VisionResult:
    mode: str
    image: str | None
    objects: list[dict[str, Any]]
    found_target: bool
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_vision_task(target: str, image_path: str | None = None) -> VisionResult:
    """Run a small vision model when available, otherwise return a demo-safe simulation."""
    vision_mode = os.getenv("VISION_MODE", "auto").strip().lower()
    if vision_mode == "mock":
        return _simulate_vision(target, image_path, "VISION_MODE=mock", found_target=True)

    if not image_path:
        return _simulate_vision(target, image_path, "No source image provided.", found_target=True)

    image = Path(image_path)
    if not image.exists():
        return _simulate_vision(target, image_path, f"Image not found: {image_path}", found_target=False)

    try:
        return _run_yolo(target, image)
    except Exception as exc:
        return _simulate_vision(
            target,
            image_path,
            f"YOLO unavailable; target not confirmed: {exc}",
            found_target=False,
        )


def _run_yolo(target: str, image: Path) -> VisionResult:
    config_dir = Path(".ultralytics").resolve()
    config_dir.mkdir(exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))

    from ultralytics import YOLO

    model_name = os.getenv("YOLO_MODEL", "yolov8n.pt")
    model = YOLO(model_name)
    results = model(str(image), verbose=False)

    detections: list[dict[str, Any]] = []
    for result in results:
        names = result.names
        for box in result.boxes:
            label = str(names[int(box.cls[0])]).lower()
            confidence = float(box.conf[0])
            detections.append({"label": label, "confidence": round(confidence, 3)})

    counts = Counter(item["label"] for item in detections)
    objects = [
        {
            "label": label,
            "count": count,
            "max_confidence": max(
                item["confidence"] for item in detections if item["label"] == label
            ),
        }
        for label, count in sorted(counts.items())
    ]
    found = target in counts if target and target != "object" else bool(objects)

    return VisionResult(
        mode="yolo",
        image=str(image),
        objects=objects,
        found_target=found,
        notes=[f"Ran YOLO model: {model_name}"],
    )


def _simulate_vision(
    target: str,
    image_path: str | None,
    reason: str,
    found_target: bool,
) -> VisionResult:
    label = target if target and target != "object" else "person"
    objects = [{"label": label, "count": 1, "max_confidence": 0.99}] if found_target else []
    return VisionResult(
        mode="simulated_vision",
        image=image_path,
        objects=objects,
        found_target=found_target,
        notes=[
            reason,
            "Simulated output is used only as a fallback when model execution is unavailable.",
        ],
    )
