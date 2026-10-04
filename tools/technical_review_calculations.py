"""Recalculate the public technical review's bounded bookkeeping examples.

This module reads no files, accesses no network and imports no package code.
The caller provides the report and failure helper. Exact arithmetic checks
recorded input/output consistency, not the physical truth of a model's inputs.
"""
from __future__ import annotations

import ast
from decimal import Decimal, localcontext
from fractions import Fraction
from math import lcm
import re


def _fraction(value, require, context):
    require(type(value) in (int, str), f"{context}: expected an exact integer or fraction string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        require(False, f"{context}: invalid exact fraction")


def _vector(values, require, context):
    require(isinstance(values, list) and bool(values), f"{context}: missing vector")
    return tuple(_fraction(v, require, context) for v in values)


def _integer(value, require, context, minimum=0):
    result = _fraction(value, require, context)
    require(result.denominator == 1 and result >= minimum, f"{context}: invalid integer domain")
    return int(result)


def _same(value, expected, require, context):
    require(_fraction(value, require, context) == expected, f"{context}: recorded value differs")


def _same_vector(values, expected, require, context):
    require(_vector(values, require, context) == tuple(expected), f"{context}: recorded vector differs")


def _matrix(values, require, context):
    require(isinstance(values, list) and bool(values), f"{context}: missing matrix")
    rows = tuple(_vector(row, require, context) for row in values)
    require(len({len(row) for row in rows}) == 1, f"{context}: ragged matrix")
    return rows


def _same_matrix(values, expected, require, context):
    require(_matrix(values, require, context) == tuple(tuple(row) for row in expected),
            f"{context}: recorded matrix differs")


def _population(values, require, context):
    require(isinstance(values, list) and bool(values), f"{context}: missing population")
    return tuple(_integer(v, require, context) for v in values)


def _positive_profile(values, require, context):
    result = _vector(values, require, context)
    require(all(v > 0 for v in result) and sum(result) == 1,
            f"{context}: positive profile does not normalize")
    return result


def _conditional_profiles(values, require, context):
    result = _matrix(values, require, context) if len({len(row) for row in values}) == 1 else tuple(
        _vector(row, require, context) for row in values)
    require(bool(result) and all(all(v >= 0 for v in row) and sum(row) == 1 for row in result),
            f"{context}: conditional profile does not normalize")
    return result


def _joint_profile(atomic, profiles, require, context):
    require(len(atomic) == len(profiles), f"{context}: elemental and state profile lengths differ")
    return tuple(a * y for a, row in zip(atomic, profiles, strict=True) for y in row)


def _inventory(record, atomic, joint, require, context):
    total = _integer(record.get("N"), require, context, 1)
    elements = tuple(total * v for v in atomic)
    states = tuple(total * v for v in joint)
    _same_vector(record.get("elemental_counts"), elements, require, context)
    _same_vector(record.get("joint_state_counts"), states, require, context)
    require(record.get("elemental_count_compatible") is all(v.denominator == 1 for v in elements),
            f"{context}: elemental compatibility differs")
    require(record.get("joint_count_compatible") is all(v.denominator == 1 for v in states),
            f"{context}: joint compatibility differs")


def _affine(expression, variables, require, context):
    """Parse only rational affine arithmetic; never evaluate report source text."""
    require(isinstance(expression, str) and bool(expression), f"{context}: missing affine expression")
    # The report's displayed -2u notation is mathematically explicit but is not
    # Python syntax. Only numeric adjacency to these named variables is expanded.
    expression = re.sub(r"(\d)([uz])", r"\1*\2", expression)
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        require(False, f"{context}: invalid affine expression")
    size = len(variables) + 1

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return (Fraction(node.value),) + (Fraction(0),) * len(variables)
        if isinstance(node, ast.Name) and node.id in variables:
            return (Fraction(0),) + tuple(Fraction(int(node.id == name)) for name in variables)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            sign = -1 if isinstance(node.op, ast.USub) else 1
            return tuple(sign * v for v in value)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                sign = -1 if isinstance(node.op, ast.Sub) else 1
                return tuple(a + sign * b for a, b in zip(left, right, strict=True))
            if isinstance(node.op, ast.Mult):
                require(not any(left[1:]) or not any(right[1:]), f"{context}: nonlinear multiplication")
                return tuple(right[0] * v for v in left) if not any(right[1:]) else tuple(
                    left[0] * v for v in right)
            if isinstance(node.op, ast.Div):
                require(not any(right[1:]) and right[0] != 0, f"{context}: nonconstant divisor")
                return tuple(v / right[0] for v in left)
        require(False, f"{context}: unsupported affine expression")

    result = visit(tree.body)
    require(len(result) == size, f"{context}: affine coordinate count differs")
    return result


def _decimal(value, require, context):
    require(type(value) in (int, str), f"{context}: expected exact decimal input")
    result = Decimal(value)
    require(result.is_finite(), f"{context}: decimal is not finite")
    return result


def check(report, require) -> dict:
    rows = report.get("independent_calculation_checks", [])
    require([row.get("id") for row in rows] == [f"C{n:02d}" for n in range(1, 16)],
            "Technical calculation group inventory differs")
    groups = {row["id"]: row for row in rows}

    def fields(name):
        item = groups[name]
        context = f"Technical review arithmetic mismatch: {name}"
        require(item.get("result") == "passed" and isinstance(item.get("inputs"), dict)
                and isinstance(item.get("values"), dict), f"{context}: incomplete record")
        return item["inputs"], item["values"], context

    inp, out, ctx = fields("C01")
    counts = _population(inp["nominal_integer_vector_B_Si_P_Cr_Ni_Nb"], require, ctx)
    denominator = _integer(inp["normalization_denominator"], require, ctx, 1)
    require(all(n > 0 for n in counts) and sum(counts) == denominator, f"{ctx}: invalid nominal inventory")
    profile = tuple(Fraction(n, denominator) for n in counts)
    _same(out["sum"], sum(profile), require, ctx)
    _same(out["primitive_denominator"], lcm(*(v.denominator for v in profile)), require, ctx)

    inp, out, ctx = fields("C02")
    scale = _integer(inp["L"], require, ctx, 1)
    carbon = _integer(inp["carbon_count"], require, ctx, 1)
    principal = _integer(inp["equal_principal_count_each"], require, ctx, 1)
    size = _integer(inp["principal_categories"], require, ctx, 1)
    floor = _fraction(inp["positive_grid_floor"], require, ctx)
    require(principal == scale - 1 and floor > 0, f"{ctx}: inventory scale or floor differs")
    total = carbon + size * principal
    profile = (Fraction(carbon, total),) + (Fraction(principal, total),) * size
    require(profile[0] < floor, f"{ctx}: carbon is not below the selected floor")
    _same(out["carbon"], profile[0], require, ctx)
    _same(out["primitive_denominator"], lcm(*(v.denominator for v in profile)), require, ctx)

    inp, out, ctx = fields("C03")
    ti, oxygen = (_integer(inp[k], require, ctx, 1) for k in ("Ti_count", "O_count"))
    reference = _integer(inp["assumed_reference_O_sites"], require, ctx, 1)
    ti3, ti4 = (_integer(inp[k], require, ctx) for k in ("formal_TiIII_count", "formal_TiIV_count"))
    charge_o = _fraction(inp["formal_O_charge"], require, ctx)
    vacancy = reference - oxygen
    require(reference == 2 * ti and 0 <= vacancy < reference and ti3 + ti4 == ti
            and charge_o == -2, f"{ctx}: restricted host assumptions differ")
    charge = 3 * ti3 + 4 * ti4 + charge_o * oxygen
    require(charge == 0 and Fraction(ti3, ti) == 2 * Fraction(vacancy, ti),
            f"{ctx}: restricted charge model does not balance")
    _same_vector(out["atomic"], (Fraction(ti, ti + oxygen), Fraction(oxygen, ti + oxygen)), require, ctx)
    _same(out["vacancy_reference_fraction"], Fraction(vacancy, reference), require, ctx)
    _same(out["TiIII_fraction"], Fraction(ti3, ti), require, ctx)
    _same(out["formal_charge_sum"], charge, require, ctx)

    inp, out, ctx = fields("C04")
    formulas = (_population(inp["methoxy_formula_counts_C_H_N_O"], require, ctx),
                _population(inp["azide_formula_counts_C_H_N_O"], require, ctx))
    amounts = _vector(inp["nominal_input_amounts_micromol"], require, ctx)
    require(len(amounts) == 2 and all(v > 0 for v in amounts) and all(len(row) == 4 for row in formulas),
            f"{ctx}: monomer-only proportional input dimensions differ")
    counts = tuple(sum(amount * row[i] for amount, row in zip(amounts, formulas, strict=True)) for i in range(4))
    _same_vector(out["counts"], counts, require, ctx)
    _same(out["total"], sum(counts), require, ctx)

    inp, out, ctx = fields("C05")
    units = (_integer(inp["unsolvated_unit_count"], require, ctx),
             _integer(inp["dihydrate_unit_count"], require, ctx))
    formulas = (_population(inp["unsolvated_atom_counts_H_C_N_O"], require, ctx),
                _population(inp["dihydrate_atom_counts_H_C_N_O"], require, ctx))
    require(sum(units) > 0 and all(len(row) == 4 and sum(row) > 0 for row in formulas),
            f"{ctx}: molecular inventory has no positive denominator")
    counts = tuple(sum(n * row[i] for n, row in zip(units, formulas, strict=True)) for i in range(4))
    total = sum(counts)
    _same_vector(out["counts"], counts, require, ctx)
    _same(out["total"], total, require, ctx)
    _same(out["dihydrate_unit_fraction"], Fraction(units[1], sum(units)), require, ctx)
    _same(out["dihydrate_atom_weight"], Fraction(units[1] * sum(formulas[1]), total), require, ctx)
    _same_vector(out["atomic"], (Fraction(n, total) for n in counts), require, ctx)

    inp, out, ctx = fields("C06")
    lengths = _population(inp["conditional_chain_repeat_lengths"], require, ctx)
    population = _population(inp["conditional_chain_population"], require, ctx)
    require(len(lengths) == len(population) and all(n > 0 for n in lengths) and sum(population) > 0,
            f"{ctx}: finite chain population is invalid")
    chains, repeats = sum(population), sum(n * k for n, k in zip(lengths, population, strict=True))
    counts = (3 * repeats, 4 * repeats + 2 * chains, 2 * repeats + chains)
    _same(out["R"], repeats, require, ctx)
    _same(out["K"], chains, require, ctx)
    _same_vector(out["counts_C_H_O"], counts, require, ctx)
    _same(out["total"], sum(counts), require, ctx)
    population = _population(inp["separate_average_example_chain_population"], require, ctx)
    masses = _vector(inp["separate_average_example_masses"], require, ctx)
    require(len(population) == len(masses) and sum(population) > 0 and all(m > 0 for m in masses),
            f"{ctx}: average mass population is invalid")
    mass_sum = sum(k * m for k, m in zip(population, masses, strict=True))
    mn = mass_sum / sum(population)
    mw = sum(k * m * m for k, m in zip(population, masses, strict=True)) / mass_sum
    require(mw >= mn, f"{ctx}: weight/number average ordering differs")
    _same_vector(out["toy_chain_counts"], population, require, ctx)
    _same_vector(out["toy_masses"], masses, require, ctx)
    _same(out["Mn"], mn, require, ctx)
    _same(out["Mw"], mw, require, ctx)

    inp, out, ctx = fields("C07")
    linkers = _integer(inp["L"], require, ctx)
    available = _integer(inp["available_host_groups_A"], require, ctx)
    populations = tuple(_population(row, require, ctx) for row in inp["populations_B_C_P_U"])
    consumed = []
    for population in populations:
        require(len(population) == 4 and sum(population) == linkers, f"{ctx}: linker partition differs")
        bridges, loops, pendant, _ = population
        ends = 2 * bridges + 2 * loops + pendant
        require(ends <= min(available, 2 * linkers) and bridges <= min(linkers, available // 2),
                f"{ctx}: linker end constraints fail")
        consumed.append(ends)
    _same_matrix(out["populations"], populations, require, ctx)
    _same(out["L"], linkers, require, ctx)
    _same_vector(out["consumed_ends"], consumed, require, ctx)

    inp, out, ctx = fields("C08")
    masses = _vector(inp["input_masses"], require, ctx)
    factors = _vector(inp["retained_factors"], require, ctx)
    densities = _vector(inp["densities"], require, ctx)
    void = _fraction(inp["void_volume"], require, ctx)
    require(len(masses) == len(factors) == len(densities) and all(m >= 0 for m in masses)
            and all(0 <= h <= 1 for h in factors) and all(rho > 0 for rho in densities) and void >= 0,
            f"{ctx}: retention/additive-volume domain differs")
    retained = tuple(m * h for m, h in zip(masses, factors, strict=True))
    require(sum(retained) > 0, f"{ctx}: retained total is zero")
    volumes = tuple(m / rho for m, rho in zip(retained, densities, strict=True))
    total_volume = sum(volumes) + void
    _same_vector(out["retained_mass"], retained, require, ctx)
    _same_vector(out["mass_fractions"], (m / sum(retained) for m in retained), require, ctx)
    _same_vector(out["densities"], densities, require, ctx)
    _same(out["void_volume"], void, require, ctx)
    _same_vector(out["constituent_volume_fractions"], (v / total_volume for v in volumes), require, ctx)
    _same(out["void_fraction"], void / total_volume, require, ctx)

    inp, out, ctx = fields("C09")
    directions = _matrix(inp["unit_directions"], require, ctx)
    weights = _vector(inp["normalized_weights"], require, ctx)
    require(len(directions) == len(weights) and all(w >= 0 for w in weights) and sum(weights) == 1
            and all(len(row) == 3 and sum(v * v for v in row) == 1 for row in directions),
            f"{ctx}: orientation directions or weights differ")
    tensor = tuple(tuple(sum(w * u[i] * u[j] for w, u in zip(weights, directions, strict=True))
                         for j in range(3)) for i in range(3))
    _same_vector(out["diagonal"], (tensor[i][i] for i in range(3)), require, ctx)
    _same(out["trace"], sum(tensor[i][i] for i in range(3)), require, ctx)
    require(out["symmetric"] is all(tensor[i][j] == tensor[j][i] for i in range(3) for j in range(3))
            and out["positive_semidefinite"] is True, f"{ctx}: tensor invariant differs")
    # Positive semidefiniteness follows exactly: v^T A v = sum w*(v.u)^2 >= 0.

    inp, out, ctx = fields("C10")
    totals = _population(inp["stock_atom_totals"], require, ctx)
    profiles = _conditional_profiles(inp["conditional_state_profiles"], require, ctx)
    require(len(totals) == len(profiles) and sum(totals) > 0 and len({len(row) for row in profiles}) == 1,
            f"{ctx}: stock profile dimensions differ")
    contributions = tuple(tuple(n * y for y in row) for n, row in zip(totals, profiles, strict=True))
    require(all(v.denominator == 1 for row in contributions for v in row), f"{ctx}: stock sub-count is not integral")
    counts = tuple(sum(row[i] for row in contributions) for i in range(len(profiles[0])))
    _same_vector(out["stock_totals"], totals, require, ctx)
    _same_matrix(out["stock_profiles"], profiles, require, ctx)
    _same_vector(out["state_counts"], counts, require, ctx)
    _same_vector(out["conditional_profile"], (n / sum(totals) for n in counts), require, ctx)

    inp, out, ctx = fields("C11")
    atomic = _positive_profile(inp["elemental_atomic"], require, ctx)
    profiles = _conditional_profiles(inp["within_element_conditional_states"], require, ctx)
    joint = _joint_profile(atomic, profiles, require, ctx)
    require(inp["inventory_totals"] == [2, 4], f"{ctx}: inventory example totals differ")
    _same(out["elemental_primitive_denominator"], lcm(*(v.denominator for v in atomic)), require, ctx)
    _same(out["joint_primitive_denominator"], lcm(*(v.denominator for v in joint)), require, ctx)
    for total in (2, 4):
        _same_vector(out[f"N{total}_elemental_counts"], (total * v for v in atomic), require, ctx)
        _same_vector(out[f"N{total}_joint_counts"], (total * v for v in joint), require, ctx)

    inp, out, ctx = fields("C12")
    population = _population(inp["excitation_counts"], require, ctx)
    energies = inp["per_excitation_energies"]
    require(isinstance(energies, list) and len(energies) == len(population), f"{ctx}: energy population lengths differ")
    parsed = tuple(None if value is None else _fraction(value, require, ctx) for value in energies)
    require(all(energy is not None and energy > 0 for n, energy in zip(population, parsed, strict=True) if n > 0),
            f"{ctx}: populated excitation energy is unresolved")
    energy = sum(n * eps for n, eps in zip(population, parsed, strict=True) if n > 0)
    require(energy > 0, f"{ctx}: energy-share denominator is zero")
    shares = tuple(n * eps / energy if n > 0 else Fraction(0) for n, eps in zip(population, parsed, strict=True))
    _same_vector(out["populations"], population, require, ctx)
    require(len(out["energies"]) == len(parsed), f"{ctx}: recorded energy vector lengths differ")
    for recorded, value in zip(out["energies"], parsed, strict=True):
        require(recorded is None, f"{ctx}: unknown zero-population energy was supplied") if value is None else _same(recorded, value, require, ctx)
    _same(out["E_exc"], energy, require, ctx)
    _same_vector(out["energy_shares"], shares, require, ctx)

    inp, out, ctx = fields("C13")
    p_model = _affine(inp["P"], ("u", "z"), require, ctx)
    z_model = _affine(inp["z"], ("u",), require, ctx)
    displayed = out["model"]
    require(isinstance(displayed, str) and displayed.startswith("P(u,z)=") and ", z(u)=" in displayed,
            f"{ctx}: recorded model notation differs")
    displayed_p, displayed_z = displayed[len("P(u,z)="):].split(", z(u)=")
    require(_affine(displayed_p, ("u", "z"), require, ctx) == p_model
            and _affine(displayed_z, ("u",), require, ctx) == z_model, f"{ctx}: recorded model differs")
    direct, linked = p_model[1], p_model[2] * z_model[1]
    _same(out["direct_derivative"], direct, require, ctx)
    _same(out["linked_derivative"], linked, require, ctx)
    _same(out["total_derivative"], direct + linked, require, ctx)

    inp, out, ctx = fields("C14")
    bounds = _matrix(inp["deterministic_mass_bounds"], require, ctx)
    require(len(bounds) == 2 and all(len(row) == 2 and 0 < row[0] <= row[1] for row in bounds),
            f"{ctx}: complete positive bound categories differ")
    lower, upper = tuple(row[0] for row in bounds), tuple(row[1] for row in bounds)
    normalized_bounds = tuple((lower[i] / (lower[i] + sum(upper[j] for j in range(2) if j != i)),
                               upper[i] / (upper[i] + sum(lower[j] for j in range(2) if j != i))) for i in range(2))
    masses = _vector(inp["separate_local_mass_point"], require, ctx)
    covariance = _matrix(inp["separate_input_covariance"], require, ctx)
    require(len(masses) == 2 and all(m > 0 for m in masses) and len(covariance) == 2
            and all(len(row) == 2 for row in covariance) and covariance[0][1] == covariance[1][0]
            and covariance[0][0] >= 0 and covariance[1][1] >= 0
            and covariance[0][0] * covariance[1][1] - covariance[0][1] * covariance[1][0] >= 0,
            f"{ctx}: local mass/covariance domain differs")
    total = sum(masses)
    fractions = tuple(m / total for m in masses)
    jacobian = tuple(tuple((Fraction(int(i == j)) - fractions[i]) / total for j in range(2)) for i in range(2))
    propagated = tuple(tuple(sum(jacobian[i][k] * covariance[k][col] * jacobian[j][col]
                                for k in range(2) for col in range(2)) for j in range(2)) for i in range(2))
    _same_matrix(out["input_bounds"], bounds, require, ctx)
    _same_matrix(out["fraction_bounds"], normalized_bounds, require, ctx)
    _same_vector(out["mass_point"], masses, require, ctx)
    _same_matrix(out["input_covariance"], covariance, require, ctx)
    _same_matrix(out["J"], jacobian, require, ctx)
    _same_matrix(out["fraction_covariance"], propagated, require, ctx)
    _same_matrix(out["percent_covariance"], tuple(tuple(10000 * v for v in row) for row in propagated), require, ctx)

    inp, out, ctx = fields("C15")
    require(inp["decimal_working_precision"] == 40 and bool(inp.get("precision_qualification")),
            f"{ctx}: source precision qualification differs")
    with localcontext() as decimal_context:
        decimal_context.prec = 40
        atoms = _integer(inp["atom_inventory"], require, ctx, 1)
        avogadro = _decimal(inp["Avogadro_constant_per_mol"], require, ctx)
        require(avogadro == Decimal("6.02214076e23"), f"{ctx}: SI Avogadro constant differs")
        threshold = _decimal(inp["numerical_wt_percent_threshold"], require, ctx)
        prefactor = _decimal(inp["source_fit_numerical_wt_percent_prefactor"], require, ctx)
        exponent = _decimal(inp["source_fit_exponent"], require, ctx)
        scale = _decimal(inp["fraction_coordinate_scale"], require, ctx)
        require(threshold >= 0 and prefactor > 0 and scale == 100, f"{ctx}: percent-coordinate domain differs")
        moles = Decimal(atoms) / avogadro
        converted_prefactor = prefactor * scale ** exponent
        require(_decimal(out["mol_for_1e19_atoms"], require, ctx) == moles
                and _decimal(out["fraction_coordinate_prefactor_S_per_m"], require, ctx) == converted_prefactor,
                f"{ctx}: recorded decimal conversion differs")
        _same(out["electrical_threshold_fraction"], Fraction(threshold) / Fraction(scale), require, ctx)

    vectors = report.get("structured_test_vectors", {})
    require(set(vectors) == {"joint_isotope_counts", "whole_molecular_units"},
            "Technical structured inventory vector inventory differs")
    vector = vectors["joint_isotope_counts"]
    ctx = "Technical review joint inventory mismatch"
    atomic = _positive_profile(vector["elemental_atomic"], require, ctx)
    profiles = _conditional_profiles(vector["within_element_state_atomic"], require, ctx)
    joint = _joint_profile(atomic, profiles, require, ctx)
    require(atomic == _vector(groups["C11"]["inputs"]["elemental_atomic"], require, ctx)
            and profiles == _conditional_profiles(groups["C11"]["inputs"]["within_element_conditional_states"], require, ctx),
            f"{ctx}: calculation group inputs differ")
    _same_vector(vector["joint_atomic"], joint, require, ctx)
    _same(vector["elemental_primitive_denominator"], lcm(*(v.denominator for v in atomic)), require, ctx)
    _same(vector["joint_primitive_denominator"], lcm(*(v.denominator for v in joint)), require, ctx)
    require([case.get("N") for case in vector["inventories"]] == [2, 4], f"{ctx}: inventory totals differ")
    for case in vector["inventories"]:
        _inventory(case, atomic, joint, require, ctx)

    vector = vectors["whole_molecular_units"]
    ctx = "Technical review whole-unit inventory mismatch"
    require(vector["formula"] == "C6H6" and vector["element_order"] == ["H", "C"],
            f"{ctx}: attributed formula/order differs")
    counts = _population(vector["atom_counts_per_intact_unit"], require, ctx)
    require(counts == (6, 6), f"{ctx}: C6H6 unit counts differ")
    total_unit = sum(counts)
    atomic = tuple(Fraction(n, total_unit) for n in counts)
    _same(vector["atoms_per_intact_unit"], total_unit, require, ctx)
    _same_vector(vector["elemental_atomic"], atomic, require, ctx)
    _same(vector["elemental_primitive_denominator"], lcm(*(v.denominator for v in atomic)), require, ctx)
    require([case.get("N") for case in vector["inventories"]] == [2, 12, 24], f"{ctx}: inventory totals differ")
    for case in vector["inventories"]:
        total = _integer(case["N"], require, ctx, 1)
        elements = tuple(total * v for v in atomic)
        molecules = Fraction(total, total_unit)
        _same_vector(case["elemental_counts"], elements, require, ctx)
        _same(case["molecule_count"], molecules, require, ctx)
        require(case["elemental_count_compatible"] is all(v.denominator == 1 for v in elements)
                and case["whole_molecule_count_compatible"] is (molecules.denominator == 1),
                f"{ctx}: recorded inventory compatibility differs")
    return {"groups_checked": 15, "structured_inventory_examples_checked": 5,
            "exact_rational_groups": 14, "decimal_group_working_precision": 40,
            "recorded_input_output_consistency_checked": True,
            "physical_or_legal_outcome_certified": False}
