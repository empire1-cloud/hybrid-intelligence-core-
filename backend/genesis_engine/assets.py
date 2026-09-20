"""Deterministic asset manifest and lightweight playable SVG asset generation."""
from __future__ import annotations
import html, uuid
from pathlib import Path
from typing import Any, Dict, List

FISH = [("small", "Fish Small", 96), ("medium", "Fish Medium", 128), ("large", "Fish Large", 176), ("boss", "Fish Boss", 240)]

def build_assets(spec: Any, root: Path) -> List[Dict[str, Any]]:
    out = root / "assets"; out.mkdir(parents=True, exist_ok=True)
    assets=[]
    for key,name,size in FISH:
        path=out/f"fish_{key}.svg"
        color={"small":"#48bfe3","medium":"#64dfdf","large":"#ffd166","boss":"#ef476f"}[key]
        label=html.escape(name)
        path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size/2:.0f}" viewBox="0 0 240 120"><ellipse cx="110" cy="60" rx="78" ry="42" fill="{color}"/><polygon points="180,60 235,25 235,95" fill="{color}"/><circle cx="70" cy="48" r="7" fill="#071018"/><text x="120" y="66" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#071018">{label}</text></svg>''', encoding="utf-8")
        assets.append({"id":str(uuid.uuid4()),"type":"sprite","name":name,"path":str(path.relative_to(root)),"dimensions":{"width":size,"height":int(size/2)},"source":"genesis_deterministic_placeholder"})
    return assets
