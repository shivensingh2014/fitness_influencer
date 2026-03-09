# Copilot Custom Instructions – Genfluence (fitness_influencer_crew)

## 🧠 Context File — READ FIRST

Before answering **any** question or making **any** code change, read `CODEBASE_CONTEXT.md`
at the project root. It contains the full architecture, pipeline flow, agent/task/tool details,
configuration, testing strategy, and known gotchas.

## 📐 Code Style & Conventions

- **Python 3.13**, type hints encouraged but not enforced.
- Use `from logger import log` for all logging — never bare `print()` in production code.
- All configuration comes from `config.py` (which reads `.env`). Never hard-code API keys or paths.
- Imports: stdlib → third-party → local, separated by blank lines.
- CrewAI agents go in `agents/`, one agent per file, exported as a module-level variable.
- CrewAI tasks go in `tasks/`, one task factory function per file (`create_*_task()`).
- CrewAI tools go in `utils/`, decorated with `@tool("tool_name")`.

## 🏗️ Architecture Rules

- Crew assembly happens in `crew.py` — never instantiate a `Crew` elsewhere.
- The pipeline is sequential: Research → Prompt → Image → Caption → (Review) → Post.
- `main.py` is the CLI entry point; `streamlit_app.py` is the web UI. Keep them in sync.
- `build_generation_crew()` returns 4 agents + 4 tasks. `build_posting_crew()` returns 1+1.
- Human review happens **between** generation and posting (not inside a crew).

## 🧪 Testing Rules

- All tests live in `tests/`. Naming: `test_<module>.py`, classes `Test*`, functions `test_*`.
- Every new agent, task, or tool **must** have corresponding tests.
- Tests must run **offline** — mock all external API calls (Gemini, Instagram, HTTP).
- Use `conftest.py` fixtures for env isolation; never touch real credentials in tests.
- Run `python -m pytest tests/ -v` to verify before committing.
- The pre-commit hook runs tests automatically; CI runs them on push/PR to main.

## 📝 Maintenance Rule

> **When you modify agents, tasks, tools, pipeline flow, config variables, dependencies,
> or the test suite — update `CODEBASE_CONTEXT.md` to reflect the change.**

This includes:
- Adding/removing/renaming any agent, task, or tool
- Changing the pipeline flow or crew composition
- Adding new environment variables or config options
- Changing the directory structure
- Adding new test files or significantly changing test counts
- Updating dependencies in `requirements.txt`

## 📦 Dependencies

- Managed with **uv** (`uv pip install -r requirements.txt --override overrides.txt`).
- Pin major versions for `crewai`, `instagrapi`, and `pydantic` to avoid breakage.
- `overrides.txt` resolves the pydantic version conflict between crewai and instagrapi.

## ⚠️ Things to Watch Out For

- `agents/director.py` and `tasks/synthesis_task.py` are **legacy/unused** — don't wire them in.
- Instagram's `login_required` errors are common — the retry logic in `instagram_tool.py` handles it.
- Gemini free-tier has strict rate limits — crews use `max_rpm=5`.
- Caption parsing depends on `CAPTION:` and `HASHTAGS:` markers — keep that format in agent prompts.
- Paths may contain spaces (OneDrive) — always quote paths in scripts and hooks.
