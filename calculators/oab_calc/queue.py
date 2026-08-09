"""Worker count, and how long a backlog takes to drain.

Drain time is the number teams skip, and it is the one that matters during an incident:
a queue that never drains is an outage with a delay on it.

    workers    = ceil(arrival_rate * service_time_s / target_utilisation)
    capacity   = workers / service_time_s
    drain_time = backlog / (capacity - arrival_rate)     when capacity > arrival_rate
"""

from math import ceil

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity


def add_arguments(parser):
    parser.add_argument("--arrival-rate", type=float, required=True, help="jobs per second")
    parser.add_argument("--service-time-ms", type=float, required=True,
                        help="average job duration, in MILLISECONDS")
    parser.add_argument("--target-utilisation", type=float, default=0.7)
    parser.add_argument("--backlog", type=float,
                        help="jobs queued after a spike, to compute drain time")
    parser.add_argument("--spike-multiplier", type=float, default=10.0,
                        help="arrival multiple during a spike, for the drain scenario")
    parser.add_argument("--measured", action="store_true")


def calculate(arrival_rate, service_time_ms, target_utilisation=0.7, backlog=None,
              spike_multiplier=10.0, measured=False):
    if arrival_rate < 0:
        raise ValueError("arrival_rate cannot be negative")
    if service_time_ms <= 0:
        raise ValueError("service_time_ms must be positive")
    if not 0 < target_utilisation <= 1:
        raise ValueError("target_utilisation must be between 0 and 1")

    source = "observed" if measured else "assumed"
    confidence = "high" if measured else "medium"

    service_time_s = service_time_ms / 1000
    workers = max(1, ceil(arrival_rate * service_time_s / target_utilisation))
    capacity = workers / service_time_s
    headroom = capacity - arrival_rate

    notes = [f"Capacity with {workers} worker(s): {capacity:.3g} jobs/second "
             f"against {arrival_rate:.3g} arriving."]

    if backlog is None:
        # Default scenario: a spike lasting 60 seconds at spike_multiplier.
        backlog = arrival_rate * (spike_multiplier - 1) * 60
        notes.append(f"Backlog scenario: a {spike_multiplier:g}x spike for 60 seconds "
                     f"leaves {backlog:,.0f} jobs queued.")

    if headroom <= 0:
        drain_text = ("NEVER DRAINS — capacity does not exceed the arrival rate. "
                      "The queue grows without bound; this is an outage with a delay on it.")
        drain_seconds = float("inf")
    else:
        drain_seconds = backlog / headroom
        drain_text = (f"Drains in {drain_seconds:,.0f} seconds "
                      f"({drain_seconds / 60:.3g} minutes) at {workers} worker(s).")
    notes.append(drain_text)

    return CalcResult(
        calculator="queue",
        assumptions=[
            Assumption("arrival rate", arrival_rate, source="calculated",
                       confidence=confidence, unit="jobs/second"),
            Assumption("average job duration", service_time_ms, source=source,
                       confidence=confidence, unit="milliseconds",
                       impact_if_wrong="proportional on worker count"),
            Assumption("target utilisation", target_utilisation, source="assumed",
                       confidence="high", unit="fraction"),
            Assumption("backlog", backlog, source="assumed", confidence="low", unit="jobs"),
        ],
        formula=("workers = ceil(arrival_rate * service_time_s / target_utilisation) ; "
                 "drain_time = backlog / (capacity - arrival_rate)"),
        calculation=(f"workers = ceil({arrival_rate:.4g} x {service_time_s:.4g} / "
                     f"{target_utilisation:g}) = {workers} ; "
                     f"capacity = {workers} / {service_time_s:.4g} = {capacity:.3g} ; "
                     + (f"drain = {backlog:,.0f} / ({capacity:.3g} - {arrival_rate:.3g}) = "
                        f"{drain_seconds:,.0f} s" if headroom > 0 else "drain = never")),
        value=workers,
        unit="workers",
        safety_margin=SafetyMargin(
            1 / target_utilisation,
            f"Sized for {target_utilisation:.0%} utilisation so queue depth stays bounded. "
            f"At utilisation near 1, waiting time grows without limit.",
        ),
        sensitivity=Sensitivity(
            "average job duration",
            "Worker count scales linearly with it, and job duration distributions are usually "
            "long-tailed — one slow job class can consume the whole pool. Consider separating "
            "job classes into their own queues before adding workers.",
        ),
        notes=notes,
    )
