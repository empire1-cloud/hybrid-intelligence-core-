from routers.empire_intake import EmpireSignalRequest, classify_empire_signal


def test_vocal_architecture_maps_to_lyrica_inside_empire1() -> None:
    result = classify_empire_signal(
        EmpireSignalRequest(
            title="Vocal Architectures",
            summary="A singing and expressive vocal control architecture for creators.",
            source_type="research",
        )
    )
    assert result.empire_parent == "Empire-1"
    assert result.primary_lane.startswith("Lyrica 3")
    assert "Soulfire" in result.supporting_lanes
    assert result.new_universe_allowed is False
    assert result.new_repository_allowed is False


def test_payment_signal_maps_to_archisynapse() -> None:
    result = classify_empire_signal(
        EmpireSignalRequest(
            title="Agent payment authorization",
            summary="Control AI spend, reconciliation, refunds, and signed receipts.",
            source_type="product",
        )
    )
    assert result.status == "READY_FOR_EXECUTION"
    assert result.primary_lane.startswith("Archisynapse")
    assert "paid pilot" in result.revenue_path


def test_game_mechanics_map_to_southern_and_sla113() -> None:
    result = classify_empire_signal(
        EmpireSignalRequest(
            title="Arcade mechanic inspector",
            summary="Study game mechanics and convert them into an original operator system.",
            source_type="feature",
        )
    )
    assert result.primary_lane.startswith("Southern Lifestyle")
    assert "SLA113" in result.supporting_lanes


def test_unknown_signal_fails_closed_to_founder_placement() -> None:
    result = classify_empire_signal(
        EmpireSignalRequest(
            title="Unclassified signal",
            summary="A completely novel object with no known product vocabulary.",
            source_type="other",
        )
    )
    assert result.status == "NEEDS_FOUNDER_PLACEMENT"
    assert result.primary_lane.startswith("Empire-1 HIC")
    assert result.decision == "EVOLVE_EXISTING"
