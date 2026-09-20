"""Deterministic audio asset generator using only the Python standard library."""
from __future__ import annotations
import math, struct, wave
from pathlib import Path
from typing import Any, Dict, List

def _tone(path: Path, frequency: float, duration: float=0.18, sample_rate: int=22050) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames=int(duration*sample_rate)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sample_rate)
        data=bytearray()
        for i in range(frames):
            env=max(0.0,1.0-i/frames)
            sample=int(12000*env*math.sin(2*math.pi*frequency*i/sample_rate))
            data.extend(struct.pack("<h",sample))
        w.writeframes(bytes(data))

def build_audio_manifest(spec: Any, root: Path) -> List[Dict[str, Any]]:
    definitions={"shot":440,"hit":660,"big_win":880,"boss_hit":220,"background":110}
    assets=[]
    for name,freq in definitions.items():
        path=root/"audio"/f"{name}.wav"
        _tone(path,freq,0.55 if name=="background" else 0.18)
        assets.append({"id":f"audio_{name}","name":name,"format":"wav","path":str(path.relative_to(root)),"status":"generated","frequency_hz":freq})
    return assets
