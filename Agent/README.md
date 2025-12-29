## DAG Diagram

Run `python generate_dag.py` to generate `dag.png` (requires graphviz).
## Sample Run

Run the sample script to produce a deterministic log:

```powershell
python scripts/sample_run.py
```

A log file `debate_log_<timestamp>.jsonl` will be written in the project root. An example sample log is included at `logs/debate_log_sample.jsonl`.
# LangGraph-style Debate Workflow ✅

A lightweight, modular Python implementation of a LangGraph-style debate workflow. The system simulates a staged debate between two persona-driven agents (default: **Scientist** vs **Philosopher**), enforces strict turn ordering, prevents repeated arguments, maintains structured memory, and concludes with a Judge node that summarizes and declares a winner. All events, node inputs/outputs, and state transitions are appended to a **JSON-lines** log file for auditing and replay.

---

## Features ✨

- Exactly **8 rounds** total (4 turns per agent), strictly alternating (AgentA → AgentB → ...).
- **Turn control** enforced programmatically by the RoundsController (rejects out-of-order calls).
- **No repetition**: string/semantic similarity checks to prevent repeated arguments.
- **MemoryNode** maintains a structured transcript and short summary and supplies only agent-relevant slices per turn.
- **JudgeNode** aggregates the debate, validates coherence at a basic level, and produces a summary + winner with justification.
- **LoggerNode** writes every event/state transition to a persistent JSON-lines log with ISO-8601 UTC timestamps.
- **Determinism**: optional `--seed` flag for reproducible runs.
- Minimal CLI interface and programmatic sample runner for testing / demos.

---

## Quickstart — Install & Run (Windows PowerShell) ⚙️

1. Clone or extract the repository into a folder and open a PowerShell terminal in the project root (where `run_debate.py` is located).
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run a debate (interactive):

```powershell
python run_debate.py
# or non-interactive:
python run_debate.py --topic "Should AI be regulated like medicine?" --seed 42 --log-path debate_log_run.jsonl
```

Output: The CLI will print round-by-round messages and the final Judge summary. A log file is appended at the path you specify (default: `debate_log_<timestamp>.jsonl`).

Example sample run helper:

```powershell
python scripts/sample_run.py
```

---

## CLI Flags & Behavior 🧭

- `--topic "<text>"` — Provide the debate topic. If omitted, you'll be prompted.
- `--seed <int>` — Set random seed to make agent outputs deterministic (useful for testing/demos).
- `--log-path <path>` — Path to JSONL log file. Default: `debate_log_<timestamp>.jsonl`.
- `--persona-config <path>` — (Planned) path to a persona config file to swap personas.

> Note: Topics are validated and sanitized (length and control characters). Invalid topics will be rejected.

---

## Project Structure & Node Roles 🔧

`/nodes`
- `user_input_node.py` — Prompts for and validates the topic.
- `coordinator.py` — `RoundCoordinator` enforces sequencing and tracks round numbers.
- `agent_node.py` — `AgentNode` implements persona-driven arguments; deterministic with `seed`. Contains duplicate detection heuristics.
- `memory_node.py` — `MemoryNode` stores structured turns (`{round, agent, text}`) and a short rolling summary; supplies only relevant memory slices to each agent.
- `judge_node.py` — Aggregates final memory, performs lightweight coherence checks, and produces the verdict + justification.
- `logger_node.py` — Appends JSON-lines (one event per line) with ISO-8601 UTC timestamps.

Other top-level files:
- `run_debate.py` — CLI entry point.
- `scripts/sample_run.py` — Programmatic deterministic run (useful for tests & reproductions).
- `generate_dag.py` — Generates a Graphviz diagram (falls back to a simple SVG if system Graphviz is unavailable).
- `persona_templates/` — Persona prompts (e.g., `scientist.txt`, `philosopher.txt`) for easy swapping.
- `tests/` — Pytest tests (turn enforcement, duplicate detection, memory updates, judge output).

---

## Logging Format 📄

All events are appended to the configured log file as **JSON-lines** (one JSON object per line). Each event contains at least:

- `ts` — timestamp (ISO-8601 UTC)
- `event` — event name (e.g., `agent_turn`, `memory_updated`, `judge_verdict`)
- other fields relevant to the event (agent, text, round, memory snapshot, verdict, etc.)

Example line:

```json
{"ts":"2025-12-29T15:33:38.529392Z","event":"agent_turn","agent":"AgentA","text":"...","round":1}
```

Logs capture: node inputs, node outputs, memory snapshots, rejection reasons, duplicates detected, and the final verdict.

---

## Tests & Validation ✅

Install test deps and run the test suite:

```powershell
pip install pytest
python -m pytest -q
```

Included tests cover:
- Turn enforcement (out-of-turn calls raise errors).
- Duplicate detection across full memory.
- Memory updates after each round.
- Judge output formatting and presence of justification.

---

## Reproducible Sample Run (example) 🎯

```powershell
python scripts/sample_run.py
# or programmatically:
python -c "import scripts.sample_run as s; s.run_sample(out_log='debate_log_test.jsonl', seed=999)"
```

This writes a deterministic log (`debate_log_test.jsonl`) containing a full 8-round debate and final verdict.

---

## DAG Diagram 🗺️

Generate the DAG with Graphviz (optional):

```powershell
pip install graphviz
python generate_dag.py
# or run the CLI: the runner attempts DAG generation and will report if Graphviz isn't available
```

If system Graphviz is unavailable, `generate_dag.py` falls back to writing a simple static `dag.svg` so documentation always contains a visual artifact.

---

## Extensibility & LLM Integration 🧩

The `AgentNode` is intentionally modular:

- To call a real LLM, replace or extend `nodes/agent_node.py` to call your preferred API (OpenAI, Anthropic, etc.).
- Keep persona prompts in `persona_templates/` and load them per-agent.
- Add rate limiting, backoff, and API key configuration via environment variables or a small config file.

Security note: Do not hard-code secrets into source files. Use environment vars or `python-dotenv`.

---

## Troubleshooting ⚠️

- Module import errors when running a script (e.g., `ModuleNotFoundError: No module named 'nodes'`): run scripts from the **project root** or run via `python -m scripts.sample_run` so Python finds the package root. The project scripts also add the project root to `sys.path` to make direct script runs work.
- Graphviz errors: install the Graphviz system package and the Python package (`pip install graphviz`), then re-run `generate_dag.py`.
- Tests not found: ensure `pytest` is installed (`pip install pytest`).

---

## Limitations & Future Work 🚧

- Coherence validation and judge scoring are currently lightweight heuristics; these can be expanded with more sophisticated NLP checks or a separate adjudication LLM.
- The `--persona-config` flag is a stub for switching personas via a config file — this can be implemented to support arbitrary persona sets.
- Add concurrency controls and a visualization UI for live monitoring.

---

## Demo Video (optional)

Create a short 2–4 minute walkthrough demonstrating:

1. Installing dependencies
2. Running `run_debate.py` with an example topic and `--seed` for reproducibility
3. Inspecting the generated JSONL log and `dag.svg`
4. A short explanation of where to change personas and how to enable LLM integration

I can prepare a demo script and record the video if you'd like — say the word and I'll produce it.

---

## License

MIT — feel free to reuse and adapt.

---

If you'd like, I can also: (a) add more test cases that assert stricter coherence checks, (b) wire in an LLM with a safe abstraction layer, or (c) produce the demo video script and record it. Tell me which you'd prefer next. ✨
