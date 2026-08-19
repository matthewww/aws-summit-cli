# aws-summit-cli

**[Live: AWS Summit Johannesburg 2026 — Session Explorer](https://matthewww.github.io/aws-summit-cli/)**

Interactive CLI to pick an AWS Summit and pull its agenda sessions as JSONL to coversationally browse with AI agents.

## Setup

```
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt   # Windows
./venv/bin/python -m pip install -r requirements.txt           # macOS/Linux
```

### Usage

```
./venv/Scripts/python.exe cli.py
```

Arrow-key select an event from the live list; sessions are written to
`data/<event-slug>/sessions.jsonl`. Loops back to the picker after each fetch.