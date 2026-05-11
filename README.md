# Level 3 AI Take-Home Prototype

## Overview

This repository contains a lightweight end-to-end prototype for the Level 3 AI take-home assignment. The prototype demonstrates how a natural language instruction can be sent through an Open Claw-style interface, delivered to a Raspberry Pi-style service, interpreted into an actionable mission, executed with a vision model, and returned as a structured task result.

The implemented flow is:

```text
User natural language instruction
  -> Open Claw API/message adapter
  -> Raspberry Pi task service
  -> mission control parser
  -> YOLO vision model
  -> structured status response
```

The prototype is intentionally scoped as a local toy demo. It preserves the integration contract and execution flow while avoiding setup overhead from physical hardware and the full Open Claw runtime.

## Architecture

| Component | Implementation | Role |
|---|---|---|
| Open Claw boundary | `openclaw_adapter.py` | Accepts a natural language instruction and sends it to the Raspberry Pi service over HTTP |
| Raspberry Pi service | `pi_service.py` | FastAPI service that receives tasks, invokes mission control, runs vision, and returns status |
| Mission control | `mission_control.py` | Converts natural language into structured actions such as `detect_object/person` |
| Vision model | `vision.py` | Runs YOLOv8n through Ultralytics when an image is provided |
| Demo notebook | `demo_notebook.ipynb` | Notebook wrapper for walkthroughs, screenshots, and quick validation |

## Prototype Assumptions

- A physical Raspberry Pi was not used for this weekend prototype. The Raspberry Pi side is represented by a local FastAPI service with the same kind of HTTP task endpoint that could later run on a real Raspberry Pi.
- The full Open Claw runtime was not installed locally. Instead, `openclaw_adapter.py` represents the Open Claw API/message boundary by accepting a user instruction and sending it to the Raspberry Pi service.
- The vision model path is real. YOLOv8n was run locally on sample images, and the output returned `vision_result.mode: yolo`.
- Mission control currently uses a deterministic rule-based parser for reliability and speed. The parser is isolated so it can be replaced with an API-based LLM or a lightweight local model.
- The goal of this submission is to demonstrate the end-to-end communication and execution loop, not to claim a completed physical robot deployment.

## Repository Contents

```text
openclaw_adapter.py      # Open Claw-style CLI/API adapter
pi_service.py            # Raspberry Pi-style FastAPI task service
mission_control.py       # Mission parser with rule-based and optional API modes
vision.py                # YOLO vision wrapper with simulated fallback
config.py                # Local .env loading helper
smoke_test.py            # In-process smoke test
demo_notebook.ipynb      # Notebook demo wrapper
REPORT_NOTES.md          # Evidence notes and report-ready wording
requirements.txt         # Core dependencies
requirements-vision.txt  # Optional YOLO dependencies
requirements-api.txt     # Optional OpenAI-compatible API dependency
.env.example             # Example runtime configuration
sample_images/           # Included sample images for YOLO validation
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

To run the YOLO vision path:

```powershell
python -m pip install -r requirements-vision.txt
```

To enable optional API-based mission control:

```powershell
python -m pip install -r requirements-api.txt
Copy-Item .env.example .env
```

Then set:

```text
MISSION_CONTROL_MODE=openai
OPENAI_API_KEY=<api key>
OPENAI_MODEL=<model name>
```

## Running The Demo

Start the Raspberry Pi-style service:

```powershell
uvicorn pi_service:app --reload --port 8000
```

In a second terminal, send instructions through the Open Claw-style adapter:

```powershell
python openclaw_adapter.py "Check whether there is a person in the image" --image sample_images\bus_people.jpg
python openclaw_adapter.py "Check whether there is a bus in the image" --image sample_images\bus_people.jpg
python openclaw_adapter.py "Check whether there is a dog in the image" --image sample_images\bus_people.jpg
```

The service returns a JSON response containing:

- `mission_plan`: the structured interpretation of the natural language instruction
- `vision_result`: detected objects, counts, confidence scores, and model mode
- `success` / `status`: whether the requested task was confirmed
- `outcome`: a readable task result

## Verified Results

The following cases were validated on May 10, 2026 using YOLOv8n:

| Instruction | Image | Result |
|---|---|---|
| Check whether there is a person | `bus_people.jpg` | YOLO detected 4 people; `success: true` |
| Check whether there is a bus | `bus_people.jpg` | YOLO detected 1 bus; `success: true` |
| Check whether there is a person | `zidane_people.jpg` | YOLO detected 2 people; `success: true` |
| Check whether there is a dog | `bus_people.jpg` | YOLO did not detect a dog; `success: false`, `status: not_confirmed` |

The negative dog case is included to show that the prototype is not hard-coded to return affirmative responses. It compares the requested target against YOLO detections and returns `not_confirmed` when the object is absent.

## Working Scope

Fully working in the local prototype:

- Natural language instruction input
- HTTP communication between the Open Claw-style adapter and Raspberry Pi-style service
- Mission parsing into structured task plans
- YOLOv8n object detection on included sample images
- Positive and negative task outcomes
- Structured JSON status responses

Partially complete by design:

- Open Claw is represented by an adapter rather than the full official runtime
- Raspberry Pi is simulated locally rather than deployed to physical hardware
- Mission control defaults to rule-based parsing, with a replacement path for an API LLM or local lightweight model

## Future Work

- Deploy `pi_service.py` to a physical Raspberry Pi running Raspberry Pi OS
- Connect a live camera stream as the image source
- Replace the adapter with the official Open Claw API, webhook, or skill interface
- Replace the rule-based mission parser with a lightweight on-device model
- Add persistent task logs and a simple operator UI

## Submission Notes

Local-only generated files are intentionally excluded by `.gitignore`, including:

```text
.venv/
__pycache__/
logs/
.env
yolov8n.pt
~$*.docx
```

`yolov8n.pt` is generated automatically by Ultralytics and does not need to be committed.
