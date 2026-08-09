"""The shared output envelope for every OAB calculator.

Every calculation emits the same seven things, in the same order, without exception:

    Assumptions   each labelled observed | stated | assumed | calculated, with a confidence
    Formula       the literal expression, so it can be disputed without the numbers
    Calculation   the expression with values substituted, so it can be checked by hand
    Result        with units, and a range whenever any input is uncertain
    Safety margin the headroom applied, and why
    Confidence    propagated from the inputs, not asserted
    Sensitivity   which single input most changes the result

The last one is the most useful line in a capacity report: it tells the reader which
assumption to go and measure first.

Standard library only — these run on a user's machine through their agent, and a pip
install would break the promise that OAB works from a git clone.
"""

from dataclasses import dataclass, field
from math import floor, isfinite, log10
from typing import Optional, Union

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}
Number = Union[int, float]


def round_sig(value: Number, figures: int = 2) -> float:
    """Round to a number of significant figures.

    Never report more precision than the inputs justify. `0.28 RPS` is honest;
    `0.2777 RPS` is a lie about precision, and a confident-looking wrong number is
    worse than an obviously approximate one.
    """
    if value == 0 or not isfinite(value):
        return float(value)
    magnitude = floor(log10(abs(value)))
    factor = 10 ** (figures - 1 - magnitude)
    return round(value * factor) / factor


@dataclass
class Assumption:
    """One input to a calculation, labelled by where it came from."""

    name: str
    value: Union[Number, str, bool]
    source: str = "assumed"           # observed | stated | assumed | calculated
    confidence: str = "medium"        # high | medium | low
    unit: Optional[str] = None
    impact_if_wrong: Optional[str] = None

    def __post_init__(self):
        if self.source not in ("observed", "stated", "assumed", "calculated"):
            raise ValueError(f"unknown assumption source: {self.source!r}")
        if self.confidence not in CONFIDENCE_ORDER:
            raise ValueError(f"unknown confidence: {self.confidence!r}")

    def to_dict(self):
        out = {
            "name": self.name,
            "value": self.value,
            "source": self.source,
            "confidence": self.confidence,
        }
        if self.unit:
            out["unit"] = self.unit
        if self.impact_if_wrong:
            out["impact_if_wrong"] = self.impact_if_wrong
        return out


@dataclass
class Sensitivity:
    dominant_input: str
    explanation: str
    decision_is_insensitive: bool = False

    def to_dict(self):
        out = {"dominant_input": self.dominant_input, "explanation": self.explanation}
        if self.decision_is_insensitive:
            out["decision_is_insensitive"] = True
        return out


@dataclass
class SafetyMargin:
    factor: float
    rationale: str

    def to_dict(self):
        return {"factor": self.factor, "rationale": self.rationale}


@dataclass
class CalcResult:
    """One calculation, in the fixed envelope, serialisable to capacity-result.schema.json."""

    calculator: str
    assumptions: list
    formula: str
    calculation: str
    value: Number
    unit: str
    safety_margin: Optional[SafetyMargin] = None
    sensitivity: Optional[Sensitivity] = None
    notes: list = field(default_factory=list)
    significant_figures: int = 2
    _range: Optional[tuple] = None

    @property
    def confidence(self) -> str:
        """Propagated from the inputs — a chain containing a low-confidence input cannot
        report high confidence.

        Note this is confidence in the NUMBER. Confidence in the DECISION can still be
        high when the result is insensitive to every uncertain input across its plausible
        range; that case is recorded in `sensitivity.decision_is_insensitive`.
        """
        if not self.assumptions:
            return "low"
        weakest = min(CONFIDENCE_ORDER[a.confidence] for a in self.assumptions)
        return {3: "high", 2: "medium", 1: "low"}[weakest]

    @property
    def rounded(self) -> float:
        return round_sig(self.value, self.significant_figures)

    def with_range(self, low: Number, high: Number) -> "CalcResult":
        self._range = (low, high)
        return self

    def to_dict(self):
        result = {
            "value": self.rounded,
            "unit": self.unit,
            "significant_figures": self.significant_figures,
        }
        if self._range:
            low, high = self._range
            result["range"] = {
                "low": round_sig(low, self.significant_figures),
                "high": round_sig(high, self.significant_figures),
            }

        out = {
            "calculator": self.calculator,
            "assumptions": [a.to_dict() for a in self.assumptions],
            "formula": self.formula,
            "calculation": self.calculation,
            "result": result,
            "confidence": self.confidence,
        }
        if self.safety_margin:
            out["safety_margin"] = self.safety_margin.to_dict()
        if self.sensitivity:
            out["sensitivity"] = self.sensitivity.to_dict()
        if self.notes:
            out["notes"] = self.notes
        return out

    def to_text(self) -> str:
        """Human-readable form, in the fixed order. This is what an agent reads back to a
        user, so it must be checkable by hand without the JSON."""
        lines = [f"{self.calculator}", ""]

        lines.append("Assumptions")
        for a in self.assumptions:
            unit = f" {a.unit}" if a.unit else ""
            impact = f"  [{a.impact_if_wrong}]" if a.impact_if_wrong else ""
            lines.append(f"  {a.name}: {a.value}{unit}  ({a.source}, {a.confidence}){impact}")

        lines += ["", f"Formula      {self.formula}", f"Calculation  {self.calculation}"]

        if self._range:
            low, high = (round_sig(v, self.significant_figures) for v in self._range)
            lines.append(f"Result       {self.rounded} {self.unit}  (range {low}–{high})")
        else:
            lines.append(f"Result       {self.rounded} {self.unit}")

        if self.safety_margin:
            lines.append(
                f"Margin       {self.safety_margin.factor}x — {self.safety_margin.rationale}"
            )
        lines.append(f"Confidence   {self.confidence}")
        if self.sensitivity:
            lines.append(f"Sensitivity  {self.sensitivity.dominant_input} — "
                         f"{self.sensitivity.explanation}")
        for note in self.notes:
            lines.append(f"Note         {note}")
        return "\n".join(lines)
