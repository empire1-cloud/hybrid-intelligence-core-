"""Audio manifest builder. Actual audio generation is intentionally provider-agnostic."""
from typing import Any, Dict, List

def build_audio_manifest(spec: Any) -> List[Dict[str, Any]]:
    names=["shot","hit","big_win","boss_hit","background"]
    return [{"id":f"audio_{n}","name":n,"format":"ogg","path":f"audio/{n}.ogg","status":"manifest_only","generator":"provider_adapter"} for n in names]
