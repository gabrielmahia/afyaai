"""
AfyaAI — Kenya Health Assistant
Maternal health, NHIF/SHA navigation, clinical guidance for Kenya.
"""
import sys, json, urllib.request, ssl
import streamlit as st

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AfyaAI — Kenya Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Gemini API ────────────────────────────────────────────────
def get_gemini_key():
    try:
        return st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None

def gemini(prompt: str, key: str, max_tokens: int = 1200) -> str:
    """Call Gemini — returns a graceful fallback string, never raises."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    prompt = prompt[:5000]
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens}}
    req = urllib.request.Request(f"{url}?key={key}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            d = json.loads(r.read())
        candidates = d.get("candidates", [])
        if not candidates:
            return "_No response generated. Try again._"
        return candidates[0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            detail = str(e)
        return f"_AI temporarily unavailable (HTTP {e.code}). {detail}_"
    except Exception as e:
        return f"_AI call failed: {type(e).__name__}. Check GOOGLE_API_KEY in Streamlit secrets._"
