"""
Unit tests for Problem 5: clean_and_aggregate

This test suite is provided as a complete reference suite.
Students can run this test suite to verify regression testing, and use it
to verify their Continuous Integration (CI) configuration in Task 2.

Running tests:
    python -m unittest test_problem5.py -v
"""
import unittest
from problem5 import clean_and_aggregate


class TestDataAggregator(unittest.TestCase):

    def setUp(self):
        """Prepare sample dataset for tests."""
        self.sample_sales = [
            {"region": "North", "rep": "Alice", "sales": 100.0, "active": True},
            {"region": "North", "rep": "Bob", "sales": 200.0, "active": True},
            {"region": "South", "rep": "Charlie", "sales": 150.0, "active": False},
            {"region": "South", "rep": "Diana", "sales": 350.0, "active": True},
            {"region": "East", "rep": "Evan", "sales": 500.0, "active": True},
            {"region": "East", "rep": "Fiona", "sales": None, "active": True},  # Null value to test cleaning
        ]

    def test_aggregate_mean_by_region(self):
        """Test calculating average sales by region."""
        result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="mean")
        expected = {
            "North": 150.0,  # (100 + 200) / 2
            "South": 250.0,  # (150 + 350) / 2
            "East": 500.0    # 500 / 1 (ignoring None)
        }
        self.assertDictEqual(result, expected)

    def test_aggregate_sum_by_region(self):
        """Test calculating sum of sales by region."""
        result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="sum")
        expected = {
            "North": 300.0,
            "South": 500.0,
            "East": 500.0
        }
        self.assertDictEqual(result, expected)

    def test_aggregate_min_and_max(self):
        """Test min and max aggregation operations."""
        min_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="min")
        max_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="max")

        self.assertAlmostEqual(min_result["North"], 100.0)
        self.assertAlmostEqual(max_result["North"], 200.0)
        self.assertAlmostEqual(min_result["South"], 150.0)
        self.assertAlmostEqual(max_result["South"], 350.0)

    def test_aggregate_count(self):
        """Test counting records with non-null metric values."""
        count_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="count")
        self.assertAlmostEqual(count_result["North"], 2.0)
        self.assertAlmostEqual(count_result["South"], 2.0)
        self.assertAlmostEqual(count_result["East"], 1.0)  # Fiona's None sales is skipped

    def test_filter_function(self):
        """Test filtering active representatives before aggregating."""
        result = clean_and_aggregate(
            self.sample_sales,
            group_by="region",
            metric="sales",
            aggregation="sum",
            filter_fn=lambda r: r.get("active") is True
        )
        # Charlie (South, 150) should be excluded
        self.assertAlmostEqual(result["South"], 350.0)
        self.assertAlmostEqual(result["North"], 300.0)

    def test_empty_dataset_raises_value_error(self):
        """Test that passing an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            clean_and_aggregate([], group_by="region", metric="sales")

    def test_invalid_input_types_raise_type_error(self):
        """Test that invalid types raise TypeError."""
        with self.assertRaises(TypeError):
            clean_and_aggregate("not a list", group_by="region", metric="sales")

        invalid_data = [{"region": "North", "sales": "one hundred"}]  # String instead of number
        with self.assertRaises(TypeError):
            clean_and_aggregate(invalid_data, group_by="region", metric="sales")

    def test_missing_keys_raise_value_error(self):
        """Test that missing dictionary keys raise ValueError."""
        invalid_data = [{"country": "USA", "revenue": 100}]
        with self.assertRaises(ValueError):
            clean_and_aggregate(invalid_data, group_by="region", metric="sales")

    def test_invalid_aggregation_operator_raises_value_error(self):
        """Test that unknown aggregation names raise ValueError."""
        with self.assertRaises(ValueError):
            clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="variance")


if __name__ == "__main__":
    unittest.main()
