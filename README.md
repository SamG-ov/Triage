# Triage — auto-classify & route customer-support tickets

> **Status: work in progress.** Built phase-by-phase as a learning + portfolio project.

Triage reads an incoming customer-support ticket and produces:

- **urgency** — low / medium / high / urgent
- **category** — billing / technical / account / shipping / ...
- **suggested team** — which queue the ticket should route to
- **draft first-response** — a polite opening reply an agent can edit and send

The point of the project is not just to call an LLM, but to **measure** how well
it does against real ground-truth labels and to **prove** that prompt changes
improve accuracy.

## Architecture (data flow)

```
   Raw ticket  ──►  1. CLASSIFY  ──►  urgency / category / team   (one LLM call,
   (free text)         (structured output, validated)             constrained to a schema)
                          │
                          ▼
                    2. DRAFT REPLY  ──►  draft first-response      (second LLM call)
                          │
                          ▼
                    3. EVAL HARNESS ──►  accuracy, confusion       (runs offline on a
                       (offline)         matrix, cost & latency     labeled sample)
```

Box 3 is the heart of the project: it compares the system's output to
pre-existing ground-truth labels and reports whether changes made it better.

## Tech stack

- **Python 3.12**
- **anthropic** — Claude SDK (the LLM provider)
- **pydantic** — define & validate the structured output schema
- **pandas** — data loading, sampling, class-balance checks
- **datasets** — dataset access (Hugging Face)
- **typer** — command-line interface
- **python-dotenv** — load the API key from `.env`
- **pytest** — guardrail tests for the eval harness

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate         # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
copy .env.example .env              # then edit .env and paste your key
```

## Usage

_Coming in a later phase (CLI)._

## Results

_Before/after evaluation table — coming in Phase 6–7._

## Limitations

_Honest accounting of what the system does and doesn't do — coming in Phase 8._
