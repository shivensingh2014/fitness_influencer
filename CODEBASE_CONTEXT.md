# 🧠 Genfluence – Codebase Context File
> **Last updated:** March 17, 2026 (Automatic JPG conversion for Instagram image uploads to prevent format errors)  
> **Purpose:** Quick reference for AI assistants and developers. Read this FIRST before modifying any code.
>
> ⚠️ **MAINTENANCE RULE:** This file must be updated whenever the code structure changes.  
> The rule is enforced by `.github/copilot-instructions.md` which Copilot reads automatically.  
> If you modify agents, tasks, tools, pipeline flow, config vars, or dependencies — update this file too.

---

## 📌 Project Overview

**Genfluence** is an automated AI fitness influencer pipeline built with [CrewAI](https://docs.crewai.com/).  
It lets the user select an influencer profile, researches trending fitness content, generates a character-consistent AI photo, writes a viral caption + hashtags, lets the user review everything, and posts to Instagram — all in one `python main.py` run.

In Streamlit, there is now an explicit setup flow before generation:
1) save influencer profile + content type,
2) run influencer strategy task to generate a digital twin context,
3) show sanitized first-agent strategy output on Setup page,
4) click Generate Ideas to run only the researcher agent using that strategy output as backstory,
5) select one idea and generate content package,
6) approve package, then move to a dedicated media page:
   - post → generate one image from `IMAGE_PROMPT`, upload to Instagram via `photo_upload()`
   - carousel → generate multiple images from `SLIDE_n_PROMPT`, upload to Instagram via `album_upload()`
   - reel → show `VIDEO_SCRIPT` only (no image generation, no posting yet).

---

## 🗂️ Directory Structure

```
fitness_crew/                     ← PROJECT ROOT (run from here)
│
├── main.py                        ← CLI entry point: python main.py
├── streamlit_app.py               ← Web UI entry point: streamlit run streamlit_app.py
├── crew.py                        ← CrewAI crew builders (generation + posting)
├── config.py                      ← All env vars, paths, API keys (reads .env)
├── llm.py                         ← LLM model string export (used by agents)
├── logger.py                      ← Centralised logger → console + output/genfluence.log
├── requirements.txt               ← pip dependencies (self-contained)
├── overrides.txt                  ← uv override for pydantic version conflict
├── run.bat                        ← Windows batch launcher
├── .env                           ← Secrets (GEMINI_API_KEY, IG creds, etc.)
├── .ig_session.json               ← Cached Instagram session (auto-generated, gitignored)
├── CODEBASE_CONTEXT.md            ← THIS FILE
├── README.md                      ← Full installation & usage guide
├── setup-hooks.sh                 ← macOS/Linux: run once to enable pre-commit hook
├── setup-hooks.ps1                ← Windows: run once to enable pre-commit hook
│
├── .githooks/                     ← Git hooks (committed, shared across team)
│   ├── pre-commit                 ← Bash: runs pytest before every commit
│   └── pre-commit.ps1             ← PowerShell: same hook for Windows
│
├── .github/
│   ├── copilot-instructions.md    ← Copilot reads this automatically every session
│   └── workflows/
│       └── tests.yml              ← Runs tests on push/PR to main (Win + Mac + Linux)
│
├── agents/                        ← CrewAI Agent definitions (one per file)
│   ├── influencer_persona.py      ← Influencer Persona Strategist & QA Reviewer
│   ├── researcher.py              ← Fitness Trend Researcher (uses google_search tool)
│   ├── content_creator.py         ← Multi-format Content Creator (post/carousel/reel package)
│   ├── prompt_creator.py          ← Nano Banana Prompt Engineer (no tools)
│   ├── image_generator.py         ← AI Image Generator (uses generate_image tool)
│   ├── caption_creator.py         ← Caption & Hashtag Creator (no tools)
│   ├── instagram_poster.py        ← Instagram Poster (uses post_to_instagram tool)
│   └── director.py                ← Creative Director (UNUSED – legacy, not wired in)
│
├── tasks/                         ← CrewAI Task factory functions (one per file)
│   ├── influencer_strategy_task.py← create_influencer_strategy_task(agent)
│   ├── research_task.py           ← create_research_task(agent)
│   ├── content_package_task.py    ← create_content_package_task(agent)
│   ├── prompt_task.py             ← create_prompt_task(agent, context)
│   ├── generate_image_task.py     ← create_generate_image_task(agent, context)
│   ├── caption_hashtag_task.py    ← create_caption_hashtag_task(agent, context)
│   ├── influencer_validation_task.py ← create_influencer_validation_task(agent, context)
│   ├── post_to_instagram_task.py  ← create_post_to_instagram_task(agent, context, image_path?, caption?)
│   └── synthesis_task.py          ← UNUSED – legacy, not wired in
│
├── utils/                         ← CrewAI Tools + helper modules
│   ├── google_search_tool.py      ← @tool("google_search") – Gemini grounded search with cache
│   ├── nano_banana_tool.py        ← @tool("generate_image") – Gemini image gen + character ref
│   ├── instagram_tool.py          ← @tool("post_to_instagram") + carousel_upload() + preflight_login()
│   ├── text_overlay.py            ← Text overlay utilities for carousel slides (add_carousel_overlays)
│   ├── influencer_context.py      ← Loads influencer profiles from influencer_context/*.txt
│   ├── review.py                  ← Human review UI: display_review(), ask_approval(), extract_image_and_caption()
│   └── post_types.py              ← 12 diverse post categories + pick_random_post_type()
│
├── influencer_context/            ← Per-influencer profile files (*.txt)
│   ├── Aisha.txt                  ← Influencer context profile
│   ├── Billa.txt                  ← Influencer context profile
│   └── Varun.txt                  ← Influencer context profile
│
├── tests/                         ← pytest test suite (≈121 tests)
│   ├── conftest.py                ← Shared fixtures, env isolation, tmp dirs
│   ├── test_config.py             ← Config loading, logger, llm module tests
│   ├── test_agents.py             ← All 5 agent definitions + cross-cutting checks
│   ├── test_tasks.py              ← All task factories incl. influencer strategy/validation
│   ├── test_tools.py              ← google_search, nano_banana, instagram_tool, review, post_types, influencer_context
│   ├── test_crew.py               ← Crew assembly integration tests incl. influencer persona flow
│   └── test_streamlit_app.py      ← Streamlit UI: import, session state, helpers, preflight
│
├── assets/
│   └── character.png              ← Base character reference image for face consistency
│
└── output/                        ← Generated images + logs land here
    ├── generated_YYYYMMDD_HHMMSS.png
    └── genfluence.log
```

---

## 🔄 Pipeline Flow (main.py)

```
Step -1 🧍 Influencer profile selection (user selects from influencer_context/*.txt)
             └─ User must click Confirm Influencer in Streamlit
             └─ Stored in `influencer_profile`
             └─ Passed to generation tasks via crew.kickoff(inputs={...})
Step -0.5 🎬 Content type selection (`post` / `carousel` / `reel`)
             └─ Stored in `content_format`
             └─ Passed to generation tasks via crew.kickoff(inputs={...})
Step 1  🔐  Instagram pre-flight login (fail-fast)
             └─ preflight_login() → caches Client in _SHARED_CLIENT
Step 1b 🔑  Gemini API quota check (lightweight test call)

┌─── GENERATION LOOP (up to 5 attempts) ────────────────────────┐
│                                                                │
│  Step 2  🧠  Influencer strategy brief                          │
│  Step 3  🔍  Research (+ persona + format)                     │
│  Step 4  ✏️   Prompt  (+ persona + format)                     │
│  Step 5  🎨  Image   (+ persona + format)                     │
│  Step 6  📝  Caption (+ persona + format)                      │
│  Step 7  ✅ Persona validation (PASS/REVISE + final caption)   │
│                                                                │
│  Step 8  👁️   HUMAN REVIEW                                     │
│           ├─ Opens image in OS viewer                          │
│           ├─ Prints caption in formatted box                   │
│           ├─ yes → proceed to Step 9                           │
│           └─ no  → loop back to Step 2 (regenerate)            │
│                                                                │
│  Step 9  📸  Post to Instagram (posting crew, reuses client)   │
└────────────────────────────────────────────────────────────────┘
```

### Influencer Profile + Content Type → Agent Flow
The selected `influencer_profile` and `content_format` are injected into generation
task descriptions via placeholders and context. CrewAI kickoff inputs replace them at
runtime, so every generation agent receives both context values directly.

`influencer_persona` backstory is dynamic: `build_generation_crew(influencer_profile=...)`
creates the persona agent with the selected influencer `.txt` content embedded in its
backstory before the generation crew runs.

---

## 🏗️ Crew Architecture (crew.py)

### `build_generation_crew()` → 5 agents, 6 tasks, sequential
| # | Task Factory | Agent | Tool | Context |
|---|-------------|-------|------|---------|
| 1 | `create_influencer_strategy_task` | influencer_persona | — | — (uses influencer profile + content format only) |
| 2 | `create_research_task` | researcher | `google_search` | [1] (strategy-driven, generic prompt) |
| 3 | `create_prompt_task` | prompt_creator | — | [1, 2] |
| 4 | `create_generate_image_task` | image_generator | `generate_image` | [3] |
| 5 | `create_caption_hashtag_task` | caption_creator | — | [1, 2, 3] |
| 6 | `create_influencer_validation_task` | influencer_persona | — | [1, 2, 3, 4, 5] |

### `build_posting_crew(image_path, caption)` → 1 agent, 1 task, sequential
| # | Task Factory | Agent | Tool | Notes |
|---|-------------|-------|------|-------|
| 1 | `create_post_to_instagram_task` | instagram_poster | `post_to_instagram` | Receives pre-approved image_path + caption as explicit params |

### `build_crew()` — legacy full 5-step crew (no review). Not used by main.py.

---

## 🤖 Agent Details

| Agent | File | Role | LLM | Tools | max_iter |
|-------|------|------|-----|-------|----------|
| **influencer_persona** | `agents/influencer_persona.py` | Influencer Persona Strategist & QA Reviewer | gemini-2.5-flash-lite | — | 3 |
| **researcher** | `agents/researcher.py` | Trend & Culture Researcher | gemini-2.5-flash-lite | google_search | 3 |
| **prompt_creator** | `agents/prompt_creator.py` | Prompt Engineer & Creative Director | gemini-2.5-flash-lite | — | 3 |
| **image_generator** | `agents/image_generator.py` | AI Image Generator | gemini-2.5-flash-lite | generate_image | 3 |
| **caption_creator** | `agents/caption_creator.py` | Social Media Copywriter & Brand Voice | gemini-2.5-flash-lite | — | 3 |
| **instagram_poster** | `agents/instagram_poster.py` | Social Media Publisher | gemini-2.5-flash-lite | post_to_instagram | 3 |
| ~~director~~ | `agents/director.py` | ~~Creative Director~~ | — | — | — (UNUSED) |

All agents: `allow_delegation=False`, `max_retry_limit=1`

---

## 🔧 Tool Details

### `google_search` (utils/google_search_tool.py)
- Uses `google.generativeai` SDK with `tools=["google_search"]` (grounding)
- Model: `gemini-2.5-flash-lite`
- In-memory MD5 cache to avoid duplicate API calls
- Strict input guardrails: empty queries fail fast; very long queries are normalized/truncated
- Compatibility: optional `mode` arg is accepted and ignored to prevent tool-call schema mismatches
- Returns: text summary of search results

### `generate_image` (utils/nano_banana_tool.py)
- REST API call to `generativelanguage.googleapis.com` (Gemini Image Generation)
- Model: `gemini-2.5-flash-image` (configurable via `IMAGE_GEN_MODEL`)
- Attaches `assets/character.png` as base64 inline data for face consistency
- Prepends identity-preservation instructions to the prompt
- Saves output as `output/generated_YYYYMMDD_HHMMSS.png`
- Returns: absolute file path string

### `post_to_instagram` (utils/instagram_tool.py)
- REST API call to Instagram via `instagrapi.Client` (Instagram Private API)
- Reuses `_SHARED_CLIENT` if `preflight_login()` was called earlier
- Session persistence: `.ig_session.json`
- Upload retry: if `login_required` during upload → re-auth + retry once
- **Automatic JPG conversion:** Calls `_ensure_jpg_format()` to convert PNG/other formats to JPG (Instagram prefers JPG)
- `cl.delay_range = [2, 5]` for human-like pacing
- Single image: `cl.photo_upload(path, caption)`
- Returns: success message with post URL, or error string

### `carousel_upload` (utils/instagram_tool.py) — private helper
- Uploads **carousel (album) posts** with multiple images to Instagram
- **Automatic JPG conversion:** Each image is converted to JPG before upload via `_ensure_jpg_format()`
- **Method:** `cl.album_upload(paths=[...], caption=caption)` 
  - `paths` is a list of absolute file paths to image files (all converted to JPG)
  - Instagram accepts **2–10 images** per carousel
  - Each image is displayed as a separate slide in the carousel
- Reuses `_SHARED_CLIENT` if available, else creates a new authenticated client
- Upload retry: same login_required recovery as single-image posts
- Returns: success message with post URL (`https://instagram.com/p/{code}/`), or error string
- **Used by:** Streamlit posting phase when `content_format = "carousel"`

### `_ensure_jpg_format()` (utils/instagram_tool.py) — image conversion helper
- Automatically converts PNG and other image formats to JPG (Instagram compatibility fix)
- If image is already JPG/JPEG: returns original path unchanged
- If image is PNG/other format: opens with PIL, converts RGBA→RGB with white background, saves as JPG with 95% quality
- Returns: path to JPG file (newly converted or original if already JPG)
- **Called by:** `carousel_upload()` and `post_to_instagram()` before uploading
- **Purpose:** Prevents "unknown error" failures on Instagram's API when non-JPG images are uploaded

### `preflight_login()` (utils/instagram_tool.py)
- Called from `main.py` Step 0 before any crew work
- Tries saved session → validates with `account_info()` → falls back to fresh login
- Caches the Client in module-level `_SHARED_CLIENT`
- Raises exception on failure (pipeline aborts immediately)

### `add_carousel_overlays` (utils/text_overlay.py)
- Adds eye-catching text overlays to carousel slide images forming a story sequence
- Each slide gets a short text label (1-3 words) that forms a narrative arc
- Text rendered in semi-transparent black background box with white bold font
- Top position for slide 1 (hero), bottom for subsequent slides
- Story example: "GHAR KI MASHAL" → "NO EXCUSES" → "PUSH HARDER" → "BE STRONGER" → "YOU GOT THIS"
- Integrated into Streamlit carousel media generation (automatic, non-blocking)

---

## 📋 Review Module (utils/review.py)

| Function | Purpose |
|----------|---------|
| `open_image(path)` | Opens image in OS default viewer (Windows: `os.startfile`) |
| `display_review(image_path, caption)` | Prints formatted Unicode box with image path + caption |
| `ask_approval()` → `bool` | Interactive yes/no prompt. `True` = post, `False` = regenerate |
| `extract_image_and_caption(crew_output)` → `(str, str)` | Parses crew output for image path + CAPTION:/HASHTAGS: markers. Fallback: scans output dir for latest `generated_*.png` |

---

## ⚙️ Configuration (config.py + .env)

| Variable | Source | Default | Description |
|----------|--------|---------|-------------|
| `GEMINI_API_KEY` | .env | `""` | Google Gemini API key |
| `GEMINI_LLM_MODEL` | .env | `gemini/gemini-2.5-flash-lite` | LLM model string (litellm format) |
| `IMAGE_GEN_MODEL` | .env | `gemini-2.5-flash-image` | Image generation model |
| `BASE_CHARACTER_IMAGE` | .env | `assets/character.png` | Path to face-consistency reference |
| `INSTAGRAM_USERNAME` | .env | `""` | Instagram handle |
| `INSTAGRAM_PASSWORD` | .env | `""` | Instagram password |
| `OUTPUT_DIR` | .env | `output` | Where generated images + logs go |
| `INFLUENCER_CONTEXT_DIR` | .env | `influencer_context` | Folder with influencer profile `.txt` files |

Config also exports: `BASE_DIR`, `ASSETS_DIR`, `OUTPUT_DIR`, `INFLUENCER_CONTEXT_DIR` (as Path objects, auto-created).

---

## 📦 Dependencies

All deps live in `requirements.txt` at the project root (self-contained, no parent references).  
Managed with **uv** — use `uv pip install -r requirements.txt --override overrides.txt`.  
`overrides.txt` resolves the pydantic version conflict between crewai and instagrapi.

```
crewai==1.9.3
crewai-tools==1.9.3
google-generativeai>=0.8.0
litellm>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
Pillow>=10.0.0
instagrapi==2.3.0
pydantic==2.11.10
streamlit
```

---

## 🪵 Logging (logger.py)

- Logger name: `genfluence`
- Console: INFO+ with timestamped format
- File: `output/genfluence.log` – DEBUG+, rotating 2 MB × 3 backups
- Import: `from logger import log` everywhere

---

## ⚠️ Known Gotchas / Notes

1. **Unused files:** `agents/director.py` and `tasks/synthesis_task.py` are legacy and NOT wired into any crew.
2. **Instagram `login_required`:** Common with `instagrapi`. The pre-flight login + upload retry handles most cases. If it persists → manual browser login to clear challenge.
3. **Gemini free-tier limits:** `max_rpm=5` on crews. Quota check runs before crew work. 429s trigger clear error messages.
4. **Research tool contract:** researcher must call `google_search` with one plain query string only; no extra parameters (`mode`, filters, JSON payloads, etc.).
5. **Caption parsing:** `extract_image_and_caption()` looks for `CAPTION:` and `HASHTAGS:` markers. If the LLM doesn't follow format, fallback uses raw output.
6. **Image path extraction:** First tries parsing crew output for `.png`/`.jpg` paths. Fallback scans `output/` for most recent `generated_*.png` by mtime.
7. **Session file:** `.ig_session.json` — auto-created, should be gitignored. Deleted on fresh login.
8. **OS-specific:** `open_image()` uses `os.startfile` on Windows, `open` on macOS, `xdg-open` on Linux.
9. **`post_to_instagram_task`** accepts optional `image_path` and `caption` kwargs — used by `build_posting_crew()` to bake approved content directly into the task description.

---

## 🚀 How to Run

```bash
# From repo root (genfluence/):
uv venv .venv --python 3.13
# Activate:
#   macOS/Linux : source .venv/bin/activate
#   Windows PS  : .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt --override overrides.txt

# Fill in fitness_crew/.env with your keys

cd fitness_crew

# Option A – CLI (terminal)
python main.py

# Option B – Web UI (Streamlit)
streamlit run streamlit_app.py
```

### Streamlit UI (streamlit_app.py)

A browser-based interface with 6 phases managed via `st.session_state`:

| Phase | What happens |
|-------|--------------|
| **input** | Select influencer + content type, confirm, save setup, generate digital twin |
| **creative** | Generate and select idea |
| **generate** | Generate content package from selected idea, preview results, Approve or Regenerate package |
| **review** | Shows generated image + editable caption → "Post to Instagram" / "Regenerate" |
| **posting** | Runs posting crew with spinner |
| **done** | Shows success message, post URL, balloons, "Create Another Post" button |

Pre-flight checks (IG login + Gemini quota) run once per session on first generation.
The review phase allows editing the caption before posting. Regeneration loops up to 5×.

---

## 🧪 Testing (tests/)

**Run all 105 tests:**
```bash
cd fitness_influencer_crew
python -m pytest tests/ -v
```

**Test coverage:**
```bash
python -m pytest tests/ --cov=. --cov-report=term-missing
```

### Test Structure

| File | What it covers | # Tests |
|------|---------------|---------|
| `test_config.py` | Config loading, env vars, logger, llm module | 11 |
| `test_agents.py` | All 5 agents: type, tools, role, delegation, max_iter + cross-cutting | 24 |
| `test_tasks.py` | All 5 task factories: type, placeholders, expected output, context | 15 |
| `test_tools.py` | google_search, nano_banana, instagram, review, post_types (all mocked) | 24 |
| `test_crew.py` | Crew assembly: generation (4+4), posting (1+1), legacy (5+5) | 15 |
| `test_streamlit_app.py` | Streamlit UI: import, session state defaults, helper functions, preflight checks | 16 |

### Key Design Decisions
- **conftest.py** sets safe dummy env vars via `monkeypatch` → no real API keys ever touched
- All external calls (Gemini, Instagram) are **mocked** → tests run offline and fast (~14s)
- Agent/crew tests use **real CrewAI objects** (not mocks) to catch pydantic validation regressions
- Streamlit tests mock the entire `st` module to avoid launching a real server
- `tmp_path` fixture isolates output files per test

### Automatic Test Runs (CI / Pre-commit)

Tests run **automatically** in two places:

| Trigger | Mechanism | Where |
|---------|-----------|-------|
| Every `git commit` | Pre-commit hook (`.githooks/pre-commit`) | Local machine |
| Every push / PR to main | GitHub Actions (`.github/workflows/tests.yml`) | GitHub CI (Win + Mac + Linux) |

**One-time setup** (run once after cloning):
```bash
# macOS / Linux
bash setup-hooks.sh

# Windows PowerShell
.\setup-hooks.ps1
```
This tells git to use `.githooks/` as the hooks directory. The hook runs `pytest tests/ -q` and **blocks the commit if any test fails**.

To skip tests for a quick WIP commit: `git commit --no-verify`

### When to Run Tests Manually
- **After upgrading** crewai, instagrapi, or pydantic (dependency validation tests)
- **After adding** a new agent, task, or tool (add matching test file too)

---

**Last updated:** March 9, 2026  
**Maintainer:** Update this file whenever you modify agents, tasks, tools, pipeline flow, or dependencies.  
**Auto-read by Copilot** via `.github/copilot-instructions.md`.