"""OAB capacity calculators.

Deterministic arithmetic for architecture sizing. Same inputs, same numbers, every time,
from a tested implementation — because arithmetic is the one place where a language
model's failure is silent and confident, and every downstream decision rests on it.

Standard library only. See ../README.md for the formulas in prose, which is the fallback
when Python is unavailable.
"""

__version__ = "0.1.0"

from .result import Assumption, CalcResult, SafetyMargin, Sensitivity, round_sig  # noqa: F401
