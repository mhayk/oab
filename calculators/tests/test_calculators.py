"""Tests for the OAB calculators.

Three kinds of test, in order of importance:

1. **Worked examples.** Each calculator reproduces the numbers published in the design
   documents. If a formula changes, the documented example fails, so the docs cannot
   silently drift from the implementation.
2. **Properties.** Relationships that must hold for any input — peak is never below
   average, doubling writes doubles storage growth, units are consistent. These catch
   whole classes of error that example-based tests miss.
3. **Edges and errors.** Zero, fractional, very large, and invalid input. A calculator
   that returns a plausible number for nonsense input is worse than one that raises.
"""

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oab_calc import bandwidth, cache, concurrency, connections, cost, queue, rps, storage
from oab_calc.result import round_sig

ALL_MODULES = [rps, storage, bandwidth, concurrency, connections, cache, queue, cost]


# --------------------------------------------------------------------------- envelope

def test_round_sig_never_invents_precision():
    assert round_sig(0.027777, 2) == 0.028
    assert round_sig(1234, 2) == 1200
    assert round_sig(0, 2) == 0
    assert round_sig(-0.027777, 2) == -0.028


def test_confidence_propagates_from_the_weakest_input():
    """A chain containing a low-confidence input cannot report high confidence."""
    result = rps.calculate(users=100, dau_share=0.3, sessions_per_day=2,
                           requests_per_session=40, peak_factor=10)
    assert any(a.confidence == "low" for a in result.assumptions)
    assert result.confidence == "low"

    # A measured request count with an assumed peak factor is still only medium:
    # the weakest link governs, and the default peak factor is a guess about shape.
    partly = rps.calculate(requests_per_day=2400, measured=True)
    assert partly.confidence == "medium"

    fully = rps.calculate(requests_per_day=2400, peak_factor=4, measured=True)
    assert fully.confidence == "high"


def test_every_calculator_emits_the_full_envelope():
    results = [
        rps.calculate(requests_per_day=2400),
        storage.calculate(writes_per_day=360, avg_record_bytes=2048),
        bandwidth.calculate(rps=0.028, avg_payload_bytes=30720),
        concurrency.calculate(arrival_rate=208, service_time_ms=80),
        connections.calculate(query_rate=312, query_time_ms=4, instances=6),
        cache.calculate(hot_keys=50000, avg_value_bytes=8192, read_rate=187),
        queue.calculate(arrival_rate=2.3, service_time_ms=800),
        cost.calculate(item=["app:1:10"], complexity_points=4),
    ]
    for result in results:
        data = result.to_dict()
        for field in ("calculator", "assumptions", "formula", "calculation",
                      "result", "confidence"):
            assert field in data, f"{result.calculator} is missing {field}"
        assert data["assumptions"], f"{result.calculator} has no assumptions"
        assert data["result"]["unit"], f"{result.calculator} has no unit"
        assert result.to_text().startswith(result.calculator)
        json.dumps(data)  # must be serialisable


# ------------------------------------------------------------------- worked examples

def test_tiny_startup_rps_matches_the_documented_example():
    """docs/design/08: 100 users, 30% DAU, 2 sessions, 40 requests, 10x peak -> 0.28 RPS."""
    result = rps.calculate(users=100, dau_share=0.3, sessions_per_day=2,
                           requests_per_session=40, peak_factor=10)
    assert result.rounded == 0.28
    assert result.unit == "requests/second"
    # The strongest finding: the conclusion holds across the whole plausible range.
    assert result.sensitivity.decision_is_insensitive is True


def test_medium_saas_rps_matches_the_documented_example():
    """docs/design/08: 25k DAU, 3 sessions, 60 requests, 4x peak -> 52 avg, 208 peak."""
    result = rps.calculate(users=100_000, dau_share=0.25, sessions_per_day=3,
                           requests_per_session=60, peak_factor=4)
    assert round(result.value) == 208
    assert result.sensitivity.decision_is_insensitive is False


def test_medium_saas_concurrency_matches_the_documented_example():
    """208 RPS x 80 ms -> 16.6 in-flight requests."""
    result = concurrency.calculate(arrival_rate=208, service_time_ms=80)
    assert result.rounded == pytest.approx(17, rel=0.05)


def test_medium_saas_connections_reject_a_pooler():
    """312 q/s x 4 ms -> 1.25 concurrent; a pooler is not justified."""
    result = connections.calculate(query_rate=312, query_time_ms=4, instances=6,
                                   max_connections=100)
    assert "NOT justified" in " ".join(result.notes)
    assert result.value < 100


def test_medium_saas_workers_match_the_documented_example():
    """2.3 jobs/s x 0.8 s / 0.7 -> 3 workers."""
    result = queue.calculate(arrival_rate=2.3, service_time_ms=800, target_utilisation=0.7)
    assert result.value == 3


def test_tiny_startup_storage_matches_the_documented_example():
    """360 writes/day x 2 KB x 2.5 -> about 0.66 GB/year."""
    result = storage.calculate(writes_per_day=360, avg_record_bytes=2048, index_overhead=2.5)
    assert result.value == pytest.approx(0.63, rel=0.1)


def test_large_scale_egress_shows_the_cdn_saving():
    """docs/design/08: ~1 PB/month; edge offload is the largest single cost lever."""
    result = bandwidth.calculate(rps=50_000, avg_payload_bytes=8192,
                                 price_per_gb=0.05, cdn_offload=0.85,
                                 cdn_price_per_gb=0.01, currency="USD")
    assert result.value == pytest.approx(1_000_000, rel=0.15)  # GB/month
    assert "saving" in " ".join(result.notes)


def test_operational_cost_can_exceed_infrastructure():
    """The reframing that decides most small-system architecture choices."""
    result = cost.calculate(item=["app:1:10", "database:1:15"], complexity_points=4)
    assert result.value == pytest.approx(25 + 4 * 4 * 60)
    assert any("exceeds the infrastructure line" in n for n in result.notes)


# ------------------------------------------------------------------------- properties

@pytest.mark.parametrize("peak_factor", [1, 1.5, 4, 10, 50])
def test_peak_is_never_below_average(peak_factor):
    result = rps.calculate(requests_per_day=100_000, peak_factor=peak_factor)
    average = 100_000 / 86_400
    assert result.value >= average - 1e-9


def test_storage_scales_linearly_with_writes():
    one = storage.calculate(writes_per_day=1000, avg_record_bytes=500)
    two = storage.calculate(writes_per_day=2000, avg_record_bytes=500)
    assert two.value == pytest.approx(one.value * 2)


def test_bandwidth_scales_linearly_with_payload():
    small = bandwidth.calculate(rps=100, avg_payload_bytes=1000)
    large = bandwidth.calculate(rps=100, avg_payload_bytes=4000)
    assert large.value == pytest.approx(small.value * 4)


def test_littles_law_is_unit_consistent():
    """1000 ms is 1 s: 10 arrivals/second x 1 s must be 10 concurrent."""
    assert concurrency.calculate(arrival_rate=10, service_time_ms=1000).value == pytest.approx(10)
    assert concurrency.calculate(arrival_rate=10, service_time_ms=100).value == pytest.approx(1)


def test_workers_increase_monotonically_with_load():
    previous = 0
    for arrival in (1, 10, 100, 1000):
        workers = queue.calculate(arrival_rate=arrival, service_time_ms=500).value
        assert workers >= previous
        previous = workers


def test_lower_target_utilisation_provisions_more():
    tight = queue.calculate(arrival_rate=10, service_time_ms=500, target_utilisation=0.9)
    loose = queue.calculate(arrival_rate=10, service_time_ms=500, target_utilisation=0.5)
    assert loose.value > tight.value


def test_higher_hit_rate_relieves_more_load():
    low = cache.calculate(hot_keys=1000, avg_value_bytes=1000, read_rate=100, hit_rate=0.5)
    high = cache.calculate(hot_keys=1000, avg_value_bytes=1000, read_rate=100, hit_rate=0.95)
    assert "47.5" in " ".join(low.notes) or "50" in " ".join(low.notes)
    assert "95" in " ".join(high.notes)


def test_cache_flags_a_marginal_benefit():
    """A cache that relieves a small share of origin load must say so rather than
    presenting itself as a win."""
    result = cache.calculate(hot_keys=1000, avg_value_bytes=1000, read_rate=10,
                             hit_rate=0.9, origin_query_rate=1000)
    assert any("marginal" in n for n in result.notes)


# ----------------------------------------------------------------------- edges/errors

def test_zero_traffic_does_not_divide_by_zero():
    assert rps.calculate(requests_per_day=0).value == 0
    assert storage.calculate(writes_per_day=0, avg_record_bytes=1000).value == 0
    assert bandwidth.calculate(rps=0, avg_payload_bytes=1000).value == 0


def test_fractional_rps_is_preserved_not_rounded_to_zero():
    result = rps.calculate(requests_per_day=1)
    assert 0 < result.rounded < 0.001


def test_very_large_inputs_stay_finite():
    result = storage.calculate(writes_per_day=1e9, avg_record_bytes=1e4)
    assert math.isfinite(result.value)
    assert result.value > 0


def test_queue_reports_never_drains_rather_than_a_negative_number():
    """Capacity below arrival is an outage with a delay on it, not a negative duration."""
    result = queue.calculate(arrival_rate=100, service_time_ms=1000,
                             target_utilisation=1.0, backlog=1000)
    text = " ".join(result.notes)
    assert "NEVER DRAINS" in text or "Drains in" in text
    assert "-" not in text.split("Drains in")[-1][:20] if "Drains in" in text else True


@pytest.mark.parametrize("kwargs,module", [
    ({"requests_per_day": -1}, rps),
    ({"requests_per_day": 100, "peak_factor": 0}, rps),
    ({"users": 100, "dau_share": 1.5, "sessions_per_day": 1, "requests_per_session": 1}, rps),
    ({"writes_per_day": 10, "avg_record_bytes": 10, "index_overhead": 0.5}, storage),
    ({"rps": 10, "avg_payload_bytes": 10, "cdn_offload": 1.0}, bandwidth),
    ({"arrival_rate": 10, "service_time_ms": 0}, concurrency),
    ({"arrival_rate": 10, "service_time_ms": 10, "target_utilisation": 0}, concurrency),
    ({"query_rate": 10, "query_time_ms": 10, "instances": 0}, connections),
    ({"hot_keys": 10, "avg_value_bytes": 10, "hit_rate": 1.0}, cache),
    ({"arrival_rate": 10, "service_time_ms": -5}, queue),
])
def test_invalid_input_raises_rather_than_returning_a_plausible_number(kwargs, module):
    with pytest.raises(ValueError):
        module.calculate(**kwargs)


def test_rps_requires_enough_inputs_and_says_which_are_missing():
    with pytest.raises(ValueError) as exc:
        rps.calculate(users=100)
    message = str(exc.value)
    assert "dau_share" in message and "sessions_per_day" in message


def test_cost_rejects_a_malformed_item():
    with pytest.raises(ValueError):
        cost.calculate(item=["app:2"])
    with pytest.raises(ValueError):
        cost.calculate(item=["app:two:20"])


# ------------------------------------------------------------------------------- CLI

def test_cli_emits_valid_json(capsys):
    from oab_calc.__main__ import main
    assert main(["rps", "--requests-per-day=2400", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["calculator"] == "rps"
    assert data["result"]["unit"] == "requests/second"


def test_cli_rejects_an_unknown_calculator(capsys):
    from oab_calc.__main__ import main
    assert main(["nonexistent"]) == 2


def test_cli_reports_a_calculation_error_without_a_traceback(capsys):
    from oab_calc.__main__ import main
    assert main(["rps", "--requests-per-day=-5"]) == 1
    assert "error:" in capsys.readouterr().err


def test_every_registered_calculator_is_importable_and_wired():
    from oab_calc.__main__ import CALCULATORS
    assert len(CALCULATORS) == len(ALL_MODULES)
    for name, (module, summary, question) in CALCULATORS.items():
        assert hasattr(module, "calculate"), f"{name} has no calculate()"
        assert hasattr(module, "add_arguments"), f"{name} has no add_arguments()"
        assert summary and question
