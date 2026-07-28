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

## Appendix: based on my interests, these are my current picks

Same lens as last year's [2025 picks](https://github.com/matthewww/aws-summit-sessions-jnb-2025)
— architecture, ML/GenAI depth over intro-level, customer-led case studies,
"at scale" over theory — applied to the 2026 Johannesburg agenda.

**GenAI / ML depth**
- *Building Multi-Tenant RAG and MCP Servers* (ARC301, Chalk talk, 13:30) —
  architecture-heavy, audience-driven Q&A on production RAG/MCP infrastructure
  rather than a service tour.
- *A practitioner's guide to data for agentic AI* (ANT303, Chalk talk, 13:30) —
  the data layer underneath agentic AI, the unglamorous part that actually
  determines whether it works.
- *SageMaker & MLflow: Innovate faster with no infrastructure management*
  (AIM308, Breakout session, 12:30) — practical MLOps, not a feature list.

**Architecture & scale**
- *Migrating 600K RPS: How Booking.com modernized accommodation search*
  (MAM302, Breakout session, 13:30) — a genuine "at scale" migration story,
  in the spirit of 2025's Fleet Tracking pick.
- *Build a well-architected foundation for scaling GenAI and agentic apps*
  (ARC304, Breakout session, 13:30) — architecture patterns for agentic
  systems specifically, not bolted onto a generic Bedrock talk.
- *Navigating the future: Solutions architecture in the age of AI* (ARC302,
  Breakout session, 11:30, with Standard Bank) — senior-architect framing,
  customer-led.

**Customer-led (real-world, no marketing filter)**
- *How Standard Bank built an AI-ready data foundation across Africa*
  (ANT302, Breakout session, 12:30)
- *Governance that Enables Innovation at Scale* feat. Old Mutual (COP301,
  Breakout session, 15:30)
- *How Peach Payments built a scalable payments engine on AWS* (CMP304,
  Breakout session, 15:30)

**Hidden gem**
- *Securing Agentic AI: OWASP, MAESTRO, and Real-World Defense Strategies*
  (SEC301, Chalk talk, 14:30) — 2025's hidden gem asked what happens when an
  AI is the user of your system; this is the security answer nobody's agenda
  has caught up to yet.

If short on time: prioritize the customer-led sessions and anything with
"at scale" or "well-architected" in the title.
