"""Bandwidth and monthly egress.

Egress is routinely the largest and most surprising line on an infrastructure invoice, and
it is almost never computed during design. At scale it can exceed the entire compute bill,
which makes offload to an edge cache the single highest-value decision available — a
bandwidth arithmetic result, not an architectural fashion.

    bytes_per_second = rps * avg_payload_bytes
    egress_per_month = bytes_per_second * 2_592_000
    cost             = egress_gb * price_per_gb * (1 - cdn_offload) + cdn_gb * cdn_price
"""

from .result import Assumption, CalcResult, Sensitivity

GB = 1024 ** 3
SECONDS_PER_MONTH = 30 * 86_400


def add_arguments(parser):
    parser.add_argument("--rps", type=float, required=True,
                        help="average requests per second (not peak — egress is billed on volume)")
    parser.add_argument("--avg-payload-bytes", type=float, required=True)
    parser.add_argument("--price-per-gb", type=float,
                        help="origin egress price per GB, in your currency")
    parser.add_argument("--cdn-offload", type=float, default=0.0,
                        help="fraction served from the edge, e.g. 0.85")
    parser.add_argument("--cdn-price-per-gb", type=float, default=0.0)
    parser.add_argument("--currency", default="GBP")
    parser.add_argument("--measured", action="store_true")


def calculate(rps, avg_payload_bytes, price_per_gb=None, cdn_offload=0.0,
              cdn_price_per_gb=0.0, currency="GBP", measured=False):
    if rps < 0 or avg_payload_bytes < 0:
        raise ValueError("rps and avg_payload_bytes cannot be negative")
    if not 0 <= cdn_offload < 1:
        raise ValueError("cdn_offload must be between 0 and 1 (exclusive of 1)")

    source = "observed" if measured else "assumed"
    confidence = "high" if measured else "medium"

    bytes_per_second = rps * avg_payload_bytes
    mbps = bytes_per_second * 8 / 1e6
    monthly_gb = bytes_per_second * SECONDS_PER_MONTH / GB

    assumptions = [
        Assumption("average requests per second", rps, source="calculated",
                   confidence=confidence, unit="requests/second"),
        Assumption("average response payload", avg_payload_bytes, source=source,
                   confidence=confidence, unit="bytes",
                   impact_if_wrong="proportional — the dominant uncertainty"),
    ]

    notes = []
    if price_per_gb is not None:
        origin_gb = monthly_gb * (1 - cdn_offload)
        edge_gb = monthly_gb * cdn_offload
        total = origin_gb * price_per_gb + edge_gb * cdn_price_per_gb
        assumptions.append(Assumption("origin egress price", price_per_gb, source="stated",
                                      confidence="medium", unit=f"{currency}/GB"))
        if cdn_offload:
            assumptions.append(Assumption("edge offload", cdn_offload, source="assumed",
                                          confidence="medium", unit="fraction"))
            unoffloaded = monthly_gb * price_per_gb
            notes.append(
                f"Without edge offload this is {unoffloaded:,.0f} {currency}/month; "
                f"at {cdn_offload:.0%} offload it is {total:,.0f} {currency}/month, "
                f"saving {unoffloaded - total:,.0f} {currency}/month."
            )
        else:
            notes.append(f"Estimated egress cost: {total:,.0f} {currency}/month.")

    return CalcResult(
        calculator="bandwidth",
        assumptions=assumptions,
        formula=("bytes_per_second = rps * avg_payload_bytes ; "
                 "egress_per_month = bytes_per_second * 2592000"),
        calculation=(f"bytes_per_second = {rps:.3g} x {avg_payload_bytes:,.0f} = "
                     f"{bytes_per_second:,.0f} ({mbps:.3g} Mbps) ; "
                     f"egress_per_month = {monthly_gb:,.3g} GB"),
        value=monthly_gb,
        unit="GB/month",
        sensitivity=Sensitivity(
            "average response payload",
            "Egress scales linearly with it. Measure real response sizes including images "
            "and uncompressed JSON before budgeting.",
        ),
        notes=notes + [f"Sustained bandwidth is {mbps:.3g} Mbps at this average rate."],
    )
