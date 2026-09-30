"""Exact positive rational compositions without an imposed concentration floor.

The older composition_ranges module retains its 10^-19 floor and optional grid.
This supplement implements the manuscript's broader rational domain separately.
Mathematical feasibility and count compatibility do not establish physical
preparation, measurement, material properties, novelty, or patent coverage.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import reduce
from itertools import combinations, islice, product
import json
from math import gcd, lcm
from pathlib import Path
from typing import Iterator, Sequence

from composition_ranges import (
    exact, integer, number_record, positive_integer_compositions,
    support_class, validate_support,
)

DISCLAIMER = (
    "Exact mathematical positive-rational domain and finite-inventory accounting "
    "only. No preparation, measurement, property, novelty, or legal effect is established."
)


def validate(support: Sequence[int], fractions: Sequence) -> tuple[Fraction, ...]:
    validate_support(support)
    if len(support) != len(fractions):
        raise ValueError("Every supported label requires exactly one coordinate.")
    values = tuple(exact(value) for value in fractions)
    if any(value <= 0 for value in values):
        raise ValueError("Supported coordinates must be strictly positive; omit absent labels.")
    if sum(values) != 1:
        raise ValueError("Coordinates must sum exactly to one.")
    return values


def normalize(support: Sequence[int], weights: Sequence) -> tuple[Fraction, ...]:
    values = tuple(exact(value) for value in weights)
    if not values or any(value <= 0 for value in values):
        raise ValueError("Weights must be strictly positive exact numbers.")
    total = sum(values)
    return validate(support, [value / total for value in values])


def record(support: Sequence[int], fractions: Sequence) -> dict:
    values = validate(support, fractions)
    denominator = lcm(*(value.denominator for value in values))
    numerators = tuple(int(value * denominator) for value in values)
    assert sum(numerators) == denominator
    assert reduce(gcd, numerators, denominator) == 1
    return {
        "evidence_status": "CALCULATED", "scope": DISCLAIMER,
        "basis": "atomic_count_fraction_target", "support": list(support),
        "classification": support_class(support),
        "fractions": [number_record(value) for value in values],
        "all_other_slots": "exactly zero in the target specification",
        "sum_fraction_exact": "1", "imposed_positive_floor": None,
        "primitive_denominator": str(denominator),
        "primitive_numerators": [str(value) for value in numerators],
        "finite_inventory_rule": "An exact N-atom count realization requires N to be a positive multiple of the primitive denominator; this supplies no preparation route.",
    }


def rational_compositions(support: Sequence[int], max_denominator: int | None = None) -> Iterator[tuple[Fraction, ...]]:
    """Unique primitive vectors; an export cap never limits the defined domain."""
    validate_support(support)
    if max_denominator is not None:
        integer(max_denominator, "max_denominator", 1)
    if len(support) == 1:
        yield (Fraction(1),)
        return
    denominator = len(support)
    while max_denominator is None or denominator <= max_denominator:
        for numerators in positive_integer_compositions(denominator, len(support)):
            if reduce(gcd, numerators, denominator) == 1:
                yield tuple(Fraction(numerator, denominator) for numerator in numerators)
        denominator += 1


def bounds_exact(bounds: Sequence[tuple]) -> tuple[tuple[Fraction, Fraction], ...]:
    if not 1 <= len(bounds) <= 138:
        raise ValueError("A composition box needs 1..138 coordinates.")
    values = []
    for low, high in bounds:
        low, high = exact(low), exact(high)
        if low > high:
            raise ValueError("Lower endpoint exceeds upper endpoint.")
        values.append((max(Fraction(0), low), min(Fraction(1), high)))
    return tuple(values)


def positive_box_witness(bounds: Sequence[tuple]) -> tuple[Fraction, ...] | None:
    """Witness for a closed rational box intersected with the open simplex.

    Zero endpoints are allowed, but zero coordinates cannot inhabit this support.
    Reserve a small exact share for each zero lower endpoint before filling the
    remaining capacity. This distinguishes strict positivity from its closure.
    """
    clipped = bounds_exact(bounds)
    lower = [low for low, _ in clipped]
    upper = [high for _, high in clipped]
    if any(low > high or high <= 0 for low, high in clipped):
        return None
    if sum(lower) > 1 or sum(upper) < 1:
        return None
    zeros = [i for i, value in enumerate(lower) if value == 0]
    slack = 1 - sum(lower)
    if zeros and slack == 0:
        return None
    if zeros:
        share = min(min(upper[i] for i in zeros), slack / len(zeros)) / 2
        for i in zeros:
            lower[i] = share
    remaining = 1 - sum(lower)
    for i in range(len(lower)):
        allocated = min(remaining, upper[i] - lower[i])
        lower[i] += allocated
        remaining -= allocated
    assert remaining == 0 and all(value > 0 for value in lower)
    return tuple(lower)


def lattice_witness(bounds: Sequence[tuple], denominator: int) -> tuple[Fraction, ...] | None:
    """Any positive integer inventory denominator, independent of the old grid."""
    integer(denominator, "denominator", 1)
    clipped = bounds_exact(bounds)
    lower = [max(1, -(-(low * denominator).numerator // (low * denominator).denominator)) for low, _ in clipped]
    upper = [(high * denominator).__floor__() for _, high in clipped]
    if any(low > high for low, high in zip(lower, upper)) or sum(lower) > denominator or sum(upper) < denominator:
        return None
    remaining = denominator - sum(lower)
    for i in range(len(lower)):
        allocated = min(remaining, upper[i] - lower[i])
        lower[i] += allocated
        remaining -= allocated
    assert remaining == 0
    return tuple(Fraction(value, denominator) for value in lower)


def finite_inventory(support: Sequence[int], fractions: Sequence, atoms: int) -> dict:
    integer(atoms, "atoms", 1)
    values = validate(support, fractions)
    counts = tuple(value * atoms for value in values)
    compatible = all(count.denominator == 1 for count in counts)
    return {
        "evidence_status": "CALCULATED", "scope": DISCLAIMER,
        "total_atoms": str(atoms), "count_compatible": compatible,
        "target_counts_exact": [str(count) for count in counts],
        "integer_counts": [str(int(count)) for count in counts] if compatible else None,
        "smallest_nonzero_count_fraction_for_this_inventory": number_record(Fraction(1, atoms)),
        "sample_independent_floor_established": False,
    }


def one_trace_atom_subsample_inclusion_probability(atoms: int, sampled_atoms: int) -> Fraction:
    """Chance an assigned trace atom is included in a uniform subset.

    Actual observation also requires a separate detection/classification model.
    """
    integer(atoms, "atoms", 1)
    integer(sampled_atoms, "sampled_atoms", 0)
    if sampled_atoms > atoms:
        raise ValueError("Subsample exceeds the fixed inventory.")
    return Fraction(sampled_atoms, atoms)


def conditional_inventory(support: Sequence[int], fractions: Sequence, conditional_partitions: Sequence[Sequence], atoms: int) -> dict:
    """Count compatibility for a classical isotope/state partition of each element.

    Caller-supplied partition labels need their own species/state provenance.
    This is not a validation of a nucleus, quantum state, or its availability.
    """
    values = validate(support, fractions)
    integer(atoms, "atoms", 1)
    if len(conditional_partitions) != len(support):
        raise ValueError("Every supported element needs a conditional partition.")
    counts = []
    for elemental, partition in zip(values, conditional_partitions):
        proportions = tuple(exact(value) for value in partition)
        if not proportions or any(value < 0 for value in proportions) or sum(proportions) != 1:
            raise ValueError("Conditional partitions must be nonnegative and sum exactly to one.")
        counts.append(tuple(atoms * elemental * value for value in proportions))
    return {
        "scope": DISCLAIMER, "evidence_status": "CALCULATED",
        "classical_partition_count_compatible": all(value.denominator == 1 for row in counts for value in row),
        "partition_counts_exact": [[str(value) for value in row] for row in counts],
        "total_atoms": str(atoms),
        "species_or_state_existence_established": False,
        "state_label_provenance": "Must be supplied separately; no specific isotope or nuclear state is asserted by these anonymous partitions.",
    }


def model() -> dict:
    return {
        "schema_version": "1.0", "scope": DISCLAIMER,
        "element_labels": {"recognized": 118, "hypothetical": 20, "total": 138},
        "unrestricted_rational_domain": "For each nonempty ordered support S, x_i=n_i/q, q any positive integer, n_i>=1, sum(n_i)=q; gcd(q,n_1,...,n_k)=1 removes duplicate representations.",
        "positive_floor": None, "zero_rule": "An absent coordinate belongs to a smaller canonical support.",
        "continuous_real_domain": "x_i>0 and sum(x_i)=1; remains symbolic. Exact numeric APIs here accept rational values only.",
        "box_scope": "Closed rational component intervals intersected with strictly positive normalized coordinates. Zero-boundary-only solutions are rejected for that support.",
        "finite_export_rule": "CLI denominator and output caps limit generated samples only; an infinite or physical exhaustive enumeration is not claimed.",
        "finite_inventory_rule": "For primitive denominator q, exact atomic counts in a fixed N-atom inventory require q|N. Inventory compatibility is not material existence or controlled placement.",
        "old_model_preserved": "composition_ranges.py retains its deliberate 10^-19 coordinate floor and optional fixed grid.",
        "conditional_partition_rule": "Every isotope/state sub-count N*x_i*y_i,a,s must be an integer in a fixed classical inventory. Element-level compatibility alone is insufficient. Identifiers and physical state existence require separate evidence.",
    }


def examples() -> dict:
    denominator = 10**100
    below_floor = [Fraction(1, denominator), Fraction(denominator - 1, denominator)]
    tiny_interval = [(Fraction(1, 10**100), Fraction(1, 10**99)), (Fraction(10**99 - 1, 10**99), Fraction(10**100 - 1, 10**100))]
    witness = positive_box_witness(tiny_interval)
    return {
        "scope": DISCLAIMER,
        "below_selected_grid": record([1, 8], below_floor),
        "below_grid_exact_inventory": finite_inventory([1, 8], below_floor, denominator),
        "same_target_in_too_small_inventory": finite_inventory([1, 8], below_floor, 10**19),
        "nonterminating_thirds": record([1, 8], ["1/3", "2/3"]),
        "all_138_labels_equal": record(list(range(1, 139)), [Fraction(1, 138)] * 138),
        "rational_box_below_grid": {"bounds": [[str(low), str(high)] for low, high in tiny_interval], "witness": record([1, 8], witness)},
        "closure_only_box": {"bounds": [["0", "0"], ["1", "1"]], "positive_support_feasible": False, "reason": "Its zero coordinate requires a smaller support."},
        "one_assigned_trace_atom_uniform_subsample": {"inventory_atoms": str(10**19), "sampled_atoms": str(10**19 // 20), "sample_inclusion_probability_exact": str(one_trace_atom_subsample_inclusion_probability(10**19, 10**19 // 20)), "assumptions": "Exactly one assigned trace atom and uniform sampling without replacement. Detector efficiency and actual observation are not modeled."},
        "anonymous_conditional_partition_compatible": conditional_inventory([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], 6),
        "same_element_counts_but_partition_incompatible": conditional_inventory([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], 3),
    }


def verify() -> dict:
    if not __debug__:
        raise ValueError("Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    groups = []

    def passed(name: str, detail: str) -> None:
        groups.append({"test": name, "status": "passed", "evidence": detail})

    for denominator in (10**20, 10**100, 3 * 10**50):
        values = [Fraction(1, denominator), Fraction(denominator - 1, denominator)]
        assert validate([1, 8], values) == tuple(values)
        assert record([1, 8], values)["primitive_denominator"] == str(denominator)
    passed("coordinates_below_old_floor", "Exact denominators 10^20, 10^100 and 3*10^50; positive coordinates preserved without floor clipping.")

    for k in range(1, 139):
        result = record(list(range(1, k + 1)), [Fraction(1, k)] * k)
        assert result["primitive_numerators"] == ["1"] * k
        assert result["primitive_denominator"] == str(k)
    passed("all_support_cardinalities", "All sizes 1..138 independently checked against equal-count primitive vectors; hypothetical status retained.")

    for k in range(2, 5):
        expected = set()
        for q in range(1, 10):
            for counts in product(range(1, q + 1), repeat=k):
                if sum(counts) == q:
                    expected.add(tuple(Fraction(count, q) for count in counts))
        generated = list(rational_compositions(list(range(1, k + 1)), 9))
        assert len(generated) == len(set(generated)) and set(generated) == expected
    passed("primitive_enumeration", "Independent Cartesian enumeration of all positive count vectors, denominators 1..9, support sizes 2..4; repeated fractions deduplicated separately.")

    interval_options = [(Fraction(low, 4), Fraction(high, 4)) for low in range(5) for high in range(low, 5)]
    cases = 0
    for k in (2, 3):
        q = 4 * k
        vectors = [tuple(Fraction(value, q) for value in row) for row in product(range(1, q), repeat=k) if sum(row) == q]
        for bounds in product(interval_options, repeat=k):
            expected = any(all(low <= value <= high for value, (low, high) in zip(row, bounds)) for row in vectors)
            witness = positive_box_witness(bounds)
            assert (witness is not None) == expected
            if witness:
                assert sum(witness) == 1 and all(value > 0 and low <= value <= high for value, (low, high) in zip(witness, bounds))
            cases += 1
    assert cases == 3600
    passed("positive_box_boundary_and_feasibility", "3,600 quarter-endpoint boxes compared with independent positive Cartesian simplex vectors at denominators 8/12; includes strict-positive boundary cases.")

    cases = 0
    for k in (2, 3):
        for q in range(1, 9):
            vectors = [tuple(Fraction(value, q) for value in row) for row in product(range(1, q + 1), repeat=k) if sum(row) == q]
            for bounds in product(interval_options, repeat=k):
                expected = any(all(low <= value <= high for value, (low, high) in zip(row, bounds)) for row in vectors)
                witness = lattice_witness(bounds, q)
                assert (witness is not None) == expected
                if witness:
                    assert sum(witness) == 1 and all((value * q).denominator == 1 and low <= value <= high for value, (low, high) in zip(witness, bounds))
                cases += 1
    assert cases == 28800
    passed("arbitrary_lattice_box", "28,800 boxes/denominators independently checked against Cartesian count vectors; denominator is not tied to 10^19.")

    values = normalize([1, 6, 8], [2, 3, 5])
    assert values == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2))
    assert record([1, 6, 8], values)["primitive_numerators"] == ["2", "3", "5"]
    passed("normalization_and_canonical_counts", "Weights2:3:5 independently give primitive denominator10 and exact normalized coordinates.")

    for atoms in range(1, 25):
        result = finite_inventory([1, 6, 8], ["1/6", "1/3", "1/2"], atoms)
        assert result["count_compatible"] == (atoms % 6 == 0)
        if result["count_compatible"]:
            assert sum(int(value) for value in result["integer_counts"]) == atoms
    passed("finite_inventory_divisibility", "Inventory sizes1..24 checked independently against divisibility by primitive denominator6.")

    for atoms in range(1, 9):
        for sampled in range(atoms + 1):
            subsets = list(combinations(range(atoms), sampled))
            expected = Fraction(sum(0 in subset for subset in subsets), len(subsets))
            assert one_trace_atom_subsample_inclusion_probability(atoms, sampled) == expected
    passed("assigned_atom_subsampling", "Uniform subsets enumerated independently for inventories1..8; exactly one distinguished atom, sampling without replacement.")

    bad_calls = [lambda: validate([1, 8], [0, 1]), lambda: validate([1, 8], [-1, 2]), lambda: validate([1, 8], [0.5, 0.5]), lambda: validate([1, 1], ["1/2", "1/2"]), lambda: validate([1, 139], ["1/2", "1/2"]), lambda: validate([1], [True]), lambda: finite_inventory([1], [1], 0), lambda: positive_box_witness([(1, 0)]), lambda: one_trace_atom_subsample_inclusion_probability(3, 4)]
    for call in bad_calls:
        try:
            call()
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("Invalid input accepted")
    passed("invalid_inputs_rejected", "Nine negative/zero/inexact/duplicate/out-of-range/inventory/interval cases rejected.")

    from composition_ranges import validate_composition
    try:
        validate_composition([1, 8], [Fraction(1, 10**20), Fraction(10**20 - 1, 10**20)])
    except ValueError:
        pass
    else:
        raise AssertionError("Original bounded domain changed")
    assert positive_box_witness([(0, 1), (1, 1)]) is None
    assert positive_box_witness([("1/3", "1/3")] * 3) == (Fraction(1, 3),) * 3
    assert lattice_witness([("1/3", "1/3")] * 3, 10**19) is None
    passed("separate_domains_preserved", "Original floor restriction unchanged; closure-only vector rejected; thirds continuous/rational feasible but absent from the original fixed grid.")

    for atoms in range(1, 25):
        result = conditional_inventory([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], atoms)
        assert result["classical_partition_count_compatible"] == (atoms % 6 == 0)
        assert sum(Fraction(value) for row in result["partition_counts_exact"] for value in row) == atoms
    assert finite_inventory([1, 8], ["1/3", "2/3"], 3)["count_compatible"]
    assert not conditional_inventory([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], 3)["classical_partition_count_compatible"]
    passed("conditional_partition_inventory", "Inventories1..24 independently checked against the joint primitive denominator6; N=3 fits elemental counts but not their supplied classical sub-partitions.")
    return {"status": "passed", "test_group_count": len(groups), "tests": groups, "scope": DISCLAIMER, "exhaustive_unbounded_domain_tested": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("verify", "build", "describe"):
        subs.add_parser(name)
    generate = subs.add_parser("generate")
    generate.add_argument("--support", required=True)
    generate.add_argument("--max-denominator", type=int, required=True)
    generate.add_argument("--limit", type=int, required=True)
    args = parser.parse_args()
    if args.command == "build":
        root = Path(__file__).resolve().parent
        for filename, value in (("unrestricted_composition_model.json", model()), ("unrestricted_numeric_examples.json", examples()), ("unrestricted_verification_report.json", verify())):
            (root / filename).write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"status": "built", "scope": DISCLAIMER}))
    elif args.command == "verify":
        print(json.dumps(verify(), indent=2))
    elif args.command == "describe":
        print(json.dumps(model(), indent=2))
    else:
        support = [int(value) for value in args.support.split(",")]
        integer(args.limit, "limit", 1)
        values = [record(support, row) for row in islice(rational_compositions(support, args.max_denominator), args.limit)]
        print(json.dumps({"scope": DISCLAIMER, "finite_export": True, "max_denominator": args.max_denominator, "limit": args.limit, "compositions": values}, indent=2))


if __name__ == "__main__":
    main()
