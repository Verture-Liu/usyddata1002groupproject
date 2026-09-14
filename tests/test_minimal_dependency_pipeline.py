import ast
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SCRIPTS = [
    ROOT / "src/download_open_meteo_wind.py",
    ROOT / "src/clean_open_meteo_wind.py",
    ROOT / "src/analyse_wind.py",
]
DELIVERED_SCRIPTS = [
    ROOT / "final_state/download_open_meteo_wind.py",
    ROOT / "final_state/clean_open_meteo_wind.py",
    ROOT / "final_state/analyse_wind.py",
]
FORBIDDEN_IMPORTS = {"numpy", "requests", "bs4", "lxml"}
EXPECTED_FINAL_FILES = {
    "analyse_wind.py",
    "clean_open_meteo_wind.py",
    "download_open_meteo_wind.py",
    "figure1_windgustspeed_by_raintomorrow.png",
    "figure2_windgust_groups_by_season.png",
    "wind_descriptive_summary_by_season_outcome.csv",
    "wind_descriptive_summary_overall.csv",
    "wind_gust_group_rainfall_rates_by_season.csv",
    "wind_sydney_analysis.csv",
    "wind_sydney_clean.csv",
}


def imported_top_level_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    return imported


class MinimalDependencyTests(unittest.TestCase):
    def test_active_scripts_have_no_forbidden_imports(self):
        for path in ACTIVE_SCRIPTS + DELIVERED_SCRIPTS:
            with self.subTest(path=path.name):
                imported = imported_top_level_modules(path)
                self.assertFalse(imported & FORBIDDEN_IMPORTS)

    def test_only_pandas_and_matplotlib_are_direct_requirements(self):
        requirements = {
            line.strip()
            for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertEqual(
            requirements, {"matplotlib==3.7.5", "pandas==1.5.3"}
        )

    def test_cleaned_data_contract(self):
        data = pd.read_csv(ROOT / "final_state/wind_sydney_clean.csv")
        parsed = pd.to_datetime(data["Date"], format="%Y-%m-%d")

        self.assertEqual(len(data), 2556)
        self.assertTrue(data["Date"].is_unique)
        self.assertTrue(
            data["Date"].str.fullmatch(
                r"\d{4}-(?:[1-9]|1[0-2])-(?:[1-9]|[12]\d|3[01])"
            ).all()
        )
        self.assertEqual(parsed.min().date().isoformat(), "2016-01-01")
        self.assertEqual(parsed.max().date().isoformat(), "2022-12-30")
        self.assertEqual(
            set(data["Season"]), {"summer", "autumn", "winter", "spring"}
        )
        self.assertLessEqual(set(data["RainTomorrow"]), {0, 1})
        self.assertFalse(
            data[
                [
                    "Date",
                    "Season",
                    "RainTomorrow",
                    "WindGustSpeed",
                    "WindSpeed9am",
                    "WindSpeed3pm",
                ]
            ].isna().any().any()
        )

    def test_final_state_inventory(self):
        actual = {path.name for path in (ROOT / "final_state").iterdir()}
        self.assertEqual(actual, EXPECTED_FINAL_FILES)

    def test_final_figures_are_nonempty_png_files(self):
        for name in [
            "figure1_windgustspeed_by_raintomorrow.png",
            "figure2_windgust_groups_by_season.png",
        ]:
            path = ROOT / "final_state" / name
            with self.subTest(name=name):
                self.assertGreater(path.stat().st_size, 10_000)
                self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


class DownloaderTests(unittest.TestCase):
    def test_fetch_uses_urlopen_and_returns_response_bytes(self):
        from src.download_open_meteo_wind import fetch

        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"csv-content"
        with patch(
            "src.download_open_meteo_wind.urlopen", return_value=response
        ) as mocked_urlopen:
            self.assertEqual(fetch({"format": "csv"}), b"csv-content")

        requested_url = mocked_urlopen.call_args.args[0]
        self.assertIn("format=csv", requested_url)
        self.assertEqual(mocked_urlopen.call_args.kwargs["timeout"], 180)


class CleanerTests(unittest.TestCase):
    def test_compass_converts_cardinal_directions_and_missing_values(self):
        from src.clean_open_meteo_wind import compass

        self.assertEqual(compass(0), "N")
        self.assertEqual(compass(90), "E")
        self.assertEqual(compass(180), "S")
        self.assertEqual(compass(270), "W")
        self.assertTrue(pd.isna(compass(pd.NA)))


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_mean_is_deterministic_and_finite(self):
        from src.analyse_wind import bootstrap_mean

        values = pd.Series(range(20), dtype=float)
        first = bootstrap_mean(values, seed=123)
        second = bootstrap_mean(values, seed=123)
        self.assertEqual(first, second)
        self.assertTrue(all(pd.notna(value) for value in first))

    def test_bootstrap_median_difference_is_deterministic_and_finite(self):
        from src.analyse_wind import bootstrap_median_difference

        first = bootstrap_median_difference(
            pd.Series(range(20), dtype=float),
            pd.Series(range(5, 25), dtype=float),
            seed=456,
        )
        second = bootstrap_median_difference(
            pd.Series(range(20), dtype=float),
            pd.Series(range(5, 25), dtype=float),
            seed=456,
        )
        self.assertEqual(first, second)
        self.assertTrue(all(pd.notna(value) for value in first))

    def test_bootstrap_returns_missing_bounds_for_small_samples(self):
        from src.analyse_wind import bootstrap_mean, bootstrap_median_difference

        mean_bounds = bootstrap_mean(pd.Series(range(9), dtype=float), seed=1)
        difference_bounds = bootstrap_median_difference(
            pd.Series(range(9), dtype=float),
            pd.Series(range(10), dtype=float),
            seed=1,
        )
        self.assertTrue(all(pd.isna(value) for value in mean_bounds))
        self.assertTrue(all(pd.isna(value) for value in difference_bounds))


if __name__ == "__main__":
    unittest.main()
