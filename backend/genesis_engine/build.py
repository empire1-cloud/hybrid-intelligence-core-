"""Build/package artifacts with no required external build toolchain for web."""
from __future__ import annotations
import shutil, zipfile
from pathlib import Path
from typing import Any, Dict

def package(spec: Any, root: Path) -> Dict[str, Any]:
    dist=root/"dist"; dist.mkdir(parents=True,exist_ok=True)
    archive=dist/(spec.name.replace(" ","_").lower()+"_web.zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for p in (root/"web").rglob("*"):
            if p.is_file(): z.write(p,p.relative_to(root))
        if (root/"verification.json").exists(): z.write(root/"verification.json","verification.json")
    tools={"web":True,"android_gradle":shutil.which("gradle") is not None,"cocos2dx":shutil.which("cocos") is not None}
    return {"status":"packaged","web_zip":str(archive.relative_to(root)),"toolchain":tools,"notes":"APK/Cocos build requires the corresponding native toolchain; this package is the portable web artifact."}
