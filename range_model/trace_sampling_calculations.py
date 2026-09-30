"""Illustrative count/sampling calculations, not instrument or synthesis claims."""
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
import json


def calculate():
    if not __debug__:
        raise ValueError("Calculation validation requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    with localcontext() as context:
        context.prec = 100
        p = Decimal(1) / Decimal(10**19)
        n = 10**19
        alpha = Decimal("0.05")
        log_miss = (1 - p).ln()
        required = int((alpha.ln() / log_miss).to_integral_value(rounding=ROUND_CEILING))
        assert (Decimal(required) * log_miss).exp() <= alpha
        assert (Decimal(required - 1) * log_miss).exp() > alpha
        count_zero = (Decimal(n) * log_miss).exp()
        upper_if_zero = 1 - (alpha.ln() / Decimal(n)).exp()
        assert count_zero > alpha
        return {
            "status": "CALCULATED under stated idealized models; no preparation or measurement",
            "iid_sampling_model": {
                "assumptions": "Independent draws from an unchanged effectively unlimited reservoir, perfect detection and classification, known sampled count; not a fixed finite one-atom specimen.",
                "trace_probability_fraction": str(Fraction(1, 10**19)),
                "sampled_entities": str(n),
                "expected_trace_count": "1",
                "probability_zero_trace_count": str(count_zero),
                "probability_at_least_one": str(1 - count_zero),
                "minimum_sampled_count_for_95_percent_at_least_one": str(required),
                "zero_count_one_sided_95_percent_upper_probability": str(upper_if_zero),
            },
            "fixed_inventory_one_atom_model": {
                "assumptions": "Exactly one known trace atom among N atoms; uniform sample of n distinct atoms without replacement; perfect detection and classification.",
                "total_atoms": str(n),
                "sampled_atoms": str(n // 100),
                "probability_detect_trace_atom": "1/100",
                "probability_miss_trace_atom": "99/100",
                "minimum_sampled_count_for_95_percent_detection": str(95 * n // 100),
            },
        }


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2))
