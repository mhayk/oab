"""Database connection pool sizing, and whether a connection pooler is justified yet.

A pooler is a component with real operational cost, and it is routinely added before it
solves anything. The arithmetic usually says no:

    concurrent_queries = query_rate * query_time_seconds        (Little's Law)
    pool_per_instance  = ceil(concurrent_queries / instances * safety)
    total_connections  = instances * pool_per_instance

If total_connections stays comfortably below the server's limit, a pooler adds a hop, a
process to operate, and a new failure mode in exchange for nothing.
"""

from math import ceil

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity

POOLER_THRESHOLD = 0.8


def add_arguments(parser):
    parser.add_argument("--query-rate", type=float, required=True,
                        help="database queries per second across the whole fleet")
    parser.add_argument("--query-time-ms", type=float, required=True)
    parser.add_argument("--instances", type=int, default=1,
                        help="application instances sharing the database")
    parser.add_argument("--max-connections", type=int, default=100,
                        help="server connection limit (default 100)")
    parser.add_argument("--safety", type=float, default=4.0,
                        help="multiplier over mean concurrency to absorb the tail (default 4)")
    parser.add_argument("--min-pool", type=int, default=5,
                        help="practical floor per instance (default 5)")
    parser.add_argument("--measured", action="store_true")


def calculate(query_rate, query_time_ms, instances=1, max_connections=100,
              safety=4.0, min_pool=5, measured=False):
    if instances < 1:
        raise ValueError("instances must be at least 1")
    if query_time_ms <= 0:
        raise ValueError("query_time_ms must be positive")
    if max_connections < 1:
        raise ValueError("max_connections must be at least 1")

    confidence = "high" if measured else "medium"
    source = "observed" if measured else "assumed"

    concurrent = query_rate * (query_time_ms / 1000)
    # Little's Law gives the MEAN. A pool sized to the mean queues on connection
    # acquisition during any burst, so a practical floor applies: the arithmetic tells you
    # when a pool is too small, not that a pool of one is ever a real configuration.
    computed = ceil(concurrent / instances * safety)
    per_instance = max(min_pool, computed)
    floor_applied = per_instance > computed
    total = instances * per_instance
    utilisation = total / max_connections

    if utilisation >= POOLER_THRESHOLD:
        verdict = (
            f"A connection pooler IS justified: {total} connections is "
            f"{utilisation:.0%} of the {max_connections} limit, at or above the "
            f"{POOLER_THRESHOLD:.0%} threshold."
        )
    else:
        verdict = (
            f"A connection pooler is NOT justified yet: {total} connections is "
            f"{utilisation:.0%} of the {max_connections} limit. Measured mean concurrency "
            f"is {concurrent:.3g} queries. Revisit above {POOLER_THRESHOLD:.0%}."
        )

    return CalcResult(
        calculator="connections",
        assumptions=[
            Assumption("query rate", query_rate, source="calculated", confidence=confidence,
                       unit="queries/second"),
            Assumption("average query time", query_time_ms, source=source,
                       confidence=confidence, unit="milliseconds",
                       impact_if_wrong="proportional"),
            Assumption("application instances", instances, source="stated",
                       confidence="high", unit="instances"),
            Assumption("server connection limit", max_connections, source="stated",
                       confidence="high", unit="connections"),
            Assumption("tail safety multiplier", safety, source="assumed", confidence="medium",
                       unit="x", impact_if_wrong="proportional on pool size"),
            Assumption("practical pool floor per instance", min_pool, source="assumed",
                       confidence="medium", unit="connections"),
        ],
        formula=("concurrent = query_rate * query_time_s ; "
                 "pool_per_instance = max(min_pool, ceil(concurrent / instances * safety)) ; "
                 "total = instances * pool_per_instance"),
        calculation=(f"concurrent = {query_rate:.4g} x {query_time_ms / 1000:.4g} = "
                     f"{concurrent:.3g} ; pool_per_instance = ceil({concurrent:.3g} / "
                     f"{instances} x {safety:g}) = {computed} ; "
                     f"pool_per_instance = max({min_pool}, {computed}) = {per_instance} ; "
                     f"total = {instances} x {per_instance} = {total}"),
        value=total,
        unit="connections",
        safety_margin=SafetyMargin(
            safety,
            "Mean concurrency understates peak demand; the multiplier absorbs the tail. "
            "Size against observed p99 query time where it is available.",
        ),
        sensitivity=Sensitivity(
            "average query time",
            "A single slow query class raises the mean and inflates the pool. Check the "
            "distribution before enlarging the pool — a slow query is usually the real problem.",
        ),
        notes=[verdict,
               f"Recommended pool size per instance: {per_instance}."
               + (f" Demand alone implies {computed}; the floor of {min_pool} applies because "
                  f"a pool sized to the mean queues on connection acquisition during any burst."
                  if floor_applied else ""),
               "Idle connections are not free: each one costs memory on the server."],
    )
