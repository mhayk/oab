"""Concurrent operations, via Little's Law.

    L = lambda * W

    L      concurrent operations in the system
    lambda arrival rate (requests/second)
    W      average time each spends in the system (seconds)

The law holds for any stable system regardless of arrival distribution or service order,
which is why it is the right tool for sizing in-flight requests, worker pools, and
connection pools without simulating anything.

The usual mistake is mixing units — milliseconds against requests/second — which produces
an answer 1000x wrong that still looks plausible. This module takes milliseconds
explicitly and converts, rather than accepting an ambiguous "time" argument.
"""

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity


def add_arguments(parser):
    parser.add_argument("--arrival-rate", type=float, required=True,
                        help="operations per second")
    parser.add_argument("--service-time-ms", type=float, required=True,
                        help="average time in the system, in MILLISECONDS")
    parser.add_argument("--target-utilisation", type=float, default=0.7,
                        help="utilisation to size for (default 0.7)")
    parser.add_argument("--measured", action="store_true")


def calculate(arrival_rate, service_time_ms, target_utilisation=0.7, measured=False):
    if arrival_rate < 0:
        raise ValueError("arrival_rate cannot be negative")
    if service_time_ms <= 0:
        raise ValueError("service_time_ms must be positive")
    if not 0 < target_utilisation <= 1:
        raise ValueError("target_utilisation must be between 0 and 1")

    source = "observed" if measured else "assumed"
    confidence = "high" if measured else "medium"

    service_time_s = service_time_ms / 1000
    concurrent = arrival_rate * service_time_s
    provisioned = concurrent / target_utilisation

    return CalcResult(
        calculator="concurrency",
        assumptions=[
            Assumption("arrival rate", arrival_rate, source="calculated",
                       confidence=confidence, unit="operations/second"),
            Assumption("average service time", service_time_ms, source=source,
                       confidence=confidence, unit="milliseconds",
                       impact_if_wrong="proportional"),
            Assumption("target utilisation", target_utilisation, source="assumed",
                       confidence="high", unit="fraction",
                       impact_if_wrong="inverse — sizing at 0.9 halves the provisioned capacity"),
        ],
        formula="L = arrival_rate * service_time_seconds ; provisioned = L / target_utilisation",
        calculation=(f"L = {arrival_rate:.4g} x {service_time_s:.4g} = {concurrent:.3g} ; "
                     f"provisioned = {concurrent:.3g} / {target_utilisation:g} = "
                     f"{provisioned:.3g}"),
        value=concurrent,
        unit="concurrent operations",
        safety_margin=SafetyMargin(
            1 / target_utilisation,
            f"Sized for {target_utilisation:.0%} utilisation. Latency grows non-linearly as "
            f"utilisation approaches 1: at 0.9 it is roughly 10x service time, at 0.95 roughly 20x.",
        ),
        sensitivity=Sensitivity(
            "average service time",
            "Concurrency scales linearly with it, and the mean hides the tail — a p99 far "
            "above the mean means peak concurrency far above this figure.",
        ),
        notes=[
            f"Provision for {provisioned:.3g} to hold {target_utilisation:.0%} utilisation.",
            "Little's Law uses the MEAN. Size pools against the tail, not this number alone.",
        ],
    )
