# 🏋️ Genfluence — AI Fitness Influencer Pipeline

> Automated AI pipeline that researches trending fitness content, generates a character-consistent photo, writes a viral caption, and posts to Instagram — all in one command.

Built with **[CrewAI](https://docs.crewai.com/)** · Powered by **Google Gemini** · Posts via **instagrapi**

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Windows](#windows)
  - [macOS / Linux](#macos--linux)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Pre-commit Hook Setup](#-pre-commit-hook-setup)
- [CI / GitHub Actions](#-ci--github-actions)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

- 🔍 **Trend Research** — Gemini-grounded Google Search finds viral fitness topics
- ✏️ **Prompt Engineering** — Auto-generates detailed image prompts with character consistency
- 🎨 **AI Image Generation** — Gemini Image Gen creates photos with your character's face
- 📝 **Caption & Hashtags** — Writes platform-optimised captions with trending hashtags
- 👁️ **Human Review** — Preview image + caption before posting; edit or regenerate
- 📸 **Instagram Posting** — Uploads directly via instagrapi with retry logic
- 🖥️ **Two UIs** — CLI (`main.py`) or Web UI (`streamlit_app.py`)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Package Manager | [uv](https://docs.astral.sh/uv/) (cross-platform) |
| Agent Framework | CrewAI 1.9.3 |
| LLM | Google Gemini (`gemini-2.5-flash-lite` via litellm) |
| Image Generation | Gemini Image Gen (`gemini-2.5-flash-image`) |
| Instagram API | instagrapi 2.3.0 |
| Web UI | Streamlit |
| Testing | pytest 9.x + pytest-cov |

---

## 📦 Prerequisites

1. **Python 3.13+** — [Download](https://www.python.org/downloads/)
2. **uv** (recommended) — fast, cross-platform Python package manager
3. **Google Gemini API key** — [Get one here](https://aistudio.google.com/apikey)
4. **Instagram account** credentials (username + password)
5. **Character reference image** — a base photo for face consistency (placed in `assets/character.png`)

### Install uv

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🚀 Installation

### Windows

```powershell
# 1. Clone the repository
git clone <your-repo-url>
cd genfluence

# 2. Create virtual environment at repo root
uv venv .venv --python 3.13

# 3. Activate it
.venv\Scripts\Activate.ps1

# 4. Install all dependencies
uv pip install -r requirements.txt --override overrides.txt

# 5. Navigate to the project
cd fitness_influencer_crew

# 6. Copy the example env file and fill in your keys
Copy-Item .env.example .env
# Edit .env with your credentials (see Configuration section)

# 7. Set up the pre-commit hook (one-time)
.\setup-hooks.ps1

# 8. Place your character reference image
# Copy your base character photo to assets/character.png
```

### macOS / Linux

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd genfluence

# 2. Create virtual environment at repo root
uv venv .venv --python 3.13

# 3. Activate it
source .venv/bin/activate

# 4. Install all dependencies
uv pip install -r requirements.txt --override overrides.txt

# 5. Navigate to the project
cd fitness_influencer_crew

# 6. Copy the example env file and fill in your keys
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# 7. Set up the pre-commit hook (one-time)
bash setup-hooks.sh

# 8. Place your character reference image
# Copy your base character photo to assets/character.png
```

### Alternative: Install with pip (no uv)

```bash
python -m venv .venv
# Activate (see above), then:
pip install -r requirements.txt
```

> **Note:** The `overrides.txt` file forces `pydantic==2.11.10` to resolve a version conflict between CrewAI and instagrapi. If using plain pip, install pydantic manually: `pip install pydantic==2.11.10`

---

## ⚙️ Configuration

Create a `.env` file inside `fitness_influencer_crew/` (or copy `.env.example`):

```dotenv
# ── Gemini API ────────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here

# ── Image Generation ──────────────────────────────────
BASE_CHARACTER_IMAGE=assets/character.png
IMAGE_GEN_MODEL=gemini-2.5-flash-image
GEMINI_LLM_MODEL=gemini/gemini-2.5-flash-lite

# ── Instagram ─────────────────────────────────────────
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# ── Output ────────────────────────────────────────────
OUTPUT_DIR=output
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | Google Gemini API key |
| `GEMINI_LLM_MODEL` | ❌ | `gemini/gemini-2.5-flash-lite` | LLM model (litellm format) |
| `IMAGE_GEN_MODEL` | ❌ | `gemini-2.5-flash-image` | Image generation model |
| `BASE_CHARACTER_IMAGE` | ❌ | `assets/character.png` | Path to face reference image |
| `INSTAGRAM_USERNAME` | ✅ | — | Instagram login username |
| `INSTAGRAM_PASSWORD` | ✅ | — | Instagram login password |
| `OUTPUT_DIR` | ❌ | `output` | Generated images + logs directory |

---

## ▶️ Usage

Always run from inside the `fitness_influencer_crew/` directory with the venv activated.

### CLI Mode

```bash
cd fitness_influencer_crew
python main.py
```

You'll be prompted for a **creative direction** (e.g., *"Morning yoga routine in a sunny park"*). Leave blank for auto-generated content.

**Pipeline flow:**
1. 🔐 Instagram pre-flight login
2. 🔍 Research trending fitness topics
3. ✏️ Generate image prompt
4. 🎨 Create AI photo
5. 📝 Write caption + hashtags
6. 👁️ Review — approve, edit, or regenerate (up to 5×)
7. 📸 Post to Instagram

### Web UI (Streamlit)

```bash
cd fitness_influencer_crew
streamlit run streamlit_app.py
```

Opens a browser with a 4-phase interface: **Input → Review → Posting → Done**

### Quick Run (Windows)

```cmd
run.bat
```

---

## 🧪 Testing

The project includes **89 automated tests** covering agents, tasks, tools, crew assembly, and configuration.

### Run all tests

```bash
cd fitness_influencer_crew
python -m pytest tests/ -v
```

### Run with coverage report

```bash
python -m pytest tests/ --cov=. --cov-report=term-missing
```

### Run a specific test file

```bash
python -m pytest tests/test_agents.py -v
```

### Test structure

| File | Covers | Tests |
|------|--------|-------|
| `test_config.py` | Config loading, env vars, logger, LLM module | 11 |
| `test_agents.py` | All 5 agents: type, tools, delegation, max_iter | 24 |
| `test_tasks.py` | All 5 task factories: types, placeholders, outputs | 15 |
| `test_tools.py` | google_search, nano_banana, instagram, review, post_types | 24 |
| `test_crew.py` | Crew assembly: generation, posting, legacy | 15 |

> All external API calls (Gemini, Instagram) are **mocked** — tests run fully offline in ~17 seconds.

---

## 🔒 Pre-commit Hook Setup

A **pre-commit hook** runs the full test suite before every `git commit`. If any test fails, the commit is blocked.

### One-time setup (run once after cloning)

**Windows:**
```powershell
cd fitness_influencer_crew
.\setup-hooks.ps1
```

**macOS / Linux:**
```bash
cd fitness_influencer_crew
bash setup-hooks.sh
```

This tells git to use `.githooks/` as the hooks directory. The hook files are committed to the repo, so every team member gets them.

### Skip tests for a WIP commit

```bash
git commit --no-verify -m "WIP: quick save"
```

---

## ☁️ CI / GitHub Actions

A GitHub Actions workflow at `.github/workflows/tests.yml` runs the test suite automatically on:

- **Push** to `main`, `master`, or `develop`
- **Pull requests** targeting those branches

Tests run on **3 platforms** in parallel: Ubuntu, Windows, and macOS — all with Python 3.13 and uv.

---

## 📁 Project Structure

```
fitness_influencer_crew/
├── main.py                 # CLI entry point
├── streamlit_app.py        # Web UI entry point
├── crew.py                 # CrewAI crew builders
├── config.py               # Env vars + paths
├── llm.py                  # LLM model string
├── logger.py               # Centralised logging
├── .env                    # Secrets (gitignored)
├── .env.example            # Template for .env
├── setup-hooks.sh          # Hook setup (macOS/Linux)
├── setup-hooks.ps1         # Hook setup (Windows)
│
├── agents/                 # CrewAI Agent definitions
├── tasks/                  # CrewAI Task factories
├── utils/                  # Tools + helpers
├── tests/                  # pytest test suite
├── assets/                 # character.png reference image
├── output/                 # Generated images + logs
│
├── .githooks/              # Git hooks (pre-commit)
└── .github/workflows/      # GitHub Actions CI
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `pydantic` version conflict | Run with `--override overrides.txt` flag, or manually `pip install pydantic==2.11.10` |
| `login_required` from Instagram | Clear `.ig_session.json`, log in manually via browser to clear challenge, then retry |
| `429 Too Many Requests` from Gemini | Free-tier rate limit hit. Wait a few minutes or upgrade your API plan |
| Tests fail after upgrading deps | Run `python -m pytest tests/ -v` to see which validations broke |
| `ImportError: Google Gen AI native provider not available` | Install the extra: `uv pip install crewai[google-genai]==1.9.3` |
| Pre-commit hook not running | Re-run `.\setup-hooks.ps1` or `bash setup-hooks.sh` |

---

## 📄 License

See [LICENSE](LICENSE) for details.
