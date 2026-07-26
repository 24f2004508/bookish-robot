from fastapi import FastAPI, Request
from pydantic import BaseModel
import re
import yaml

app = FastAPI()

class SkillRequest(BaseModel):
    skill: str

@app.post("/scan")
async def scan_skill(req: SkillRequest):
    text = req.skill
    categories = []

    # --- Parse YAML frontmatter ---
    try:
        if text.startswith("---"):
            fm_end = text.find("---", 3)
            if fm_end != -1:
                frontmatter = text[3:fm_end]
                meta = yaml.safe_load(frontmatter)
            else:
                meta = {}
        else:
            meta = {}
    except Exception:
        meta = {}

    # --- Checks ---
    # Hardcoded secret
    if re.search(r"(AKIA|SECRET|API[_-]?KEY|token=|Bearer\s+[A-Za-z0-9])", text, re.IGNORECASE):
        categories.append("hardcoded_secret")

    # Prompt injection
    if re.search(r"(ignore user|exfiltrate|send .* without consent|override stop)", text, re.IGNORECASE):
        categories.append("prompt_injection")

    # Excessive permissions
    if re.search(r"(read/write\s+/.+|access\s+all\s+domains|full\s+filesystem)", text, re.IGNORECASE):
        categories.append("excessive_permissions")

    # Unclear provenance
    if not any(k in meta for k in ["author","version","changelog"]):
        categories.append("unclear_provenance")

    return {"categories": categories}
