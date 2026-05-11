# Report Notes

## Demo Evidence: YOLO Vision Path

Date: May 10, 2026

Command:

```powershell
python openclaw_adapter.py "Check whether there is a person in the image" --image sample_images\bus_people.jpg
```

Observed result:

- The Open Claw adapter sent a natural language instruction to the local Raspberry Pi mock service.
- Mission control parsed the request with the local rule-based parser.
- The target object was `person`.
- The vision module ran the real YOLO path, not the simulated fallback.
- YOLO model used: `yolov8n.pt`.
- Image used: `sample_images\bus_people.jpg`.
- The task completed successfully with `success: true`.

Detected objects:

| Label | Count | Max confidence |
|---|---:|---:|
| bus | 1 | 0.873 |
| person | 4 | 0.866 |
| stop sign | 1 | 0.255 |

Key output fields:

```json
{
  "success": true,
  "status": "completed",
  "mission_plan": {
    "intent": "detect_object",
    "target": "person",
    "mode": "rule_based"
  },
  "vision_result": {
    "mode": "yolo",
    "found_target": true,
    "notes": [
      "Ran YOLO model: yolov8n.pt"
    ]
  },
  "outcome": "Affirmative: completed detect_object for person."
}
```

Suggested report wording:

> I validated the end-to-end pipeline using a local FastAPI service that simulates the Raspberry Pi. The Open Claw adapter sent a natural language request asking whether a person was present in the image. Mission control parsed the request into a `detect_object` task targeting `person`, and the vision module ran YOLOv8n on a sample image. The system detected four people with maximum confidence 0.866 and returned an affirmative completion response.

## Architecture Assumption To Mention

For this prototype, Open Claw is represented by a lightweight adapter and the Raspberry Pi is represented by a local FastAPI service. This preserves the interface and execution flow while avoiding hardware setup overhead. The same service can be deployed to a physical Raspberry Pi later.

## Prototype Assumptions

The following assumptions should be included clearly in the final report:

1. Raspberry Pi is simulated locally.

   For the weekend prototype, I did not use a physical Raspberry Pi. Instead, I implemented the Raspberry Pi side as a local FastAPI service in `pi_service.py`. This service exposes the same kind of HTTP task endpoint that could later run on a real Raspberry Pi.

2. Open Claw is represented by a lightweight API adapter.

   I did not run the full Open Claw runtime locally. Instead, `openclaw_adapter.py` simulates the Open Claw message/API boundary by accepting a natural language user instruction and sending it to the Raspberry Pi service over HTTP. In a production version, this adapter could be replaced with the official Open Claw API, webhook, or skill interface.

3. Vision model is real.

   The vision component runs YOLOv8n through the `ultralytics` package when an image is provided and the dependency is installed. This was validated with `sample_images\bus_people.jpg` and `sample_images\zidane_people.jpg`, where `vision_result.mode` returned `yolo`.

4. Mission control currently uses a deterministic fallback.

   The mission control component currently uses a lightweight rule-based parser to convert natural language instructions into structured actions such as `detect_object/person` or `detect_object/bus`. This was chosen for reliability and speed in the toy prototype. The architecture keeps this component isolated so it can be replaced with an API-based LLM or a small local model on the Raspberry Pi.

5. The demo focuses on the end-to-end integration contract.

   The primary goal of this prototype is to demonstrate the full communication and execution loop: natural language instruction -> Open Claw adapter -> Raspberry Pi service -> mission plan -> vision model -> structured status response. The hardware deployment and full Open Claw integration are left as next steps.

Suggested report wording:

> For this prototype, I made a few practical assumptions to keep the scope focused on the end-to-end integration. I simulated the Raspberry Pi as a local FastAPI service and represented the Open Claw boundary with a lightweight API adapter. The adapter accepts a natural language instruction and sends it to the Raspberry Pi service over HTTP, preserving the same communication pattern that could later be used with a real Open Claw API, webhook, or skill interface. The vision model path is real: YOLOv8n runs on local sample images and returns object detections. Mission control currently uses a deterministic parser for reliability, with a clear replacement path for an API-based LLM or lightweight local model on a physical Raspberry Pi.

## Additional Demo Evidence

### Bus Detection

Command:

```powershell
python openclaw_adapter.py "Check whether there is a bus in the image" --image sample_images\bus_people.jpg
```

Observed result:

- `success: true`
- `status: completed`
- Mission intent: `detect_object`
- Mission target: `bus`
- Mission parser mode: `rule_based`
- Vision mode: `yolo`
- YOLO model used: `yolov8n.pt`
- Outcome: `Affirmative: completed detect_object for bus.`

Detected objects:

| Label | Count | Max confidence |
|---|---:|---:|
| bus | 1 | 0.873 |
| person | 4 | 0.866 |
| stop sign | 1 | 0.255 |

### Person Detection On Second Image

Command:

```powershell
python openclaw_adapter.py "Check whether there is a person in the image" --image sample_images\zidane_people.jpg
```

Observed result:

- `success: true`
- `status: completed`
- Mission intent: `detect_object`
- Mission target: `person`
- Mission parser mode: `rule_based`
- Vision mode: `yolo`
- YOLO model used: `yolov8n.pt`
- Outcome: `Affirmative: completed detect_object for person.`

Detected objects:

| Label | Count | Max confidence |
|---|---:|---:|
| person | 2 | 0.836 |
| tie | 1 | 0.291 |

### Negative Case: Dog Not Present

Command:

```powershell
python openclaw_adapter.py "Check whether there is a dog in the image" --image sample_images\bus_people.jpg
```

Observed result:

- `success: false`
- `status: not_confirmed`
- Mission intent: `detect_object`
- Mission target: `dog`
- Mission parser mode: `rule_based`
- Vision mode: `yolo`
- `found_target: false`
- YOLO model used: `yolov8n.pt`
- Outcome: `Unable to confirm dog from the current input.`

Detected objects:

| Label | Count | Max confidence |
|---|---:|---:|
| bus | 1 | 0.873 |
| person | 4 | 0.866 |
| stop sign | 1 | 0.255 |

Why this matters:

> This negative case demonstrates that the system is not hard-coded to return affirmative responses. It checks the YOLO detections against the mission target and returns `not_confirmed` when the requested object is absent.
