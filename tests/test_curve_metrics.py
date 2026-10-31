"""Synthetic analytical witnesses; no solver or experimental-data access."""
import copy
import math
import unittest
from atlas.curve_metrics import METHOD, compare_acquisition_linear


def case(x, errors):
    rows = [{"axial_strain": v, "q": 0.0} for v in x]
    prediction = {"status": "success", "points": [
        {"observation_index": i, "axial_strain": v, "q": e}
        for i, (v, e) in enumerate(zip(x, errors))]}
    return rows, prediction


def metric(x, errors, scale=1):
    return compare_acquisition_linear(*case(x, errors), "q", scale)


class OrderedCurveMetricTests(unittest.TestCase):
    def assertRelative(self, actual, expected):
        self.assertTrue(math.isclose(actual, expected, rel_tol=3e-15),
                        (actual, expected))

    def test_linear_residual_analytic_integral(self):
        result = metric([0, 1], [0, 1])
        self.assertEqual(result["method"], METHOD)
        self.assertRelative(result["scaled_mse"], 1/3)
        self.assertRelative(result["rmse"], math.sqrt(1/3))
        self.assertEqual(result["mae"], 0.5)
        self.assertEqual(result["max_abs"], 1)

    def test_sign_crossing_absolute_integral(self):
        result = metric([0, 1], [-1, 1])
        self.assertRelative(result["scaled_mse"], 1/3)
        self.assertRelative(result["mae"], 0.5)

    def test_redundant_sampling_preserves_linear_interpolant(self):
        for errors in ([0, 1], [-1, 1], [2, 1]):
            first = metric([0, 1], errors)
            second = metric([0, 0.5, 1], [errors[0], sum(errors)/2, errors[1]])
            for name in ("rmse", "mae", "scaled_mse", "max_abs"):
                self.assertRelative(first[name], second[name])
        # Historical endpoint quadrature changes with redundant linear sampling.
        self.assertEqual((0**2 + 1**2)/2, 0.5)
        self.assertEqual(0.5*(0**2+0.5**2)/2 + 0.5*(0.5**2+1**2)/2, 0.375)

    def test_reversal_uses_travel_not_net_strain(self):
        result = metric([0, 1, 0], [0, 1, 0])
        self.assertEqual(result["total_absolute_axial_strain_travel"], 2)
        self.assertRelative(result["scaled_mse"], 1/3)
        self.assertFalse(result["physical_time_weighted"])

    def test_holds_are_counted_and_maximum_includes_them(self):
        result = metric([0, 0, 1], [100, 0, 0])
        self.assertEqual(result["rmse"], 0)
        self.assertEqual(result["mae"], 0)
        self.assertEqual(result["max_abs"], 100)
        self.assertEqual(result["zero_travel_segments"], 1)
        self.assertEqual(result["zero_travel_residual_change_segments"], 1)
        with self.assertRaises(ValueError):
            metric([0, 0], [1, 2])

    def test_channel_units_and_scale_covary(self):
        a = metric([0, 1, 2], [-2, 3, 1], 4)
        b = metric([0, 1, 2], [-2000, 3000, 1000], 4000)
        self.assertRelative(a["scaled_mse"], b["scaled_mse"])
        for name in ("rmse", "mae", "max_abs"):
            self.assertRelative(1000*a[name], b[name])

    def test_coordinate_scaling_preserves_scores(self):
        a = metric([0, 1, 0], [0, 1, 0])
        b = metric([0, 100, 0], [0, 1, 0])
        self.assertRelative(a["rmse"], b["rmse"])
        self.assertRelative(a["mae"], b["mae"])
        self.assertEqual(b["total_absolute_axial_strain_travel"], 200)

    def test_large_finite_residual_does_not_square_prematurely(self):
        result = metric([0, 1], [1e200, 1e200], 1e200)
        self.assertRelative(result["rmse"], 1e200)
        self.assertRelative(result["mae"], 1e200)
        self.assertRelative(result["scaled_mse"], 1)

    def test_short_high_error_interval_keeps_contribution(self):
        result = metric([0, 1e-200, 1], [1e200, 0, 0], 1e100)
        self.assertRelative(result["scaled_mse"], 1/3)
        self.assertRelative(result["rmse"], 1e100/math.sqrt(3))
        self.assertRelative(result["mae"], 0.5)
        # Weight/total itself underflows, but the weighted error is representable.
        result = metric([0, 1e-200, 1e200], [1e200, 0, 0], 1)
        self.assertRelative(result["scaled_mse"], 1/3)
        self.assertRelative(result["mae"], 0.5e-200)

    def test_rejects_failed_partial_reordered_and_mismatched_predictions(self):
        for change in ("failed", "short", "index", "bool_index", "coordinate"):
            rows, prediction = case([0, 1], [0, 1])
            if change == "failed": prediction["status"] = "failed"
            if change == "short": prediction["points"].pop()
            if change == "index": prediction["points"][0]["observation_index"] = 1
            if change == "bool_index": prediction["points"][0]["observation_index"] = False
            if change == "coordinate": prediction["points"][1]["axial_strain"] = 0.5
            with self.subTest(change=change), self.assertRaises(ValueError):
                compare_acquisition_linear(rows, prediction, "q", 1)
        rows, prediction = case([2**53, 2**53+2], [0, 1])
        prediction["points"][0]["axial_strain"] = 2**53+1
        with self.assertRaises(ValueError):
            compare_acquisition_linear(rows, prediction, "q", 1)

    def test_rejects_invalid_values_and_nonrepresentable_results(self):
        for value in (True, None, "1", math.inf, math.nan, 10**400):
            for location in ("scale", "coordinate", "observed", "predicted"):
                rows, prediction = case([0, 1], [0, 1])
                scale = 1
                if location == "scale": scale = value
                if location == "coordinate": rows[0]["axial_strain"] = value
                if location == "observed": rows[0]["q"] = value
                if location == "predicted": prediction["points"][0]["q"] = value
                with self.subTest(value=value, location=location), self.assertRaises(ValueError):
                    compare_acquisition_linear(rows, prediction, "q", scale)
        for scale in (0, -1, 1e-300):
            with self.assertRaises(ValueError): metric([0, 1], [1, 1], scale)
        for x in ([-1e308, 1e308], [0, 1e308, 0]):
            with self.assertRaises(ValueError): metric(x, [0]*len(x))
        rows, prediction = case([0, 1], [1e308, 0])
        rows[0]["q"] = -1e308
        with self.assertRaises(ValueError):
            compare_acquisition_linear(rows, prediction, "q", 1)

    def test_inputs_unchanged(self):
        rows, prediction = case([0, 1], [0, 1])
        before = copy.deepcopy((rows, prediction))
        compare_acquisition_linear(rows, prediction, "q", 1)
        self.assertEqual((rows, prediction), before)


if __name__ == "__main__":
    unittest.main()
