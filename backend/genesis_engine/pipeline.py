"""End-to-end Genesis pipeline: spec -> assets -> math -> verify -> compose -> package."""
from __future__ import annotations
import json, tempfile, uuid
from pathlib import Path
from typing import Any, Dict
from .assets import build_assets
from .audio import build_audio_manifest
from .build import package
from .compliance import build_verification_artifact
from .composer import compose_web
from .logic import verify_math

class GenesisPipeline:
    def run(self, spec: Any, include_audio: bool=True, include_vision: bool=True, include_build: bool=True) -> Dict[str,Any]:
        job_id=f"genesis_{uuid.uuid4().hex}"
        root=Path(tempfile.gettempdir())/job_id; root.mkdir(parents=True,exist_ok=True)
        verification=verify_math(spec)
        assets=build_assets(spec,root) if include_vision else []
        audio=build_audio_manifest(spec) if include_audio else []
        manifest={"job_id":job_id,"spec":spec.model_dump(),"assets":assets,"audio":audio,"logic":verification}
        composed=compose_web(spec,verification,assets,audio,root)
        verification_artifact=build_verification_artifact(spec,verification,manifest,root)
        built=package(spec,root) if include_build else {"status":"skipped"}
        artifacts=[verification_artifact,{"type":"playable","path":composed["entrypoint"],"status":composed["status"]}]
        if built.get("web_zip"): artifacts.append({"type":"build","path":built["web_zip"],"status":built["status"]})
        return {"job_id":job_id,"status":"complete","manifest":manifest|{"composer":composed},"verification":verification,"artifacts":artifacts,"workspace":str(root),"build":built}
