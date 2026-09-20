from pathlib import Path
from genesis_engine.logic import verify_math
from genesis_engine.models import GameSpec
from genesis_engine.pipeline import GenesisPipeline

def test_deterministic_math_repeats():
    spec=GameSpec(seed=113,shots_per_round=1000)
    a=verify_math(spec); b=verify_math(spec)
    assert a==b
    assert a["proof_hash"]

def test_math_flags_target_mismatch():
    spec=GameSpec(target_rtp=0.50,seed=113,shots_per_round=1000)
    assert verify_math(spec)["verification_status"]=="review_required"

def test_pipeline_creates_playable_bundle():
    result=GenesisPipeline().run(GameSpec(name="Test Genesis",seed=113,shots_per_round=1000))
    assert result["status"]=="complete"
    assert result["manifest"]["composer"]["status"]=="playable"
    root=Path(result["workspace"])
    assert (root/"web"/"index.html").exists()
    assert (root/"verification.json").exists()
    assert Path(result["workspace"])/result["build"]["web_zip"]
