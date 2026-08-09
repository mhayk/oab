"""Monthly cost: infrastructure plus the operational cost nobody puts in the spreadsheet.

    infrastructure = sum(quantity * unit_price)
    operational    = complexity_points * hours_per_point * loaded_hourly_rate
    total          = infrastructure + operational

The operational line is the point of this calculator. A component's price is not its
invoice; it is invoice plus on-call surface plus upgrade burden plus the engineer-hours to
understand it. At the default rates each complexity point costs roughly 240 GBP/month,
which reframes most small-system decisions correctly: self-hosting a database to save
25 GBP/month costs 3 complexity points, or about 720 GBP/month of engineering attention.

Prices are inputs, not built in. Price tables live in knowledge/cost/ with their date
attached, because undated prices rot and a stale number stated confidently is worse than
no number.
"""

from .result import Assumption, CalcResult, Sensitivity

DEFAULT_HOURS_PER_POINT = 4.0
DEFAULT_LOADED_RATE = 60.0


def add_arguments(parser):
    parser.add_argument("--item", action="append", default=[], metavar="NAME:QTY:PRICE",
                        help="repeatable, e.g. --item app:2:20 --item database:1:250")
    parser.add_argument("--complexity-points", type=float, default=0.0)
    parser.add_argument("--hours-per-point", type=float, default=DEFAULT_HOURS_PER_POINT,
                        help=f"engineer-hours per point per month (default {DEFAULT_HOURS_PER_POINT})")
    parser.add_argument("--loaded-rate", type=float, default=DEFAULT_LOADED_RATE,
                        help=f"loaded hourly cost of an engineer (default {DEFAULT_LOADED_RATE})")
    parser.add_argument("--currency", default="GBP")
    parser.add_argument("--price-date", help="date the price table was checked, ISO format")
    parser.add_argument("--uncertainty", type=float, default=0.25,
                        help="range width around the estimate (default 0.25)")


def parse_item(raw):
    parts = raw.split(":")
    if len(parts) != 3:
        raise ValueError(f"--item must be NAME:QTY:PRICE, got {raw!r}")
    name, quantity, price = parts
    try:
        return name, float(quantity), float(price)
    except ValueError:
        raise ValueError(f"--item quantity and price must be numbers, got {raw!r}")


def calculate(item=None, complexity_points=0.0, hours_per_point=DEFAULT_HOURS_PER_POINT,
              loaded_rate=DEFAULT_LOADED_RATE, currency="GBP", price_date=None,
              uncertainty=0.25):
    items = [parse_item(raw) for raw in (item or [])]
    if not items and complexity_points == 0:
        raise ValueError("provide at least one --item or a --complexity-points value")
    if not 0 <= uncertainty < 1:
        raise ValueError("uncertainty must be between 0 and 1")

    infrastructure = sum(qty * price for _, qty, price in items)
    operational = complexity_points * hours_per_point * loaded_rate
    total = infrastructure + operational

    assumptions = [
        Assumption(f"{name} x{qty:g}", qty * price, source="stated", confidence="medium",
                   unit=f"{currency}/month")
        for name, qty, price in items
    ]
    if complexity_points:
        assumptions += [
            Assumption("complexity points", complexity_points, source="calculated",
                       confidence="medium", unit="points"),
            Assumption("engineer-hours per point per month", hours_per_point,
                       source="assumed", confidence="low",
                       unit="hours",
                       impact_if_wrong="proportional on the operational line, which usually "
                                       "dominates for small teams"),
            Assumption("loaded hourly rate", loaded_rate, source="assumed",
                       confidence="medium", unit=f"{currency}/hour"),
        ]
    if price_date:
        assumptions.append(Assumption("price table date", price_date, source="stated",
                                      confidence="high"))

    breakdown = " + ".join(f"{name} ({qty:g} x {price:g})" for name, qty, price in items)
    notes = [
        f"Infrastructure: {infrastructure:,.0f} {currency}/month.",
        f"Operational: {operational:,.0f} {currency}/month "
        f"({complexity_points:g} points x {hours_per_point:g} h x {loaded_rate:g} {currency}).",
    ]
    if operational > infrastructure and infrastructure > 0:
        notes.append(
            "The operational line exceeds the infrastructure line. This is normal for a small "
            "team, invisible in every cloud calculator, and the reason a cheaper self-hosted "
            "option is often the more expensive architecture."
        )
    if not price_date:
        notes.append("No price date given. Undated prices rot — record when the table was checked.")
    notes.append("Estimates, not quotes. Verify against your provider's current pricing.")

    return CalcResult(
        calculator="cost",
        assumptions=assumptions,
        formula=("infrastructure = sum(quantity * unit_price) ; "
                 "operational = complexity_points * hours_per_point * loaded_rate ; "
                 "total = infrastructure + operational"),
        calculation=(f"infrastructure = {breakdown or 0} = {infrastructure:,.0f} ; "
                     f"operational = {complexity_points:g} x {hours_per_point:g} x "
                     f"{loaded_rate:g} = {operational:,.0f} ; "
                     f"total = {total:,.0f} {currency}"),
        value=total,
        unit=f"{currency}/month",
        sensitivity=Sensitivity(
            "engineer-hours per complexity point",
            "The operational line usually dominates for small teams and rests on a default of "
            f"{hours_per_point:g} hours per point per month, which is judgement rather than "
            "measurement. Calibrate it against your own incident and maintenance records.",
        ),
        notes=notes,
    ).with_range(total * (1 - uncertainty), total * (1 + uncertainty))
