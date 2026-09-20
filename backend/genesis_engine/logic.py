"""Deterministic game mathematics. No LLM is trusted for numeric truth.

The engine computes a weighted payout model from the supplied paytable.  A
fixed-seed Monte Carlo run is used as a secondary reproducibility check; it is
not presented as regulatory certification.
"""
from __future__ import annotations
import hashlib, json, math, random
from typing import Any, Dict


def _weights(paytable: Dict[str, float]) -> Dict[str, float]:
    # Canonical fish weights. Higher-value targets are less frequent.
    defaults = {"small": 0.70, "medium": 0.22, "large": 0.07, "boss": 0.01}
    raw = {k: defaults.get(k, 1.0 / max(1, len(paytable))) for k in paytable}
    total = sum(raw.values()) or 1.0
    return {k: v / total for k, v in raw.items()}


def verify_math(spec: Any) -> Dict[str, Any]:
    paytable = dict(spec.paytable)
    weights = _weights(paytable)
    theoretical_rtp = sum(weights[k] * float(v) for k, v in paytable.items())
    # RTP is normalized to one unit wager per resolved target event.
    seed_material = json.dumps({"paytable": paytable, "seed": spec.seed}, sort_keys=True)
    digest = hashlib.sha256(seed_material.encode()).hexdigest()
    seed = spec.seed if spec.seed is not None else int(digest[:16], 16)
    rng = random.Random(seed)
    rounds = int(spec.shots_per_round)
    payouts = []
    keys = list(paytable)
    cumulative = []
    acc = 0.0
    for k in keys:
        acc += weights[k]
        cumulative.append(acc)
    for _ in range(rounds):
        x = rng.random()
        idx = next(i for i, c in enumerate(cumulative) if x <= c)
        payouts.append(float(paytable[keys[idx]]))
    simulated_rtp = sum(payouts) / rounds
    mean = simulated_rtp
    variance = sum((p - mean) ** 2 for p in payouts) / rounds
    stddev = math.sqrt(variance)
    tolerance = max(0.01, 4.0 / math.sqrt(rounds))
    target_delta = abs(theoretical_rtp - float(spec.target_rtp))
    return {
        "model": "weighted_target_payout_v1",
        "theoretical_rtp": round(theoretical_rtp, 8),
        "theoretical_rtp_percent": round(theoretical_rtp * 100, 5),
        "target_rtp": float(spec.target_rtp),
        "target_rtp_percent": round(float(spec.target_rtp) * 100, 5),
        "target_delta": round(target_delta, 8),
        "simulation_rounds": rounds,
        "simulation_seed": seed,
        "simulated_rtp": round(simulated_rtp, 8),
        "simulated_rtp_percent": round(simulated_rtp * 100, 5),
        "simulation_stddev": round(stddev, 8),
        "simulation_within_tolerance": abs(simulated_rtp - theoretical_rtp) <= tolerance,
        "target_matches_model": target_delta <= 0.0025,
        "probabilities": weights,
        "verification_status": "verified" if target_delta <= 0.0025 and abs(simulated_rtp-theoretical_rtp) <= tolerance else "review_required",
        "proof_hash": hashlib.sha256(json.dumps({"weights":weights,"paytable":paytable,"rtp":theoretical_rtp}, sort_keys=True).encode()).hexdigest(),
    }
