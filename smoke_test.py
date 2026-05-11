"""In-process smoke test for the local demo framework."""

from __future__ import annotations

import json

from mission_control import parse_instruction
from vision import run_vision_task


def main() -> None:
    instruction = "Check whether there is a person in the image"
    plan = parse_instruction(instruction)
    vision = run_vision_task(plan.target, plan.source_image)
    result = {
        "success": vision.found_target,
        "mission_plan": plan.to_dict(),
        "vision_result": vision.to_dict(),
        "outcome": f"Affirmative: completed {plan.intent} for {plan.target}.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
