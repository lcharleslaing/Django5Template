import os, json
from typing import Dict, Any
try:
    from django.conf import settings
except Exception:
    settings = None

def _get_openai_config():
    api_key = (getattr(settings, "OPENAI_API_KEY", "") if settings else "") or os.getenv("OPENAI_API_KEY", "")
    model = (getattr(settings, "OPENAI_MODEL", "") if settings else "") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = (getattr(settings, "OPENAI_BASE_URL", "") if settings else "") or os.getenv("OPENAI_BASE_URL", "")
    return api_key, model, base_url

USE_OPENAI = True
if USE_OPENAI:
    try:
        from openai import OpenAI
        _api_key, _model, _base = _get_openai_config()
        _client = OpenAI(api_key=_api_key, base_url=_base or None)
    except Exception:
        _client = None

SCHEMA = {
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "description": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"},
          "questions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": {"type": "string", "enum": ["LIKERT","MULTI","SINGLE","MATRIX","SHORT_TEXT","LONG_TEXT","NPS","RANK","DATE","NUMBER"]},
                "prompt": {"type": "string"},
                "help_text": {"type": "string"},
                "required": {"type": "boolean"},
                "anonymity_mode": {"type": "string", "enum": ["ANONYMOUS","ESCROW","SIGNED"]},
                "options": {"type": "array", "items": {"type": "string"}},
                "scale_min": {"type": "integer"},
                "scale_max": {"type": "integer"}
              },
              "required": ["type","prompt","required","anonymity_mode"]
            }
          }
        },
        "required": ["title","questions"]
      }
    }
  },
  "required": ["title","sections"]
}

SYSTEM_PROMPT = """You create high-signal employee surveys for internal use.
Return STRICT JSON matching the provided schema. Do not include commentary.
Rules:
- Mix anonymity modes: ESCROW for sensitive, SIGNED for commitments, ANONYMOUS for catch-all/NPS.
- 3–5 sections, 10–20 questions total.
- Keep Likert scales 1–5 unless NPS 0–10.
- For MULTI/SINGLE give 3–7 options.
- Keep prompts concrete and behavior-based; avoid fluff.
"""

def _mk_user_prompt(topic:str, goals:str, audience:str, tone:str, length_hint:str):
    return f"""Topic: {topic}
Goals: {goals}
Audience: {audience}
Tone: {tone}
Length: {length_hint}

Output JSON ONLY that fits the schema."""

def generate_survey_json(topic:str, goals:str="", audience:str="company-wide", tone:str="direct, respectful", length_hint:str="~15 minutes") -> Dict[str, Any]:
    if not _client:
        # Fallback minimal stub for dev without API key
        return {
            "title": f"AI: {topic}",
            "description": goals or "",
            "sections": [
                {
                    "title": "Overview",
                    "description": "Auto-generated",
                    "questions": [
                        {"type":"NPS","prompt":"How likely are you to recommend working here?","help_text":"0-10","required":True,"anonymity_mode":"ANONYMOUS","scale_min":0,"scale_max":10},
                        {"type":"LIKERT","prompt":"I have clarity on my priorities.","help_text":"1-5","required":True,"anonymity_mode":"ESCROW","scale_min":1,"scale_max":5},
                        {"type":"LONG_TEXT","prompt":"What should we start, stop, continue?","help_text":"","required":False,"anonymity_mode":"ESCROW"}
                    ]
                }
            ]
        }

    resp = _client.chat.completions.create(
        model=_model,
        temperature=0.2,
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":_mk_user_prompt(topic,goals,audience,tone,length_hint)},
            {"role":"system","content":f"JSON Schema (for reference): {json.dumps(SCHEMA)}"}
        ]
    )
    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{"); end = content.rfind("}")
        return json.loads(content[start:end+1])


