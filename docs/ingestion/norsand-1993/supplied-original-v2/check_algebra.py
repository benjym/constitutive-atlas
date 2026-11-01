"""Source algebra only; no Atlas model import, production evaluator or trajectory."""
from decimal import Decimal as Q, localcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
POLICY = json.loads((BASE / "algebra-policy.json").read_text())


def power(x, a):
    if x <= 0:
        raise ValueError("nonpositive power base")
    return (a * x.ln()).exp()


def yield_eta(r, m, n):
    if r <= 0 or m <= 0 or not 0 <= n < 1:
        raise ValueError("yield domain")
    if n == 0:
        return m * (1 + r.ln())
    return m / n * (1 - (1 - n) * power(1 / r, n / (1 - n)))


def inverse(eta, m, n):
    if m <= 0 or not 0 <= n < 1:
        raise ValueError("inverse domain")
    if n == 0:
        return (eta / m - 1).exp()
    return power((1 - n * eta / m) / (1 - n), (n - 1) / n)


def limiting(psi, m, n):
    if m <= 0 or not 0 <= n < 1:
        raise ValueError("limit domain")
    if n == 0:
        return (-Q("3.5") * psi / m).exp()
    return power(1 + Q("3.5") * psi * n / m, (n - 1) / n)


def run(precision):
    with localcontext() as ctx:
        ctx.prec = precision
        tol = Q(POLICY["algebra_absolute_tolerance"])
        counts = {}
        maxima = {}

        def close(group, actual, expected, bound=tol):
            err = abs(actual - expected)
            assert err <= bound, (group, str(actual), str(expected), str(err))
            counts[group] = counts.get(group, 0) + 1
            maxima[group] = max(maxima.get(group, Q(0)), err)

        for n in map(Q, POLICY["N_values"]):
            for m in map(Q, POLICY["M_values"]):
                for factor in map(Q, POLICY["eta_over_M"]):
                    eta = m * factor
                    r = inverse(eta, m, n)
                    close("yield_inverse", yield_eta(r, m, n), eta)
                    # Differentiate Eq7 q=p*eta at fixed image pressure,
                    # separately from the source's Eq6 normality expression.
                    y = Q(1) if n == 0 else power(1 / r, n / (1 - n))
                    dq_dp = eta - m * y
                    close("normality", -dq_dp, (m - eta) / (1 - n))
                close("image_condition", inverse(m, m, n), Q(1))
                for psi in map(Q, POLICY["psi_i"]):
                    eta_l = yield_eta(limiting(psi, m, n), m, n)
                    close("limiting_flow", (m - eta_l) / (1 - n), Q("3.5") * psi)
                for p in map(Q, POLICY["p_Pa"]):
                    for lam in map(Q, POLICY["lambda_values"]):
                        gamma, e, pref = Q("0.9"), Q("0.65"), Q("1000")
                        r = inverse(m / 2, m, n)
                        ec_p = gamma - lam * (p / pref).ln()
                        ec_i = gamma - lam * (p * r / pref).ln()
                        close("image_CSL", e - ec_i, e - ec_p + lam * r.ln())
                        # Change numerical pressure reference without changing e_c.
                        gamma_pa = gamma + lam * Q(1000).ln()
                        close("pressure_reference", ec_p, gamma_pa - lam * p.ln())

        for n in [Q("1e-8"), Q("1e-12")]:
            m, psi, eta, r = Q("1.25"), Q("-0.1"), Q("0.5"), Q("0.6")
            for name, a, b in [
                ("zero_limit_yield", yield_eta(r, m, n), yield_eta(r, m, Q(0))),
                ("zero_limit_inverse", inverse(eta, m, n), inverse(eta, m, Q(0))),
                ("zero_limit_LHL", limiting(psi, m, n), limiting(psi, m, Q(0))),
            ]:
                close(name, a, b, Q(POLICY["N_zero_limit_scaled_tolerance_factor"]) * n)

        # Central derivative through an independently solved implicit yield+
        # cell constraint. This is a local algebra probe, not path integration.
        probe = {k: Q(v) for k, v in POLICY["constant_cell_probe"].items()}
        n, m, eta, cell = (probe[k] for k in ["N", "M", "eta", "cell_Pa"])
        r = inverse(eta, m, n)
        p = cell / (1 - eta / 3)
        pi = p * r
        delta = probe["log_pi_perturbation"]

        def solve_eta(target_pi):
            value = eta
            for _ in range(15):
                pressure = cell / (1 - value / 3)
                ratio = inverse(value, m, n)
                y_local = power(1 / ratio, n / (1 - n))
                residual = (pressure * ratio / target_pi).ln()
                # d log(pi)/d eta follows implicit yield+cell equations.
                derivative = 1 / (3 - value) + 1 / (m * y_local)
                value -= residual / derivative
            return value

        fd = (solve_eta(pi * delta.exp()) - solve_eta(pi * (-delta).exp())) / (2 * delta)
        y = power(1 / r, n / (1 - n))
        analytic = m * y * (3 - eta) / (3 - eta + m * y)
        close("constant_cell_implicit_derivative", fd, analytic, Q(POLICY["derivative_absolute_tolerance"]))
        pi_rate_over_pi = probe["h"] * (limiting(probe["psi_i"], m, n) / r - 1)
        close("constant_cell_Eq12", analytic * pi_rate_over_pi,
              (3 - eta) * (m * y * pi_rate_over_pi) / (3 - eta + m * y))

        # Exact rational witness, independent of Decimal power implementation.
        r0 = F(4, 5) ** 4
        assert r0 == F(256, 625) and str(Q(r0.numerator) / Q(r0.denominator)) == "0.4096"
        counts["exact_NC_ratio"] = 1
        D0 = F(5, 4) / (1 - F(1, 5))
        assert D0 == F(25, 16) and D0 != 0  # arbitrary isochoric strain witness
        counts["mixed_control_witness"] = 1
        s1, s3, de1, de3 = F(170000), F(110000), F(3, 1000), F(-1, 2000)
        pressure, shear = (s1 + 2 * s3) / 3, s1 - s3
        ev, eq = de1 + 2 * de3, F(2, 3) * (de1 - de3)
        assert s1 * de1 + 2 * s3 * de3 == pressure * ev + shear * eq
        assert de1 == ev / 3 + eq and de3 == ev / 3 - eq / 2
        counts["exact_work_conjugacy"] = 3

        invalid = [lambda: yield_eta(Q(0), Q(1), Q(".2")),
                   lambda: inverse(Q(1), Q(0), Q(".2")),
                   lambda: inverse(Q(1), Q(1), Q(1)),
                   lambda: inverse(Q(1), Q(1), Q("-.1")),
                   lambda: inverse(Q(5), Q(1), Q(".2")),
                   lambda: inverse(Q(6), Q(1), Q(".2")),
                   lambda: limiting(Q(-2), Q(1), Q(".2"))]
        for call in invalid:
            try:
                call()
            except ValueError:
                pass
            else:
                raise AssertionError("invalid algebra domain accepted")
        counts["invalid_algebra_domain"] = len(invalid)
        return {"precision": precision, "checks": counts, "total": sum(counts.values()),
                "maximum_absolute_errors": {k: str(v) for k, v in maxima.items()},
                "constant_cell_derivative": str(analytic), "NC_pi_over_p": "0.4096"}


if __name__ == "__main__":
    print(json.dumps({"ok": True,
                      "policy_sha256": hashlib.sha256((BASE / "algebra-policy.json").read_bytes()).hexdigest(),
                      "runs": [run(n) for n in POLICY["precisions"]],
                      "candidate_or_backend_executed": False}, indent=2))
