"""Cache working set, and what the cache actually saves.

Caches are added reflexively. This calculator makes the benefit explicit in absolute
terms, because "improves read performance" and "removes 4 queries/second from a database
doing 300" are very different justifications, and only the second one is checkable.

    working_set_bytes = hot_keys * avg_value_bytes * overhead
    origin_reads      = read_rate * (1 - hit_rate)
    relieved          = read_rate - origin_reads
"""

from .result import Assumption, CalcResult, Sensitivity

MB = 1024 ** 2
DEFAULT_OVERHEAD = 1.3  # key storage, per-entry metadata, allocator slack, replication headroom


def add_arguments(parser):
    parser.add_argument("--hot-keys", type=float, required=True,
                        help="number of distinct keys in the working set")
    parser.add_argument("--avg-value-bytes", type=float, required=True)
    parser.add_argument("--read-rate", type=float,
                        help="reads per second against the cached data")
    parser.add_argument("--hit-rate", type=float, default=0.9,
                        help="expected hit rate, e.g. 0.9")
    parser.add_argument("--origin-query-rate", type=float,
                        help="total queries/second the origin handles, for context")
    parser.add_argument("--overhead", type=float, default=DEFAULT_OVERHEAD)


def calculate(hot_keys, avg_value_bytes, read_rate=None, hit_rate=0.9,
              origin_query_rate=None, overhead=DEFAULT_OVERHEAD):
    if hot_keys < 0 or avg_value_bytes < 0:
        raise ValueError("hot_keys and avg_value_bytes cannot be negative")
    if not 0 < hit_rate < 1:
        raise ValueError("hit_rate must be between 0 and 1 (exclusive)")
    if overhead < 1:
        raise ValueError("overhead is a multiplier of at least 1")

    working_set = hot_keys * avg_value_bytes * overhead

    assumptions = [
        Assumption("hot keys", hot_keys, source="assumed", confidence="low", unit="keys",
                   impact_if_wrong="proportional — the dominant uncertainty"),
        Assumption("average value size", avg_value_bytes, source="assumed",
                   confidence="medium", unit="bytes", impact_if_wrong="proportional"),
        Assumption("per-entry overhead", overhead, source="assumed", confidence="medium",
                   unit="x"),
    ]

    notes = []
    if read_rate is not None:
        origin_reads = read_rate * (1 - hit_rate)
        relieved = read_rate - origin_reads
        assumptions += [
            Assumption("read rate", read_rate, source="calculated", confidence="medium",
                       unit="reads/second"),
            Assumption("hit rate", hit_rate, source="assumed", confidence="low",
                       unit="fraction",
                       impact_if_wrong="strongly non-linear on origin load below 0.8"),
        ]
        notes.append(
            f"At a {hit_rate:.0%} hit rate the cache relieves {relieved:.3g} reads/second, "
            f"leaving {origin_reads:.3g} reads/second at the origin."
        )
        if origin_query_rate:
            share = relieved / origin_query_rate
            notes.append(
                f"That is {share:.0%} of the origin's {origin_query_rate:.3g} queries/second. "
                + ("The benefit is material." if share > 0.3 else
                   "The benefit is marginal — justify this cache on something other than "
                   "load relief, such as shared state across instances, or do not add it.")
            )

    notes.append(
        "A cache in front of a healthy database is a component with its own failure modes. "
        "Define what happens when it is empty, stale, or unavailable before adding it."
    )

    return CalcResult(
        calculator="cache",
        assumptions=assumptions,
        formula="working_set = hot_keys * avg_value_bytes * overhead",
        calculation=(f"working_set = {hot_keys:,.0f} x {avg_value_bytes:,.0f} x {overhead:g} "
                     f"= {working_set:,.0f} bytes ({working_set / MB:.3g} MB)"),
        value=working_set / MB,
        unit="MB",
        sensitivity=Sensitivity(
            "hot keys",
            "The working set is usually estimated from intuition and is routinely out by an "
            "order of magnitude. Measure distinct key access over a representative window.",
        ),
        notes=notes,
    ).with_range(working_set / MB / 3, working_set / MB * 3)
