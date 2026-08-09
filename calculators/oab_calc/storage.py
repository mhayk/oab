"""Storage growth per day and per year.

Answers "when do we outgrow the disk, the plan, or the backup window". The number that
matters is rarely today's size; it is the slope.

    bytes_per_day  = writes_per_day * avg_record_bytes * index_overhead
    bytes_per_year = bytes_per_day * 365

Index overhead is the multiplier that turns row size into stored size: indexes, tuple
headers, page fill factor, and dead-tuple slack before vacuum. 2.5 is a reasonable
default for an indexed relational table and is deliberately conservative — under-estimating
storage produces a capacity surprise, over-estimating produces a slightly larger disk.
"""

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity

GB = 1024 ** 3
DEFAULT_INDEX_OVERHEAD = 2.5


def add_arguments(parser):
    parser.add_argument("--writes-per-day", type=float, required=True,
                        help="rows or documents written per day (inserts, not updates)")
    parser.add_argument("--avg-record-bytes", type=float, required=True)
    parser.add_argument("--index-overhead", type=float, default=DEFAULT_INDEX_OVERHEAD,
                        help=f"stored bytes per logical byte (default {DEFAULT_INDEX_OVERHEAD})")
    parser.add_argument("--retention-days", type=float,
                        help="if set, storage plateaus at this retention rather than growing")
    parser.add_argument("--measured", action="store_true")


def calculate(writes_per_day, avg_record_bytes, index_overhead=DEFAULT_INDEX_OVERHEAD,
              retention_days=None, measured=False):
    if writes_per_day < 0 or avg_record_bytes < 0:
        raise ValueError("writes_per_day and avg_record_bytes cannot be negative")
    if index_overhead < 1:
        raise ValueError("index_overhead is a multiplier of at least 1")

    source = "observed" if measured else "assumed"
    confidence = "high" if measured else "medium"

    per_day = writes_per_day * avg_record_bytes * index_overhead
    per_year = per_day * 365

    assumptions = [
        Assumption("writes per day", writes_per_day, source="stated", confidence=confidence,
                   unit="rows", impact_if_wrong="proportional"),
        Assumption("average record size", avg_record_bytes, source=source,
                   confidence=confidence, unit="bytes", impact_if_wrong="proportional"),
        Assumption("index and page overhead", index_overhead, source="assumed",
                   confidence="medium", unit="x",
                   impact_if_wrong="proportional; measure with a table size query"),
    ]

    notes = []
    if retention_days:
        plateau = per_day * retention_days
        assumptions.append(Assumption("retention", retention_days, source="stated",
                                      confidence="high", unit="days"))
        notes.append(
            f"With {retention_days:g}-day retention, storage plateaus at "
            f"{plateau / GB:.3g} GB rather than growing indefinitely."
        )

    notes.append("Counts inserts only. Updates consume space until vacuum or compaction "
                 "reclaims it, which is a performance concern rather than a growth one.")

    return CalcResult(
        calculator="storage",
        assumptions=assumptions,
        formula=("bytes_per_day = writes_per_day * avg_record_bytes * index_overhead ; "
                 "bytes_per_year = bytes_per_day * 365"),
        calculation=(f"bytes_per_day = {writes_per_day:,.0f} x {avg_record_bytes:,.0f} x "
                     f"{index_overhead:g} = {per_day:,.0f} bytes ({per_day / GB:.3g} GB) ; "
                     f"bytes_per_year = {per_day / GB:.3g} GB x 365 = {per_year / GB:.3g} GB"),
        value=per_year / GB,
        unit="GB/year",
        safety_margin=SafetyMargin(
            index_overhead,
            "Index and page overhead multiplier. Verify against actual table sizes once "
            "there is production data."
        ),
        sensitivity=Sensitivity(
            "average record size",
            "Storage scales linearly with it, and estimates are routinely out by 2x "
            "because blob and text columns are forgotten.",
        ),
        notes=notes,
    ).with_range(per_year / GB / 2, per_year / GB * 2)
