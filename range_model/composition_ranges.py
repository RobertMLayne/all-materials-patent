"""Exact mathematical composition ranges; no assertion of material enablement.

Run `python composition_ranges.py build` to regenerate the three JSON artifacts.
Run `python composition_ranges.py verify` for independent finite checks.
Use `generate` for bounded samples, never an alleged exhaustive material list.
Only standard-library modules are required. Floating-point inputs are rejected.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import reduce
from itertools import combinations, islice, product
import json
from math import comb, gcd
from pathlib import Path
from typing import Iterator, Sequence

N_KNOWN = 118
N_HYPOTHETICAL = 20
N_SLOTS = N_KNOWN + N_HYPOTHETICAL
D = 10**19
MIN_FRACTION = Fraction(1, D)
DISCLAIMER = (
    "Mathematical composition coverage only. Hypothetical slots 119–138 are "
    "formal labels, not established elements. These definitions do not establish "
    "material existence, structure, preparation, utility, invention, patentability, "
    "anticipation, obviousness, written description, or enablement."
)


def exact(value: str | int | Fraction) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("Use an integer, decimal/fraction string, or Fraction; not float/bool.")
    if not isinstance(value, (str, int, Fraction)):
        raise TypeError("Unsupported exact-number input.")
    return Fraction(value)


def integer(value: int, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}.")
    return value


def terminating_decimal(value: str | int | Fraction) -> str | None:
    """Exact ordinary decimal, or None if its reduced denominator has other factors."""
    value = exact(value)
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return None
    scale = max(twos, fives)
    scaled = abs(value.numerator) * (10**scale // value.denominator)
    sign = "-" if value < 0 else ""
    if not scale:
        return sign + str(scaled)
    digits = str(scaled).zfill(scale + 1)
    result = digits[:-scale] + "." + digits[-scale:]
    return sign + result.rstrip("0").rstrip(".")


def number_record(value: str | int | Fraction) -> dict:
    value = exact(value)
    percent = 100 * value
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "fraction_exact": str(value),
        "decimal_fraction": terminating_decimal(value),
        "percentage_exact": str(percent),
        "decimal_percentage": terminating_decimal(percent),
    }


def support_class(support: Sequence[int]) -> str:
    validate_support(support)
    return "known_only" if max(support) <= N_KNOWN else "contains_hypothetical"


def validate_support(support: Sequence[int]) -> None:
    if not 1 <= len(support) <= N_SLOTS:
        raise ValueError("Support size must be 1..138.")
    for slot in support:
        integer(slot, "slot", 1)
        if slot > N_SLOTS:
            raise ValueError("Slot exceeds 138.")
    if tuple(support) != tuple(sorted(set(support))):
        raise ValueError("Support labels must be distinct and strictly increasing.")


def iter_supports(k: int, known_only: bool = False) -> Iterator[tuple[int, ...]]:
    integer(k, "k", 1)
    maximum = N_KNOWN if known_only else N_SLOTS
    if k > maximum:
        return
    yield from combinations(range(1, maximum + 1), k)


def validate_composition(support: Sequence[int], fractions: Sequence) -> tuple[Fraction, ...]:
    validate_support(support)
    if len(support) != len(fractions):
        raise ValueError("Each supported label needs one fraction.")
    values = tuple(exact(value) for value in fractions)
    if any(value < MIN_FRACTION for value in values):
        raise ValueError("Supported fractions must be >= 10^-19; zero denotes an absent label.")
    if sum(values) != 1:
        raise ValueError("Supported fractions must sum exactly to one.")
    return values


def normalize_weights(support: Sequence[int], weights: Sequence) -> tuple[Fraction, ...]:
    values = tuple(exact(value) for value in weights)
    if not values or any(value <= 0 for value in values):
        raise ValueError("Normalization requires positive weights.")
    total = sum(values)
    return validate_composition(support, [value / total for value in values])


def composition_record(support: Sequence[int], fractions: Sequence) -> dict:
    values = validate_composition(support, fractions)
    return {
        "basis": "atomic_fraction",
        "classification": support_class(support),
        "support": list(support),
        "fractions": [number_record(value) for value in values],
        "all_other_slots": "exactly zero",
        "sum_fraction_exact": str(sum(values)),
        "sum_percentage_exact": str(100 * sum(values)),
        "on_D_10_pow_19_grid": all((D * value).denominator == 1 for value in values),
    }


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def clipped_bounds(bounds: Sequence[tuple], floor=MIN_FRACTION) -> tuple[tuple[Fraction, Fraction], ...]:
    if not 1 <= len(bounds) <= N_SLOTS:
        raise ValueError("Box dimension must be 1..138.")
    floor = exact(floor)
    if floor <= 0:
        raise ValueError("The supported-coordinate floor must be positive.")
    maximum = 1 - (len(bounds) - 1) * floor
    result = []
    for low, high in bounds:
        low, high = exact(low), exact(high)
        if low > high:
            raise ValueError("Raw lower bound exceeds upper bound.")
        result.append((max(low, floor), min(high, maximum)))
    return tuple(result)


def box_witness(bounds: Sequence[tuple], floor=MIN_FRACTION) -> tuple[Fraction, ...] | None:
    """Exact rational witness; same feasibility test proves real-box feasibility."""
    clipped = clipped_bounds(bounds, floor)
    lower = [low for low, _ in clipped]
    upper = [high for _, high in clipped]
    if any(low > high for low, high in clipped) or sum(lower) > 1 or sum(upper) < 1:
        return None
    remaining = 1 - sum(lower)
    for index in range(len(lower)):
        delta = min(remaining, upper[index] - lower[index])
        lower[index] += delta
        remaining -= delta
    assert remaining == 0
    return tuple(lower)


def lattice_box_witness(bounds: Sequence[tuple], denominator=D, floor=MIN_FRACTION) -> tuple[Fraction, ...] | None:
    integer(denominator, "denominator", 1)
    clipped = clipped_bounds(bounds, floor)
    lower = [ceil_fraction(low * denominator) for low, _ in clipped]
    upper = [(high * denominator).__floor__() for _, high in clipped]
    if any(low > high for low, high in zip(lower, upper)) or sum(lower) > denominator or sum(upper) < denominator:
        return None
    remaining = denominator - sum(lower)
    for index in range(len(lower)):
        delta = min(remaining, upper[index] - lower[index])
        lower[index] += delta
        remaining -= delta
    assert remaining == 0
    return tuple(Fraction(value, denominator) for value in lower)


def positive_integer_compositions(total: int, k: int, minimum=1) -> Iterator[tuple[int, ...]]:
    integer(total, "total", 0)
    integer(k, "k", 1)
    integer(minimum, "minimum", 1)
    if total < k * minimum:
        return
    if k == 1:
        yield (total,)
        return
    for first in range(minimum, total - (k - 1) * minimum + 1):
        for rest in positive_integer_compositions(total - first, k - 1, minimum):
            yield (first,) + rest


def integer_composition_count(total: int, k: int, minimum=1) -> int:
    integer(total, "total", 0)
    integer(k, "k", 1)
    integer(minimum, "minimum", 1)
    residual = total - k * minimum
    return comb(residual + k - 1, k - 1) if residual >= 0 else 0


def iter_lattice_compositions(support: Sequence[int], denominator=D) -> Iterator[tuple[Fraction, ...]]:
    validate_support(support)
    integer(denominator, "denominator", 1)
    minimum = ceil_fraction(denominator * MIN_FRACTION)
    for numerators in positive_integer_compositions(denominator, len(support), minimum):
        yield tuple(Fraction(numerator, denominator) for numerator in numerators)


def iter_rational_compositions(support: Sequence[int], max_denominator: int | None = None) -> Iterator[tuple[Fraction, ...]]:
    """Canonical common denominators are unbounded unless caller imposes a finite cap."""
    validate_support(support)
    if max_denominator is not None:
        integer(max_denominator, "max_denominator", 1)
    if len(support) == 1:
        yield (Fraction(1),)
        return
    denominator = 1
    while max_denominator is None or denominator <= max_denominator:
        minimum = ceil_fraction(denominator * MIN_FRACTION)
        for numerators in positive_integer_compositions(denominator, len(support), minimum):
            if reduce(gcd, numerators, denominator) == 1:
                yield tuple(Fraction(numerator, denominator) for numerator in numerators)
        denominator += 1


def grid_interval(p: int, j: int, m: int) -> tuple[Fraction, Fraction]:
    integer(p, "p", 0)
    if p > 19:
        raise ValueError("Fixed precision index p must be 0..19.")
    integer(j, "j", 0)
    integer(m, "m", 0)
    if not 0 <= j <= m <= 10**p:
        raise ValueError("Require 0 <= j <= m <= 10^p.")
    return Fraction(j, 10**p), Fraction(m, 10**p)


def iter_grid_intervals(p: int, elementary=False, include_singletons=True) -> Iterator[tuple[Fraction, Fraction]]:
    grid_interval(p, 0, 0)
    count = 10**p
    if elementary:
        for j in range(count):
            yield grid_interval(p, j, j + 1)
        return
    for j in range(count + 1):
        for m in range(j if include_singletons else j + 1, count + 1):
            yield grid_interval(p, j, m)


def decimal_refinement_cell(e: int, r: int, j: int) -> tuple[Fraction, Fraction]:
    if not isinstance(e, int) or isinstance(e, bool) or not -19 <= e <= -1:
        raise ValueError("Decade exponent e must be -19..-1.")
    integer(r, "r", 0)
    integer(j, "j", 1)
    if not 10**r <= j < 10**(r + 1):
        raise ValueError("Require 10^r <= j < 10^(r+1).")
    scale = Fraction(10) ** (e - r)
    return j * scale, (j + 1) * scale


def complementary_interval(low, high) -> tuple[Fraction, Fraction]:
    low, high = exact(low), exact(high)
    if not 0 <= low <= high <= 1:
        raise ValueError("Require 0 <= lower <= upper <= 1.")
    return 1 - high, 1 - low


def count_record(value: int) -> dict:
    with localcontext() as context:
        context.prec = 50
        decimal_value = Decimal(value)
        return {
            "exact_integer": str(value),
            "decimal_digits": len(str(value)),
            "log10_approximation": str(decimal_value.log10()) if value > 0 else None,
            "approximation_note": "Only the logarithm is approximate; integer count is exact.",
        }


def build_model() -> dict:
    precision_grids = []
    for p in range(20):
        size = 10**p
        precision_grids.append({
            "p": p, "M": str(size), "fraction_step": number_record(Fraction(1, size)),
            "raw_elementary_interval_count": str(size),
            "raw_nondegenerate_endpoint_subrange_count": str(size * (size + 1) // 2),
            "raw_endpoint_subrange_count_including_singletons": str((size + 1) * (size + 2) // 2),
        })
    cardinalities = []
    for k in range(1, N_SLOTS + 1):
        all_supports = comb(N_SLOTS, k)
        known_supports = comb(N_KNOWN, k) if k <= N_KNOWN else 0
        per_support = comb(D - 1, k - 1)
        cardinalities.append({
            "k": k, "all_supports": str(all_supports), "known_only_supports": str(known_supports),
            "supports_containing_hypothetical": str(all_supports - known_supports),
            "D_grid_compositions_per_support": str(per_support),
            "D_grid_compositions_all_supports": str(all_supports * per_support),
            "D_grid_compositions_known_only": str(known_supports * per_support),
            "maximum_coordinate_fraction": number_record(1 - (k - 1) * MIN_FRACTION),
        })
    return {
        "format_version": "1.0", "purpose": DISCLAIMER,
        "basis": "Atomic fractions by default; independent mass-fraction treatment needs an explicit basis and weights.",
        "slots": {"known": {"first": 1, "last": 118}, "hypothetical": {"first": 119, "last": 138},
                  "known_count": 118, "hypothetical_count": 20, "total_count": 138,
                  "classification": "Hypothetical labels are never presented as established chemical elements."},
        "minimum_positive_fraction": number_record(MIN_FRACTION),
        "support_rule": "Every nonempty subset S of slots 1..138; labels strictly increasing; all other fractions zero.",
        "real_continuous_domain": {
            "definition": "For every support S with k=1..138: x in R^k, each x_i >= a=10^-19, sum_i x_i=1.",
            "upper_bound": "x_i <= 1-(k-1)a; k=1 forces x_1=1.",
            "coverage": "Includes rational and irrational coordinates; represented symbolically, not enumerated.",
            "exclusion": "Positive fractions below 10^-19 are excluded; zero denotes absent support only.",
        },
        "all_rational_domain": {
            "definition": "Intersection of the real domain with Q^k; all positive common denominators q are allowed.",
            "canonical_enumeration": "q=1,2,...; n_i >= ceil(q/D); sum n_i=q; gcd(q,n_1,...,n_k)=1; x_i=n_i/q.",
            "finite_exports": "A max_denominator or sample limit is an export limit only, never an exhaustive domain claim.",
            "not_the_fixed_grid": "1/3 is included in this domain but not in the D=10^19 grid.",
        },
        "fixed_D_grid": {"D": str(D), "definition": "n_i positive integers, sum n_i=D, x_i=n_i/D.",
                         "step": number_record(MIN_FRACTION), "optional_subset_only": True},
        "fixed_precision_intervals": {
            "p_range_inclusive": [0, 19],
            "elementary": "[j/10^p,(j+1)/10^p], 0 <= j < 10^p.",
            "all_endpoint_subranges": "[j/10^p,m/10^p], 0 <= j <= m <= 10^p; singletons explicitly included.",
            "zero_endpoint": "Raw grids include zero. Intersect supported-coordinate boxes with [a,1-(k-1)a]; discard empty intersections.",
            "closed_intervals": "All endpoints included. Adjacent intervals overlap at boundaries; clipped records may duplicate.",
            "count_note": "Counts below count raw index-defined intervals, not distinct intervals after clipping.",
            "grids": precision_grids,
        },
        "unbounded_decimal_refinement": {
            "definition": "e=-19..-1, r=0,1,..., j=10^r..10^(r+1)-1: [j*10^(e-r),(j+1)*10^(e-r)].",
            "per_depth_raw_cell_count": "171*10^r", "scope": "Union at each r covers [10^-19,1]; refinement changes widths, not the coordinate floor.",
        },
        "arbitrary_rational_endpoint_intervals": "Every closed [L,U] with rational endpoints is permitted, then intersected with the supported-coordinate domain.",
        "multicomponent_boxes": {
            "normalization": "Every box is intersected with sum x_i=1; component choices are coupled.",
            "feasibility": "After clipping, every L_i<=U_i and sum L_i<=1<=sum U_i.",
            "proof": "Start at all lower bounds and distribute the remaining mass without exceeding any upper bound. Total capacity is sufficient exactly under these inequalities.",
            "rational_witness": "Rational endpoints give a rational greedy witness; the same condition proves real-domain feasibility.",
            "D_grid_feasibility": "ell_i=ceil(D*L_i); u_i=floor(D*U_i); every ell_i<=u_i and sum ell_i<=D<=sum u_i.",
        },
        "binary_complements": "x_A in [L,U] entails x_B=1-x_A in [1-U,1-L], with both fractions satisfying the floor.",
        "coverage_arguments": [
            "Every nonzero coordinate uniquely determines its support, so the union over all nonempty supports covers the specified simplex with optional zero coordinates.",
            "Every real coordinate in [0,1] lies in a closed elementary interval at every fixed p; x=1 lies in the last interval. Products of these intervals, intersected with the simplex, cover every allowed real composition.",
            "Every rational vector has a finite least common denominator; primitive common-denominator enumeration reaches it exactly once.",
            "For a fixed k-support, subtract one from each positive grid numerator. Stars and bars gives C(D-1,k-1). Selecting the support gives C(N,k) times that count.",
            "Summing over k equals C(D+N-1,N-1), the number of weak compositions of D into N slots. No subtraction of one is needed because D>0.",
        ],
        "support_counts": {
            "known_only": str(2**118 - 1), "all_formal_slots": str(2**138 - 1),
            "containing_hypothetical": str((2**20 - 1) * 2**118),
        },
        "D_grid_counts": {
            "known_only_formula": "C(D+117,117)", "known_only": count_record(comb(D + 117, 117)),
            "all_formal_slots_formula": "C(D+137,137)", "all_formal_slots": count_record(comb(D + 137, 137)),
            "containing_hypothetical": count_record(comb(D + 137, 137) - comb(D + 117, 117)),
            "by_support_size": cardinalities,
        },
        "serialization": "Exact integers and fractions are strings. Terminating decimals are exact ordinary decimal strings. Nonterminating decimal fields are null; exact rational fields remain authoritative. Only explicitly labeled logarithms are approximate.",
        "limitations": [DISCLAIMER, "No composition basis conversion is inferred.", "A fraction-only description does not identify bonding, phases, crystal structures, microstructures, processing histories, isotopes, or uses.", "Finite samples and finite grids do not enumerate the continuous or all-rational domain."],
    }


def interval_record(bounds: tuple[Fraction, Fraction]) -> dict:
    return {"lower": number_record(bounds[0]), "upper": number_record(bounds[1]), "endpoints": "closed"}


def build_examples() -> dict:
    tiny = (Fraction(1, 10**18), Fraction(1, 10**17))
    thirds = (Fraction(1, 3),) * 3
    examples = {
        "pure_known": composition_record([6], [1]),
        "pure_hypothetical_formal_only": composition_record([119], [1]),
        "fifty_fifty_known": composition_record([1, 8], ["1/2", "1/2"]),
        "minimum_binary": composition_record([1, 8], [MIN_FRACTION, 1 - MIN_FRACTION]),
        "requested_tiny_lower_endpoint": composition_record([1, 8], [tiny[0], 1 - tiny[0]]),
        "requested_tiny_upper_endpoint": composition_record([1, 8], [tiny[1], 1 - tiny[1]]),
        "rational_thirds_off_D_grid": composition_record([1, 6, 8], thirds),
        "all_138_slots_minimum_boundary": composition_record(list(range(1, 139)), [MIN_FRACTION] * 137 + [Fraction(D - 137, D)]),
        "all_138_slots_uniform_rational": composition_record(list(range(1, 139)), [Fraction(1, 138)] * 138),
        "normalized_weights_2_3_5": composition_record([1, 6, 8], normalize_weights([1, 6, 8], [2, 3, 5])),
    }
    feasible = [("1/5", "2/5"), ("3/10", "1/2"), ("1/10", "1/2")]
    witness = box_witness(feasible)
    return {
        "purpose": DISCLAIMER, "compositions": examples,
        "requested_interval": {
            "fraction_interval": interval_record(tiny), "binary_complement": interval_record(complementary_interval(*tiny)),
            "D_grid_numerator_lower": "10", "D_grid_numerator_upper": "100",
            "inclusive_D_grid_point_count": "91", "elementary_D_grid_interval_count": "90",
            "indexed_at_p19": {"p": 19, "j": "10", "m": "100"},
            "coarser_endpoint_representation_at_p18": {"p": 18, "j": "1", "m": "10"},
        },
        "real_continuous_symbolic_example": {
            "support": [1, 8], "fractions": ["sqrt(2)/2", "1-sqrt(2)/2"],
            "sum_exact": "1", "domain": "real continuous; not rational; symbolic only", "numerically_evaluated": False,
        },
        "box_examples": {
            "feasible": {"bounds": [interval_record((exact(lower), exact(upper))) for lower, upper in feasible],
                         "witness": composition_record([1, 6, 8], witness)},
            "lower_sum_too_large": {"bounds_fraction_exact": [["2/5", "1/2"]] * 3, "feasible": False},
            "upper_sum_too_small": {"bounds_fraction_exact": [["1/10", "1/5"]] * 3, "feasible": False},
            "singleton_thirds": {"bounds_fraction_exact": [["1/3", "1/3"]] * 3, "real_and_rational_feasible": True, "D_grid_feasible": False},
        },
    }


def verify() -> dict:
    """Independent exhaustive toy checks plus exact production-domain boundaries."""
    if not __debug__:
        raise ValueError("Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    results = []

    def check(name, predicate, evidence):
        if not predicate:
            raise AssertionError(name)
        results.append({"test": name, "status": "passed", "evidence": evidence})

    count_cases = 0
    for slots in range(1, 6):
        for total in range(1, 9):
            by_k = [0] * (slots + 1)
            for vector in product(range(total + 1), repeat=slots):
                if sum(vector) == total:
                    by_k[sum(value > 0 for value in vector)] += 1
            expected = [0] + [comb(slots, k) * (comb(total - 1, k - 1) if k <= total else 0) for k in range(1, slots + 1)]
            assert by_k == expected
            assert sum(by_k) == comb(total + slots - 1, slots - 1)
            count_cases += 1
    check("exhaustive_toy_support_and_composition_counts", count_cases == 40, "Independent Cartesian enumeration: N=1..5, denominator=1..8; support-stratified and total counts.")

    composition_cases = 0
    for total in range(1, 13):
        for k in range(1, 5):
            for minimum in (1, 2, 3):
                observed = list(positive_integer_compositions(total, k, minimum))
                independent = [v for v in product(range(minimum, total + 1), repeat=k) if sum(v) == total]
                assert observed == independent
                assert len(observed) == integer_composition_count(total, k, minimum)
                composition_cases += 1
    check("integer_generator_and_minimum_floor", composition_cases == 144, "Independent brute-force composition vectors for totals 1..12, k=1..4, minimum=1..3.")

    possible_bounds = [(Fraction(j, 4), Fraction(m, 4)) for j in range(5) for m in range(j, 5)]
    box_cases = 0
    for k in (2, 3):
        lattice_vectors = [tuple(Fraction(v, 4) for v in row) for row in product(range(1, 5), repeat=k) if sum(row) == 4]
        for bounds in product(possible_bounds, repeat=k):
            expected = [v for v in lattice_vectors if all(lo <= x <= hi for x, (lo, hi) in zip(v, bounds))]
            rational = box_witness(bounds, floor=Fraction(1, 4))
            lattice = lattice_box_witness(bounds, denominator=4, floor=Fraction(1, 4))
            assert bool(expected) == (lattice is not None) == (rational is not None)
            if lattice is not None:
                assert lattice in expected and sum(lattice) == 1
            box_cases += 1
    check("exhaustive_toy_box_feasibility", box_cases == 3600, "All closed endpoint boxes on denominator 4 for k=2,3, compared against independent brute-force lattice witnesses.")

    third = Fraction(1, 3)
    thirds = [(third, third)] * 3
    check("rational_feasible_but_D_grid_infeasible", box_witness(thirds) == (third,) * 3 and lattice_box_witness(thirds) is None, "Exact thirds normalize to one; 3 does not divide D=10^19.")
    check("unequal_lattice_rounding_rejects_infeasible_box", lattice_box_witness([("0.15", "0.15"), ("0.85", "0.85")], denominator=10) is None, "Real/rational singleton is feasible, denominator-10 integer ceilings exceed floors.")

    singleton = [(Fraction(1, 5), Fraction(1, 5)), (Fraction(3, 10), Fraction(3, 10)), (Fraction(1, 2), Fraction(1, 2))]
    check("closed_equality_boundaries", box_witness(singleton) == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)), "Both lower and upper sums equal one; accepted.")
    check("upper_sum_infeasible", box_witness([("1/10", "1/5")] * 3) is None, "Total upper capacity 3/5 < 1.")
    check("lower_sum_infeasible", box_witness([("2/5", "1/2")] * 3) is None, "Total required lower mass 6/5 > 1.")
    check("zero_supported_interval_rejected", box_witness([(0, 0), (1, 1)]) is None, "Zero is permitted only outside the positive support.")
    check("unary_is_exactly_one", box_witness([(0, 1)]) == (Fraction(1),), "Normalization forces a unary composition to one.")

    maximum_vector = (MIN_FRACTION,) * 137 + (Fraction(D - 137, D),)
    check("138_slot_minimum_boundary", validate_composition(tuple(range(1, 139)), maximum_vector) == maximum_vector and sum(maximum_vector) == 1, "137 minimum fractions plus (D-137)/D; exact normalization.")
    check("138_slot_box_and_grid_boundary", box_witness([(MIN_FRACTION, MIN_FRACTION)] * 137 + [(Fraction(D - 137, D), Fraction(D - 137, D))]) == maximum_vector and lattice_box_witness([(MIN_FRACTION, MIN_FRACTION)] * 137 + [(Fraction(D - 137, D), Fraction(D - 137, D))]) == maximum_vector, "Rational and fixed-D feasibility agree at the 138-slot extreme.")
    check("normalization_from_weights", normalize_weights([1, 6, 8], [2, 3, 5]) == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)), "Independent expected normalized fractions.")

    check("requested_percentage_endpoints", 100 * Fraction(10, D) == Fraction(1, 10**16) and 100 * Fraction(100, D) == Fraction(1, 10**15), "Fraction 10^-18..10^-17 maps to 10^-16%..10^-15%.")
    check("minimum_percentage_and_half", 100 * MIN_FRACTION == Fraction(1, 10**17) and number_record("1/2")["decimal_percentage"] == "50", "Minimum is 10^-17%, and half is 50%.")
    check("requested_grid_indices", grid_interval(19, 10, 100) == grid_interval(18, 1, 10) == (Fraction(1, 10**18), Fraction(1, 10**17)), "Both indexed representations have identical exact endpoints.")
    complement = complementary_interval(Fraction(1, 10**18), Fraction(1, 10**17))
    check("binary_complement_reversal", complement == (1 - Fraction(1, 10**17), 1 - Fraction(1, 10**18)), "Endpoints reverse on complementation, preserving exact sums.")

    for p in range(20):
        size = 10**p
        assert grid_interval(p, 0, 1)[0] == 0
        assert grid_interval(p, size - 1, size)[1] == 1
        j = size // 2
        if 0 < j < size:
            assert grid_interval(p, j - 1, j)[1] == grid_interval(p, j, j + 1)[0]
    for p in (0, 1):
        size = 10**p
        assert len(list(iter_grid_intervals(p, elementary=True))) == size
        assert len(list(iter_grid_intervals(p))) == (size + 1) * (size + 2) // 2
        assert len(list(iter_grid_intervals(p, include_singletons=False))) == size * (size + 1) // 2
    check("all_fixed_precisions_and_endpoint_subranges", True, "Endpoint and adjacency checks at p=0..19; exhaustive generator-count checks at p=0,1.")

    refinement_cases = 0
    for e in range(-19, 0):
        for r in range(3):
            assert decimal_refinement_cell(e, r, 10**r)[0] == Fraction(10) ** e
            assert decimal_refinement_cell(e, r, 10**(r + 1) - 1)[1] == Fraction(10) ** (e + 1)
            refinement_cases += 1
    check("decimal_refinement_decade_boundaries", refinement_cases == 57, "All 19 decades, refinement depths 0,1,2; exact first and final endpoints.")

    for k in (2, 3):
        observed = list(iter_rational_compositions(list(range(1, k + 1)), max_denominator=8))
        independent = set()
        for q in range(1, 9):
            for nums in product(range(1, q + 1), repeat=k):
                if sum(nums) == q:
                    independent.add(tuple(Fraction(n, q) for n in nums))
        assert len(observed) == len(set(observed)) and set(observed) == independent
    check("canonical_rational_enumeration", True, "All denominator <=8 binary/ternary vectors independently collected and deduplicated; generator returns exactly that set once.")
    beyond_D = next(iter_lattice_compositions([1, 8], denominator=D + 1))
    check("denominator_above_D_preserves_positive_floor", beyond_D == (Fraction(2, D + 1), Fraction(D - 1, D + 1)) and all(value >= MIN_FRACTION for value in beyond_D), "At q=D+1 the minimum numerator is ceil(q/D)=2, not 1; arbitrary denominators do not permit below-floor coordinates.")
    check("unary_rational_generator_terminates", list(iter_rational_compositions([1])) == [(Fraction(1),)], "Unary domain has exactly one point even without a denominator cap.")
    check("support_classification", support_class([1, 118]) == "known_only" and support_class([1, 119]) == "contains_hypothetical" and support_class([138]) == "contains_hypothetical", "Explicit boundaries 118,119,138.")

    def fails(call):
        try:
            call()
        except (TypeError, ValueError):
            return True
        return False
    invalid_cases = [lambda: exact(0.1), lambda: exact(True), lambda: validate_support([2, 1]), lambda: validate_support([1, 1]), lambda: validate_support([0]), lambda: validate_support([139]), lambda: validate_composition([1, 8], ["0.1", "0.2"]), lambda: validate_composition([1, 8], [0, 1]), lambda: validate_composition([1, 8], ["1e-20", "0.99999999999999999999"]), lambda: grid_interval(20, 0, 1), lambda: grid_interval(19, 2, 1)]
    check("invalid_inputs_rejected", all(fails(call) for call in invalid_cases), f"{len(invalid_cases)} malformed/float/unnormalized/below-floor input cases.")
    check("exact_decimal_serialization", terminating_decimal(MIN_FRACTION) == "0.0000000000000000001" and terminating_decimal(Fraction(1, 10**18)) == "0.000000000000000001" and terminating_decimal(third) is None and terminating_decimal(Fraction(-1, 8)) == "-0.125", "Terminating strings are exact; no invented rounded decimal for thirds.")

    for slots in (118, 138):
        assert sum(comb(slots, k) * comb(D - 1, k - 1) for k in range(1, slots + 1)) == comb(D + slots - 1, slots - 1)
    check("production_count_identity", True, "Exact large-integer sum across every support size equals closed form for 118 and 138 slots.")
    model, examples = build_model(), build_examples()

    def contains_float(value):
        if isinstance(value, float):
            return True
        if isinstance(value, dict):
            return any(contains_float(v) for v in value.values())
        if isinstance(value, list):
            return any(contains_float(v) for v in value)
        return False
    check("artifact_serialization_roundtrip", json.loads(json.dumps(model)) == model and json.loads(json.dumps(examples)) == examples and not contains_float(model) and not contains_float(examples), "Both generated artifacts round-trip exactly through JSON and contain no binary floats.")
    return {
        "status": "passed", "test_group_count": len(results), "results": results,
        "runtime_arithmetic": "Python standard-library integer, Fraction, and Decimal arithmetic; no third-party dependencies.",
        "proof_vs_tests": "Finite checks support implementation correctness. Universal mathematical coverage follows the definitions and coverage arguments in composition_range_model.json, not exhaustive testing of the actual infinite or astronomical domains.",
        "limitations": DISCLAIMER,
    }


def write_artifacts(directory: Path) -> dict:
    report = verify()
    artifacts = {
        "composition_range_model.json": build_model(),
        "numeric_examples.json": build_examples(),
        "verification_report.json": report,
    }
    directory.mkdir(parents=True, exist_ok=True)
    for filename, contents in artifacts.items():
        (directory / filename).write_text(json.dumps(contents, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": "passed", "test_groups": report["test_group_count"], "files": list(artifacts)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="Verify and write JSON artifacts beside this source file.")
    sub.add_parser("verify", help="Print the verification report without writing files.")
    generate = sub.add_parser("generate", help="Print a bounded sample, explicitly not an exhaustive material list.")
    generate.add_argument("--support", required=True, help="Strictly increasing comma-separated slots, e.g. 1,8.")
    generate.add_argument("--domain", choices=("grid", "rational"), default="grid")
    generate.add_argument("--denominator", type=int, default=D)
    generate.add_argument("--max-denominator", type=int, default=100)
    generate.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    if args.command == "build":
        output = write_artifacts(Path(__file__).resolve().parent)
    elif args.command == "verify":
        output = verify()
    else:
        support = [int(label.strip()) for label in args.support.split(",")]
        validate_support(support)
        integer(args.limit, "limit", 1)
        if args.limit > 10000:
            parser.error("Sample limit must be <=10000; astronomical/infinite domains are symbolic.")
        iterator = iter_lattice_compositions(support, args.denominator) if args.domain == "grid" else iter_rational_compositions(support, args.max_denominator)
        sample = list(islice(iterator, args.limit))
        output = {"purpose": DISCLAIMER, "export": "bounded sample; not the full domain", "domain": args.domain,
                  "denominator": str(args.denominator) if args.domain == "grid" else None,
                  "max_denominator": str(args.max_denominator) if args.domain == "rational" else None,
                  "limit": args.limit, "returned": len(sample),
                  "records": [composition_record(support, vector) for vector in sample]}
    print(json.dumps(output, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
