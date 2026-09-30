"""Independent bounded adversarial oracles for the unrestricted supplement."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import json
import random
import sys

MODULE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_ROOT))
import unrestricted_compositions as target


def vertices(bounds):
    """Intersect box edges with sum(x)=1 without the target's greedy algorithm."""
    clipped = [(max(Fraction(0), Fraction(lo)), min(Fraction(1), Fraction(hi))) for lo, hi in bounds]
    if any(lo > hi for lo, hi in clipped):
        return []
    found = set()
    for free in range(len(clipped)):
        fixed = [i for i in range(len(clipped)) if i != free]
        for choices in product((0, 1), repeat=len(fixed)):
            row = [Fraction(0)] * len(clipped)
            for i, choice in zip(fixed, choices):
                row[i] = clipped[i][choice]
            row[free] = 1 - sum(row)
            if all(lo <= x <= hi for x, (lo, hi) in zip(row, clipped)):
                found.add(tuple(row))
    return sorted(found)


def positive_oracle(bounds):
    rows = vertices(bounds)
    # A bounded nonempty polytope is a convex hull of its vertices. If each
    # coordinate is positive at some vertex, their average is strictly positive.
    return bool(rows) and all(any(row[i] > 0 for row in rows) for i in range(len(bounds)))


def positive_integer_rows(q, k):
    """Count tuples from separator positions, independent of recursive generation."""
    if q < k:
        return
    for cuts in combinations(range(1, q), k - 1):
        walls = (0,) + cuts + (q,)
        yield tuple(walls[i + 1] - walls[i] for i in range(k))


def run():
    rng = random.Random(20260930)
    continuous_cases = lattice_cases = enumeration_cases = 0
    regressions = [
        [(0, 1)], [(0, 0)], [(2, 3)], [(-3, -2)],
        [(0, 1), (1, 1)], [("1/3", "1/3")] * 3,
        [(0, "1/3"), (0, "1/3"), (0, "1/3")],
        [("1/4", "1/4"), ("3/4", 1)],
        [(0, 0), ("1/3", 1), ("2/3", 1)],
        [(Fraction(1, 10**200), Fraction(1, 10**199)), (0, 1)],
        [(Fraction(1, 10**200), Fraction(1, 10**200)),
         (1 - Fraction(1, 10**200), 1 - Fraction(1, 10**200))],
        [(0, 1)] * 138,
    ]
    for bounds in regressions:
        witness = target.positive_box_witness(bounds)
        expected = True if len(bounds) == 138 else positive_oracle(bounds)
        assert (witness is not None) == expected, bounds
        if witness is not None:
            assert sum(witness) == 1 and all(x > 0 and Fraction(lo) <= x <= Fraction(hi) for x, (lo, hi) in zip(witness, bounds))
        continuous_cases += 1
    for k in range(1, 7):
        for _ in range(300):
            bounds = []
            for __ in range(k):
                q = rng.choice((3, 7, 11, 13))
                lo, hi = sorted((Fraction(rng.randrange(-q, 2 * q + 1), q), Fraction(rng.randrange(-q, 2 * q + 1), q)))
                bounds.append((lo, hi))
            expected = positive_oracle(bounds)
            witness = target.positive_box_witness(bounds)
            assert (witness is not None) == expected, (bounds, witness, expected)
            if witness is not None:
                assert sum(witness) == 1 and all(x > 0 and lo <= x <= hi for x, (lo, hi) in zip(witness, bounds))
            continuous_cases += 1
    for k in range(1, 5):
        for q in range(1, 16):
            rows = [tuple(Fraction(n, q) for n in row) for row in positive_integer_rows(q, k)]
            for _ in range(40):
                bounds = []
                for __ in range(k):
                    denominator = rng.choice((3, 7, 11))
                    lo, hi = sorted((Fraction(rng.randrange(-denominator, 2 * denominator + 1), denominator), Fraction(rng.randrange(-denominator, 2 * denominator + 1), denominator)))
                    bounds.append((lo, hi))
                expected = any(all(lo <= x <= hi for x, (lo, hi) in zip(row, bounds)) for row in rows)
                witness = target.lattice_witness(bounds, q)
                assert (witness is not None) == expected, (bounds, q, witness)
                if witness is not None:
                    assert sum(witness) == 1 and all(x > 0 and (x * q).denominator == 1 and lo <= x <= hi for x, (lo, hi) in zip(witness, bounds))
                lattice_cases += 1
    for k in range(1, 7):
        expected = set()
        for q in range(1, 17):
            expected.update(tuple(Fraction(n, q) for n in row) for row in positive_integer_rows(q, k))
        actual = list(target.rational_compositions(list(range(1, k + 1)), 16))
        assert set(actual) == expected and len(actual) == len(expected)
        for row in actual:
            item = target.record(list(range(1, k + 1)), row)
            primitive = int(item["primitive_denominator"])
            assert tuple(Fraction(int(n), primitive) for n in item["primitive_numerators"]) == row
            for atoms in (primitive, 2 * primitive, primitive + 1):
                assert target.finite_inventory(list(range(1, k + 1)), row, atoms)["count_compatible"] == (atoms % primitive == 0)
        enumeration_cases += len(actual)
    conditional_cases = 0
    conditional_regressions = [
        ([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], 6, True),
        ([1, 8], ["1/3", "2/3"], [["1/2", "1/2"], ["1/4", "3/4"]], 3, False),
        ([1], [1], [[0, "1/3", "2/3"]], 3, True),
        ([1], [1], [[0, "1/3", "2/3"]], 2, False),
        ([1], [1], [[0, 1, 0]], 1, True),
    ]
    for support, elemental, partitions, atoms, compatible in conditional_regressions:
        result = target.conditional_inventory(support, elemental, partitions, atoms)
        assert result["classical_partition_count_compatible"] == compatible
        assert result["species_or_state_existence_established"] is False
        parsed = [[Fraction(value) for value in row] for row in result["partition_counts_exact"]]
        assert [sum(row) for row in parsed] == [atoms * Fraction(value) for value in elemental]
        assert sum(sum(row) for row in parsed) == atoms
        conditional_cases += 1
    for _ in range(600):
        k = rng.randrange(1, 5)
        elemental_counts = [rng.randrange(1, 9) for __ in range(k)]
        elemental_total = sum(elemental_counts)
        elemental = [Fraction(value, elemental_total) for value in elemental_counts]
        partitions = []
        joint = []
        for x in elemental:
            state_counts = [rng.randrange(0, 9) for __ in range(rng.randrange(1, 5))]
            if not any(state_counts):
                state_counts[0] = 1
            total = sum(state_counts)
            row = [Fraction(value, total) for value in state_counts]
            partitions.append(row)
            joint.extend(x * value for value in row)
        # Independent integer-multiple oracle for the flattened joint fractions.
        common = 1
        from math import lcm
        for value in joint:
            common = lcm(common, value.denominator)
        for atoms in (common, common + 1, 2 * common):
            result = target.conditional_inventory(list(range(1, k + 1)), elemental, partitions, atoms)
            assert result["classical_partition_count_compatible"] == (atoms % common == 0)
            parsed = [[Fraction(value) for value in row] for row in result["partition_counts_exact"]]
            assert [sum(row) for row in parsed] == [atoms * value for value in elemental]
            assert sum(sum(row) for row in parsed) == atoms
            conditional_cases += 1
    bad_partitions = [
        lambda: target.conditional_inventory([1], [1], [], 1),
        lambda: target.conditional_inventory([1], [1], [[]], 1),
        lambda: target.conditional_inventory([1], [1], [["1/3", "1/3"]], 1),
        lambda: target.conditional_inventory([1], [1], [[-1, 2]], 1),
        lambda: target.conditional_inventory([1], [1], [[True]], 1),
        lambda: target.conditional_inventory([1], [1], [[0.5, 0.5]], 1),
        lambda: target.conditional_inventory([1], [1], [[1]], 0),
        lambda: target.conditional_inventory([1, 8], [0, 1], [[1], [1]], 3),
    ]
    for call in bad_partitions:
        try:
            call()
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("Invalid conditional partition accepted")
    probability_cases = 0
    for population in range(1, 11):
        for sample_size in range(population + 1):
            subsets = list(combinations(range(population), sample_size))
            expected = Fraction(sum(0 in subset for subset in subsets), len(subsets))
            assert target.one_trace_atom_subsample_inclusion_probability(population, sample_size) == expected
            probability_cases += 1
    return {
        "status": "passed",
        "positive_box_cases": continuous_cases,
        "lattice_box_cases": lattice_cases,
        "primitive_vectors_and_inventory_checks": enumeration_cases,
        "joint_conditional_partition_cases": conditional_cases,
        "invalid_conditional_partition_cases_rejected": len(bad_partitions),
        "single_atom_uniform_subset_cases": probability_cases,
        "methods": ["box/simplex vertices and convex averages", "integer separator positions", "explicit uniform subsets"],
        "seed": 20260930,
        "scope": "Independent finite adversarial evidence; no exhaustive unbounded or physical claim",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
