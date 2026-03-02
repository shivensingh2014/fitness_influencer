# tools/google_search_tool.py
import os
import hashlib
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool

# import logger from project root
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logger import log

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Simple in-memory cache to avoid duplicate search API calls
_search_cache: dict[str, str] = {}


@tool("google_search")
def google_search(query: str) -> str:
    """
    Uses Gemini's Google Search grounding to fetch real-time information.
    Returns a concise textual summary for agents to consume.
    Results are cached so the same query never burns a second API call.
    """
    cache_key = hashlib.md5(query.lower().strip().encode()).hexdigest()
    if cache_key in _search_cache:
        log.info("[google_search] CACHE HIT for: %s", query[:80])
        return _search_cache[cache_key]

    log.info("[google_search] Calling Gemini (gemini-2.5-flash-lite + grounding) query=%s", query[:80])
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            tools=["google_search"]
        )
        resp = model.generate_content(
            [{"role": "user", "parts": [{"text": f"Search the web and summarize: {query}"}]}]
        )
        result = (resp.text or "").strip()
        log.info("[google_search] Success – response length: %d chars", len(result))
        log.debug("[google_search] Response preview: %s", result[:200])
        _search_cache[cache_key] = result
        return result
    except Exception as exc:
        log.error("[google_search] FAILED: %s", exc)
        log.debug("[google_search] Traceback:\n%s", traceback.format_exc())
        return f"ERROR: Google search failed – {exc}"
