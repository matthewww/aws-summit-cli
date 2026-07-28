# aws-summit-cli

**[Live: AWS Summit Johannesburg 2026 — Session Explorer](https://matthewww.github.io/aws-summit-cli/)**

Interactive CLI to pick an AWS Summit and pull its agenda sessions as JSONL to coversationally browse with AI agents.

## Setup

```
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt   # Windows
./venv/bin/python -m pip install -r requirements.txt           # macOS/Linux
```

## Usage

```
./venv/Scripts/python.exe cli.py
```

Arrow-key select an event from the live list; sessions are written to
`data/<event-slug>/sessions.jsonl`. Loops back to the picker after each fetch.

## How it works

- `events.py` — pages AWS's summit-listing API
  (`events-cards-interactive-summits-cards-interactive-events-summits-hub`)
  to build the picker list.
- `aws_agenda.py` — for the chosen event, scrapes its agenda page for the
  event-specific `directoryId` AWS embeds in the HTML (there's no shared/stable
  agenda directory across events), then pages `/api/dirs/items/search` against
  it.

Some events render their agenda widget fully client-side with nothing
embedded server-side to scrape — those are reported as "undiscoverable"
rather than silently treated as having no sessions.
