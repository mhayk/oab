"""Average and peak requests per second.

The first calculation in almost every sizing conversation, and the one that most often
ends it: "high traffic" described in adjectives usually turns out to be a fraction of a
request per second, with four orders of magnitude of headroom on one instance.

    avg_rps  = requests_per_day / 86400
    peak_rps = avg_rps * peak_factor

Requests per day can be given directly, or derived:

    requests_per_day = users * dau_share * sessions_per_day * requests_per_session
"""

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity

SECONDS_PER_DAY = 86_400

# Typical peak factors, for when the caller has no measurement. These are ratios of peak
# to average, and they fall as traffic spreads across time zones — a global consumer
# service is far smoother than a single-country business tool.
PEAK_FACTOR_GUIDANCE = {
    "single-timezone consumer app (evening concentration)": 10,
    "single-timezone business tool (working hours)": 4,
    "multi-region service": 2,
    "global consumer service": 1.5,
}


def add_arguments(parser):
    parser.add_argument("--requests-per-day", type=float,
                        help="total requests per day, if known directly")
    parser.add_argument("--users", type=float, help="registered or total users")
    parser.add_argument("--dau-share", type=float,
                        help="fraction of users active daily, e.g. 0.3")
    parser.add_argument("--sessions-per-day", type=float,
                        help="sessions per active user per day")
    parser.add_argument("--requests-per-session", type=float)
    parser.add_argument("--peak-factor", type=float,
                        help="ratio of peak to average (default 4, a working-hours shape)")
    parser.add_argument("--measured", action="store_true",
                        help="inputs are measured rather than assumed")


def calculate(requests_per_day=None, users=None, dau_share=None, sessions_per_day=None,
              requests_per_session=None, peak_factor=None, measured=False):
    # Distinguishing an explicit peak factor from the default matters: with --measured, a
    # peak the caller actually observed is high confidence, while the fallback of 4 is a
    # guess about traffic shape and must not inherit that confidence.
    peak_factor_given = peak_factor is not None
    if peak_factor is None:
        peak_factor = 4.0
    if peak_factor <= 0:
        raise ValueError("peak_factor must be positive")

    source = "observed" if measured else "assumed"
    confidence = "high" if measured else "low"
    assumptions = []

    if requests_per_day is not None:
        if requests_per_day < 0:
            raise ValueError("requests_per_day cannot be negative")
        assumptions.append(Assumption("requests per day", requests_per_day,
                                      source="stated" if not measured else "observed",
                                      confidence="high" if measured else "medium",
                                      unit="requests"))
        derivation = f"{requests_per_day:,.0f}"
    else:
        missing = [n for n, v in (
            ("users", users), ("dau_share", dau_share),
            ("sessions_per_day", sessions_per_day),
            ("requests_per_session", requests_per_session)) if v is None]
        if missing:
            raise ValueError(
                "provide --requests-per-day, or all of --users, --dau-share, "
                f"--sessions-per-day and --requests-per-session (missing: {', '.join(missing)})"
            )
        if not 0 < dau_share <= 1:
            raise ValueError("dau_share must be between 0 and 1")

        requests_per_day = users * dau_share * sessions_per_day * requests_per_session
        assumptions += [
            Assumption("users", users, source="stated", confidence="high", unit="users"),
            Assumption("daily active share", dau_share, source=source, confidence=confidence,
                       impact_if_wrong="proportional — the dominant uncertainty"),
            Assumption("sessions per active user per day", sessions_per_day,
                       source=source, confidence=confidence, impact_if_wrong="proportional"),
            Assumption("requests per session", requests_per_session, source=source,
                       confidence="medium", impact_if_wrong="proportional"),
        ]
        derivation = (f"{users:,.0f} x {dau_share} x {sessions_per_day} x "
                      f"{requests_per_session} = {requests_per_day:,.0f}")

    peak_measured = measured and peak_factor_given
    assumptions.append(Assumption(
        "peak factor", peak_factor,
        source="observed" if peak_measured else source,
        confidence="high" if peak_measured else "medium",
        unit="x",
        impact_if_wrong="proportional on peak only"
        + ("" if peak_measured else "; the default of 4 assumes a working-hours shape")))

    avg = requests_per_day / SECONDS_PER_DAY
    peak = avg * peak_factor

    # Worst plausible case: everyone active, and a sharper peak than assumed. If the
    # architectural conclusion survives this, it survives every input in the range, and
    # that is a stronger finding than any single number.
    if dau_share is not None:
        upper_requests = users * 1.0 * sessions_per_day * requests_per_session
        upper_peak = (upper_requests / SECONDS_PER_DAY) * (peak_factor * 2)
        insensitive = upper_peak < 10
        explanation = (
            f"At 100% daily active users and a {peak_factor * 2:g}x peak factor the result is "
            f"{upper_peak:.2g} requests/second"
            + (". The recommendation does not change anywhere in the plausible input range."
               if insensitive else ", so the conclusion does depend on this input.")
        )
        sensitivity = Sensitivity("daily active share", explanation, insensitive)
    else:
        upper_peak = peak * 2
        sensitivity = Sensitivity(
            "peak factor",
            f"At a {peak_factor * 2:g}x peak factor the result is {upper_peak:.2g} "
            f"requests/second.",
            upper_peak < 10,
        )

    return CalcResult(
        calculator="rps",
        assumptions=assumptions,
        formula="avg_rps = requests_per_day / 86400 ; peak_rps = avg_rps * peak_factor",
        calculation=(f"requests_per_day = {derivation} ; "
                     f"avg_rps = {requests_per_day:,.0f} / 86400 = {avg:.3g} ; "
                     f"peak_rps = {avg:.3g} x {peak_factor:g} = {peak:.3g}"),
        value=peak,
        unit="requests/second",
        safety_margin=SafetyMargin(
            peak_factor,
            "Peak factor applied to average. Measure the real peak-to-average ratio "
            "before relying on this for provisioning."
        ),
        sensitivity=sensitivity,
        notes=[f"Average is {round(avg, 4):g} requests/second."],
    ).with_range(avg, upper_peak)
