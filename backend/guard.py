"""Dependency-free security primitives (tokens, RBAC, prompt-injection screening, LLM-output validation)."""
from __future__ import annotations
import hmac, os, re, unicodedata

ROLE_ACTIONS = {"viewer": {"view"}, "analyst": {"view", "score", "trace", "simulate", "recommend", "feedback"}, "admin": {"view", "score", "trace", "simulate", "recommend", "feedback", "admin"}}

def _tokens() -> dict[str, str]:
    raw = os.getenv("FLOWFREEZE_API_TOKENS", "")
    if not raw and os.getenv("FLOWFREEZE_DEMO_MODE", "false").lower() == "true": raw = "demo-analyst-token:analyst,demo-viewer-token:viewer"   # demo only, never default
    return {t.strip(): r.strip() for t, _, r in (x.partition(":") for x in raw.split(",") if ":" in x)}

def role_for(token: str | None) -> str | None:
    if not token: return None
    found = None
    for known, role in _tokens().items():
        if hmac.compare_digest(known.encode(), token.encode()): found = role     # constant-time compare
    return found

def authenticate(token: str | None) -> bool: return role_for(token) is not None
def authorized(role: str | None, action: str) -> bool: return action in ROLE_ACTIONS.get(role or "", set())

INJECTION = [r"ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)", r"disregard\s+(the\s+)?(rules|policy|instructions|above)", r"system\s*prompt|developer\s+message",
             r"bypass\s+(the\s+)?(approval|review|policy|human)", r"override\s+(the\s+)?(policy|threshold|hold|approval|score)", r"reveal\s+(the\s+)?(secret|key|prompt|token)",
             r"you\s+are\s+now|act\s+as\s+(an?\s+)?(admin|system)", r"(release|unfreeze|approve)\s+(the\s+)?(funds|hold|transfer)", r"<\s*\|?\s*(system|assistant)\s*\|?\s*>"]
def _norm(t: str) -> str: return re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFKC", t) if unicodedata.category(c) != "Cf")).lower()

def detect_prompt_injection(text: str) -> dict:
    t = _norm(text); hits = [p for p in INJECTION if re.search(p, t)]
    return {"blocked": bool(hits), "matches": hits, "layer": "heuristic screen (one layer, not the defence)",
            "policy": "structured evidence is authoritative; free text cannot change risk, amount, scope, or approval"}

def sanitize_untrusted(items: list[str]):
    clean, flags = [], []
    for it in items:
        r = detect_prompt_injection(str(it))
        (flags if r["blocked"] else clean).append(str(it)[:300] if not r["blocked"] else {"text": str(it)[:80], "matches": r["matches"]})
    return clean, flags

def llm_output_ok(text: str, allowed_numbers: set[str]) -> bool:
    """Reject LLM text that introduces money amounts / scores not present in the structured result, or tries to decide."""
    nums = {n.replace(",", "") for n in re.findall(r"\d[\d,]{2,}", text)}
    if nums - {a.replace(",", "") for a in allowed_numbers}: return False
    return not re.search(r"\b(i (have )?(approve|release|freeze)|approved|funds (are|have been) (frozen|released))\b", text.lower())
