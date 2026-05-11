"""FastAPI service that represents the Raspberry Pi side of the demo."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mission_control import parse_instruction
from vision import run_vision_task


app = FastAPI(title="Level 3 AI Raspberry Pi Toy Service", version="0.1.0")


class TaskRequest(BaseModel):
    instruction: str = Field(..., min_length=1)
    source_image: str | None = None
    correlation_id: str | None = None


class TaskResponse(BaseModel):
    success: bool
    status: str
    correlation_id: str | None
    mission_plan: dict[str, Any]
    vision_result: dict[str, Any]
    outcome: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/task", response_model=TaskResponse)
def handle_task(request: TaskRequest) -> TaskResponse:
    try:
        plan = parse_instruction(request.instruction, request.source_image)
        vision = run_vision_task(plan.target, plan.source_image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    success = _is_success(plan.intent, vision.found_target)
    target = plan.target if plan.target != "object" else "requested object"
    if success:
        outcome = f"Affirmative: completed {plan.intent} for {target}."
        status = "completed"
    else:
        outcome = f"Unable to confirm {target} from the current input."
        status = "not_confirmed"

    return TaskResponse(
        success=success,
        status=status,
        correlation_id=request.correlation_id,
        mission_plan=plan.to_dict(),
        vision_result=vision.to_dict(),
        outcome=outcome,
    )


def _is_success(intent: str, found_target: bool) -> bool:
    if intent in {"detect_object", "count_objects"}:
        return found_target
    if intent == "describe_scene":
        return True
    return found_target


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("pi_service:app", host="127.0.0.1", port=8000, reload=True)
