"""Reproduce bounded arithmetic evidence for the prospective claim clarifications.

These checks use exact fractions, anonymous toy masses and independent separator
tuples. They do not establish material preparation, measured properties, legal
support or exhaustive coverage of an infinite domain. Importing writes nothing;
the direct-script CLI prints a deterministic JSON report without creating files.
"""

from fractions import Fraction
from itertools import combinations, product
from math import lcm
from pathlib import Path
import json
import sys

MODULE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_ROOT))
# Match the existing independent checker: fixture callers load this exact sibling.
import unrestricted_compositions as target  # noqa: E402


class VerificationError(RuntimeError):
    """An explicit check failed; checks are not removable Python assertions."""


class UnresolvedMassError(ValueError):
    """A positively populated state lacks a qualified numerical mass."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def exact(value):
    if isinstance(value, bool) or not isinstance(value, (Fraction, int, str)):
        raise TypeError("Use exact Fraction, integer or fraction-string inputs.")
    return Fraction(value)


def checked_bounds(bounds):
    values = tuple((exact(lo), exact(hi)) for lo, hi in bounds)
    if not values or any(not 0 <= lo <= hi <= 1 for lo, hi in values):
        raise ValueError("A nonempty box requires 0 <= L_i <= U_i <= 1.")
    return values


def residual_allocation(lower, upper, total):
    """Allocate a feasible residual; exact Fractions and integers both work."""
    result = list(lower)
    remaining = total - sum(result)
    require(remaining >= 0, "Lower bounds already exceed the required total.")
    require(all(lo <= hi for lo, hi in zip(lower, upper)), "Empty coordinate bounds.")
    for index, ceiling in enumerate(upper):
        allocated = min(remaining, ceiling - result[index])
        result[index] += allocated
        remaining -= allocated
    require(remaining == 0, "Upper bounds cannot absorb the required residual.")
    return tuple(result)


def preliminary_witness(bounds):
    """Claim 191's closed-box witness; zero coordinates remain preliminary."""
    values = checked_bounds(bounds)
    lower, upper = zip(*values)
    if sum(lower) > 1 or sum(upper) < 1:
        return None
    return residual_allocation(lower, upper, Fraction(1))


def epsilon_witness(bounds):
    """Use the preserved claim 192 epsilon, raising every lower bound."""
    values = checked_bounds(bounds)
    lower, upper = zip(*values)
    lower_sum = sum(lower)
    if lower_sum > 1 or sum(upper) < 1 or any(hi <= 0 for hi in upper):
        return None
    if lower_sum == 1:
        return tuple(lower) if all(lo > 0 for lo in lower) else None
    epsilon = min(min(upper), (1 - lower_sum) / (2 * len(values)))
    raised = tuple(max(lo, epsilon) for lo in lower)
    require(epsilon > 0, "A positive-support epsilon must be positive.")
    require(sum(raised) <= (1 + lower_sum) / 2 < 1, "Epsilon slack bound failed.")
    require(all(lo <= hi for lo, hi in zip(raised, upper)), "Raised lower exceeds upper.")
    result = residual_allocation(raised, upper, Fraction(1))
    check_positive_witness(result, values)
    return result


def positive_integer_rows(denominator, size):
    """Expected positive tuples from separators, independent of either allocator."""
    for cuts in combinations(range(1, denominator), size - 1):
        walls = (0,) + cuts + (denominator,)
        yield tuple(walls[i + 1] - walls[i] for i in range(size))


def check_positive_witness(witness, bounds, denominator=None):
    require(len(witness) == len(bounds), "Wrong witness dimension.")
    require(sum(witness) == 1, "Witness does not normalize exactly.")
    require(all(value > 0 for value in witness), "Witness has a nonpositive coordinate.")
    require(all(lo <= value <= hi for value, (lo, hi) in zip(witness, bounds)),
            "Witness falls outside its stated bounds.")
    if denominator is not None:
        require(all((value * denominator).denominator == 1 for value in witness),
                "Witness is not on the selected integer lattice.")


def grid_integer_witness(bounds, denominator):
    """Claim 193's positive-count cap, acceptance test and residual integers."""
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator < 1:
        raise ValueError("The accounting denominator must be a positive integer.")
    values = checked_bounds(bounds)
    lower = [max(1, -(-(denominator * lo).numerator // (denominator * lo).denominator))
             for lo, _ in values]
    upper = [min(denominator - len(values) + 1,
                 (denominator * hi).numerator // (denominator * hi).denominator)
             for _, hi in values]
    if (any(lo > hi for lo, hi in zip(lower, upper))
            or sum(lower) > denominator or sum(upper) < denominator):
        return None
    counts = residual_allocation(lower, upper, denominator)
    require(all(isinstance(value, int) and value >= 1 for value in counts),
            "The grid witness lacks positive integer counts.")
    fractions = tuple(Fraction(value, denominator) for value in counts)
    check_positive_witness(fractions, values, denominator)
    return counts


def conditional_mass_distribution(populations, masses):
    """Sum only positive populations; an omitted zero-state mass is never read.

    The mapping keys are anonymous state indices. Missing/None populated masses
    stay unresolved through an explicit exception, rather than a fabricated zero.
    """
    atoms = tuple(exact(value) for value in populations)
    if not atoms or any(value < 0 for value in atoms) or sum(atoms) != 1:
        raise ValueError("Conditional atom populations must be nonnegative and sum to one.")
    weighted = [Fraction(0)] * len(atoms)
    for index, population in enumerate(atoms):
        if population == 0:
            continue
        if index not in masses or masses[index] is None:
            raise UnresolvedMassError("A positively populated state has an unknown mass.")
        mass = exact(masses[index])
        if mass <= 0:
            raise ValueError("Populated state masses must be positive.")
        weighted[index] = population * mass
    effective_mass = sum(weighted)
    require(effective_mass > 0, "Effective mass is not positive.")
    conditional_mass = tuple(value / effective_mass for value in weighted)
    require(sum(conditional_mass) == 1, "Conditional mass fractions do not normalize.")
    return effective_mass, conditional_mass


def serialized(values):
    return [str(value) for value in values]


def verify_epsilon_boxes(intervals):
    cases = feasible = 0
    by_size = []
    for size in range(1, 4):
        expected_rows = tuple(tuple(Fraction(n, 12) for n in row)
                              for row in positive_integer_rows(12, size))
        size_cases = size_feasible = 0
        for bounds in product(intervals, repeat=size):
            # Independent positive vectors are produced only by separator cuts.
            expected = any(all(lo <= value <= hi for value, (lo, hi) in zip(row, bounds))
                           for row in expected_rows)
            proposed = epsilon_witness(bounds)
            production = target.positive_box_witness(bounds)
            require((proposed is not None) == expected,
                    f"Epsilon/oracle feasibility differs for {bounds!r}.")
            require((production is not None) == expected,
                    f"Production/oracle feasibility differs for {bounds!r}.")
            for witness in (proposed, production):
                if witness is not None:
                    check_positive_witness(witness, bounds)
            size_cases += 1
            size_feasible += int(expected)
        cases += size_cases
        feasible += size_feasible
        by_size.append({"k": size, "boxes": size_cases, "feasible": size_feasible,
                        "oracle_positive_vectors": len(expected_rows)})
    require(cases == 3615 and feasible == 1318, "Previously reported epsilon counts differ.")
    return cases, feasible, by_size


def verify_grid_boxes(intervals):
    cases = 0
    by_denominator = []
    for denominator in range(2, 9):
        denominator_cases = 0
        for size in range(1, min(3, denominator) + 1):
            expected_rows = tuple(positive_integer_rows(denominator, size))
            for bounds in product(intervals, repeat=size):
                expected = any(all(lo <= Fraction(n, denominator) <= hi
                                   for n, (lo, hi) in zip(row, bounds))
                               for row in expected_rows)
                counts = grid_integer_witness(bounds, denominator)
                production = target.lattice_witness(bounds, denominator)
                require((counts is not None) == expected,
                        f"Grid/oracle feasibility differs at D={denominator}, {bounds!r}.")
                require((production is not None) == expected,
                        f"Production lattice/oracle differs at D={denominator}, {bounds!r}.")
                if counts is not None:
                    require(counts in expected_rows, "Grid counts absent from independent tuples.")
                if production is not None:
                    check_positive_witness(production, bounds, denominator)
                denominator_cases += 1
        cases += denominator_cases
        by_denominator.append({"D": denominator, "boxes": denominator_cases})
    require(cases == 21930, "Previously reported integer-grid count differs.")
    return cases, by_denominator


def verify_boundaries():
    zero, one = Fraction(0), Fraction(1)
    examples = [
        ("fixed_binary_zero", ((zero, zero), (one, one)), None),
        ("binary_unconstrained", ((zero, one), (zero, one)),
         (Fraction(3, 4), Fraction(1, 4))),
        ("binary_mixed_lower_half", ((zero, Fraction(1, 2)), (Fraction(1, 2), one)),
         (Fraction(1, 2), Fraction(1, 2))),
        ("fixed_binary_thirds", ((Fraction(1, 3), Fraction(1, 3)),
                                 (Fraction(2, 3), Fraction(2, 3))),
         (Fraction(1, 3), Fraction(2, 3))),
        ("prior_tiny_upper_10^-50", ((zero, Fraction(1, 10**50)), (zero, one)),
         (Fraction(1, 10**50), one - Fraction(1, 10**50))),
        ("ancillary_tiny_10^-100_to_10^-99",
         ((Fraction(1, 10**100), Fraction(1, 10**99)), (zero, one)),
         (Fraction(1, 10**99), one - Fraction(1, 10**99))),
        ("138_unconstrained", ((zero, one),) * 138,
         (Fraction(139, 276),) + (Fraction(1, 276),) * 137),
        ("zero_upper_in_positive_support", ((zero, zero), (Fraction(1, 3), one)), None),
        ("three_lower_bounds_2/5", ((Fraction(2, 5), one),) * 3, None),
    ]
    records = []
    for name, bounds, expected in examples:
        preliminary = preliminary_witness(bounds)
        proposed = epsilon_witness(bounds)
        production = target.positive_box_witness(bounds)
        require(proposed == expected, f"Boundary epsilon result changed for {name}.")
        require((production is not None) == (expected is not None),
                f"Boundary production feasibility changed for {name}.")
        if production is not None:
            check_positive_witness(production, bounds)
        if preliminary is not None:
            require(sum(preliminary) == 1 and all(value >= 0 for value in preliminary),
                    f"Invalid preliminary witness for {name}.")
            require(all(lo <= value <= hi for value, (lo, hi) in zip(preliminary, bounds)),
                    f"Out-of-bounds preliminary witness for {name}.")
        if len(bounds) == 138:
            record = {"case": name, "k": 138, "epsilon": "1/276",
                      "first_coordinate": str(proposed[0]),
                      "remaining_coordinate": str(proposed[1]), "remaining_count": 137,
                      "sum": str(sum(proposed)), "positive_feasible": True}
        else:
            record = {"case": name, "bounds": [serialized(pair) for pair in bounds],
                      "preliminary": serialized(preliminary) if preliminary is not None else None,
                      "positive_witness": serialized(proposed) if proposed is not None else None,
                      "positive_feasible": proposed is not None}
        if name == "fixed_binary_thirds":
            require(grid_integer_witness(bounds, 10**19) is None,
                    "Exact thirds unexpectedly entered the decimal grid.")
            record["on_D_10^19_grid"] = False
        records.append(record)
    # The reported 21,930-case matrix intentionally excludes k>D. Check that
    # omitted infeasible stratum separately rather than inflating its old count.
    oversized = ((zero, one),) * 3
    require(not tuple(positive_integer_rows(2, 3)), "Positive D=2,k=3 tuples exist.")
    require(grid_integer_witness(oversized, 2) is None,
            "A positive three-count inventory fit a total of two.")
    require(target.lattice_witness(oversized, 2) is None,
            "Production accepted a positive D=2,k=3 lattice.")
    positive = epsilon_witness(oversized)
    require(positive == (Fraction(2, 3), Fraction(1, 6), Fraction(1, 6)),
            "The continuously feasible oversized-grid example changed.")
    records.append({"case": "integer_grid_k_exceeds_D", "k": 3, "D": 2,
                    "independent_positive_tuple_count": 0, "grid_feasible": False,
                    "positive_continuous_witness": serialized(positive),
                    "counted_in_integer_grid_matrix": False})
    return records


def verify_isotope_examples():
    atomic = (Fraction(4, 5), Fraction(1, 5))
    populations = ((Fraction(1, 2), Fraction(1, 2)), (Fraction(1),))
    masses = ({0: Fraction(1), 1: Fraction(2)}, {0: Fraction(3)})
    distributions = tuple(conditional_mass_distribution(row, mass)
                          for row, mass in zip(populations, masses))
    effective = tuple(item[0] for item in distributions)
    total_mass = sum(value * mass for value, mass in zip(atomic, effective))
    elemental_mass = tuple(value * mass / total_mass for value, mass in zip(atomic, effective))
    whole_atomic = tuple(value * population for value, row in zip(atomic, populations)
                         for population in row)
    whole_mass = tuple(value * fraction for value, (_, row) in zip(elemental_mass, distributions)
                       for fraction in row)
    inverse_total = sum(value / mass for value, mass in zip(elemental_mass, effective))
    inverse = tuple((value / mass) / inverse_total
                    for value, mass in zip(elemental_mass, effective))
    # Independent five-atom inventory: state counts (2,2,1), per-atom masses (1,2,3).
    expected_counts = (2, 2, 1)
    expected_masses = tuple(n * mass for n, mass in zip(expected_counts, (1, 2, 3)))
    require(whole_atomic == tuple(Fraction(n, 5) for n in expected_counts),
            "Atomic state fractions disagree with the independent toy inventory.")
    require(whole_mass == tuple(Fraction(mass, 9) for mass in expected_masses),
            "Mass state fractions disagree with the independent toy inventory.")
    require(effective == (Fraction(3, 2), Fraction(3)), "Toy effective masses changed.")
    require(elemental_mass == (Fraction(2, 3), Fraction(1, 3)), "Toy elemental mass changed.")
    require(inverse == atomic and sum(whole_atomic) == sum(whole_mass) == 1,
            "Toy normalization or inverse conversion failed.")
    for element, (_, row) in enumerate(distributions):
        require(sum(elemental_mass[element] * value for value in row) == elemental_mass[element],
                "State mass fractions fail to sum to their elemental fraction.")
    zero_entry_masses = {1: Fraction(3)}
    require(0 not in zero_entry_masses, "Zero-population regression must omit its mass key.")
    require(conditional_mass_distribution((0, 1), zero_entry_masses)
            == (Fraction(3), (Fraction(0), Fraction(1))),
            "An omitted zero-population mass was evaluated or fabricated.")
    unknown_cases = [("populated_mass_omitted", {}), ("populated_mass_None", {0: None})]
    for name, mass in unknown_cases:
        try:
            conditional_mass_distribution((1,), mass)
        except UnresolvedMassError:
            pass
        else:
            raise VerificationError(f"Unknown populated mass was accepted: {name}.")
    return {
        "evidence_status": "CALCULATED anonymous toy masses; no measured isotope data",
        "elemental_atomic": serialized(atomic), "effective_masses": serialized(effective),
        "elemental_mass": serialized(elemental_mass),
        "first_element_conditional_mass": serialized(distributions[0][1]),
        "whole_atomic_states": serialized(whole_atomic), "whole_mass_states": serialized(whole_mass),
        "inverse_elemental_atomic": serialized(inverse), "independent_atom_counts": list(expected_counts),
        "independent_allocated_masses": list(expected_masses),
        "unknown_mass_cases": [
            {"case": "zero_population_mass_omitted", "outcome": "not evaluated; fraction zero"},
            *({"case": name, "outcome": "UnresolvedMassError"} for name, _ in unknown_cases),
        ],
    }


def verify_basis_count_regressions(isotope):
    """Check both native bases and the atom-count denominator, using toy masses.

    These two examples are separate from the earlier box, boundary and missing-
    mass counts. They add no physical masses or experimental inventories.
    """
    atomic = tuple(exact(value) for value in isotope["elemental_atomic"])
    elemental_mass = tuple(exact(value) for value in isotope["elemental_mass"])
    masses = tuple(exact(value) for value in isotope["effective_masses"])
    atomic_mass_total = sum(value * mass for value, mass in zip(atomic, masses))
    forward = tuple(value * mass / atomic_mass_total for value, mass in zip(atomic, masses))
    mass_atom_total = sum(value / mass for value, mass in zip(elemental_mass, masses))
    inverse = tuple((value / mass) / mass_atom_total
                    for value, mass in zip(elemental_mass, masses))
    require(forward == elemental_mass and inverse == atomic,
            "Qualified-mass conversion failed in one of the two native bases.")
    native_branches = []
    for basis, x, corresponding in (("atomic", atomic, forward),
                                     ("mass", elemental_mass, inverse)):
        require(sum(x) == sum(corresponding) == 1,
                "A native-basis branch fails exact normalization.")
        require(x == (atomic if basis == "atomic" else elemental_mass),
                "The generic x coordinate does not match its identified basis.")
        native_branches.append({"native_basis": basis, "x": serialized(x),
                                "other_basis": "mass" if basis == "atomic" else "atomic",
                                "converted_fractions": serialized(corresponding)})
    # Unequal masses make the prior accidental mass-as-atomic substitution visible.
    wrong_total = sum(value * mass for value, mass in zip(elemental_mass, masses))
    wrong = tuple(value * mass / wrong_total for value, mass in zip(elemental_mass, masses))
    require(wrong == (Fraction(1, 2), Fraction(1, 2)) and wrong != elemental_mass,
            "The unequal-mass regression no longer detects the wrong substitution.")
    basis_record = {"case": "qualified_mass_conversion_both_native_bases",
                    "effective_toy_masses": serialized(masses), "branches": native_branches,
                    "mass_as_atomic_wrong_result": serialized(wrong),
                    "wrong_result_differs_from_native_mass": True}

    mass_target = (Fraction(1, 2), Fraction(1, 2))
    toy_masses = (Fraction(1), Fraction(2))
    total_atoms_per_mass = sum(value / mass for value, mass in zip(mass_target, toy_masses))
    atom_target = tuple((value / mass) / total_atoms_per_mass
                        for value, mass in zip(mass_target, toy_masses))
    mass_denominator = lcm(*(value.denominator for value in mass_target))
    atom_denominator = lcm(*(value.denominator for value in atom_target))
    require(atom_target == (Fraction(2, 3), Fraction(1, 3))
            and mass_denominator == 2 and atom_denominator == 3,
            "The distinct mass/atomic denominator example changed.")
    inventory_records = []
    for total, expected in ((2, False), (3, True)):
        counts = tuple(total * value for value in atom_target)
        compatible = all(value.denominator == 1 for value in counts)
        require(compatible == expected == (total % atom_denominator == 0),
                "Atomic-count compatibility used the wrong basis denominator.")
        require((total % mass_denominator == 0) != compatible,
                "The toy inventory fails to distinguish the mass denominator.")
        # These support IDs are bookkeeping inputs; toy masses are not their
        # physical chemical masses. Compare only the production count operation.
        production = target.finite_inventory([1, 2], atom_target, total)
        require(production["count_compatible"] == compatible,
                "Production atomic inventory differs from exact toy counts.")
        inventory_records.append({"N": total, "target_atom_counts": serialized(counts),
                                  "atomic_count_compatible": compatible,
                                  "mass_denominator_divides_N": total % mass_denominator == 0})
    count_record = {"case": "rational_mass_denominator_is_not_atom_count_denominator",
                    "mass_target": serialized(mass_target),
                    "qualified_toy_masses": serialized(toy_masses),
                    "converted_atomic_target": serialized(atom_target),
                    "mass_primitive_denominator": mass_denominator,
                    "atomic_primitive_denominator": atom_denominator,
                    "inventories": inventory_records}
    return [basis_record, count_record]


def verify():
    if not __debug__:
        raise VerificationError("Run without -O, -OO or PYTHONOPTIMIZE; production checks use assertions.")
    endpoints = tuple(Fraction(index, 4) for index in range(5))
    intervals = tuple((lo, hi) for lo in endpoints for hi in endpoints if lo <= hi)
    require(len(intervals) == 15, "Quarter-endpoint interval selection changed.")
    epsilon_cases, feasible, by_size = verify_epsilon_boxes(intervals)
    grid_cases, by_denominator = verify_grid_boxes(intervals)
    boundaries = verify_boundaries()
    isotope = verify_isotope_examples()
    basis_count = verify_basis_count_regressions(isotope)
    return {
        "status": "passed", "evidence_status": "CALCULATED",
        "epsilon_box_cases": epsilon_cases, "epsilon_feasible_boxes": feasible,
        "integer_grid_cases": grid_cases, "boundary_cases": len(boundaries),
        "isotope_unknown_mass_cases": len(isotope["unknown_mass_cases"]),
        "basis_count_regression_cases": len(basis_count),
        "enumeration": {
            "endpoints": serialized(endpoints), "closed_intervals": len(intervals),
            "epsilon_box_domain": "All products of the 15 intervals for k=1,2,3",
            "epsilon_count_identity": "15 + 15^2 + 15^3 = 3615",
            "positive_oracle_denominator": 12, "epsilon_by_k": by_size,
            "integer_grid_domain": "D=2..8; k=1..min(3,D); all products of the same intervals",
            "integer_count_identity": "7*(15 + 15^2 + 15^3) - 15^3 = 21930",
            "integer_by_D": by_denominator,
        },
        "methods": ["preserved epsilon = min(min U, (1-sum L)/(2k)); raise every lower bound",
                    "independent positive tuples from separator positions, not greedy allocation",
                    "cross-check the current separate positive and arbitrary-lattice allocators",
                    "claim 193 positive-count cap, integer inequalities and residual construction",
                    "anonymous five-atom inventory; omitted zero-state and unresolved populated masses",
                    "separate anonymous native-basis conversion and atomic-count denominator regressions"],
        "boundaries": boundaries, "isotope_example": isotope,
        "basis_count_regressions": basis_count,
        "scope": "Bounded exact arithmetic only; no exhaustive infinite domain, physical preparation, "
                 "measured property, application support, patentability or legal effect established.",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
