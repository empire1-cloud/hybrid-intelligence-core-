"""Deployment artifact generation. No cloud credentials are required to produce the artifact."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict

def build_deployment_artifact(spec: Any, root: Path, build: Dict[str, Any]) -> Dict[str, Any]:
    artifact={"engine":"Genesis Engine","game":spec.name,"platform":spec.target_platform,"artifact":build.get("web_zip"),"deployment_mode":"static-cdn","entrypoint":"web/index.html","cache_policy":"immutable-assets","health_path":"/index.html","credentials_required":True,"status":"deployment_ready"}
    path=root/"deployment.json"
    path.write_text(json.dumps(artifact,indent=2),encoding="utf-8")
    return {"type":"deployment","path":str(path.relative_to(root)),"status":artifact["status"],"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
