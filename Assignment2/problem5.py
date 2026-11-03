"""
Problem 5: Data Pipeline Aggregator (Developped by AI)
"""
from typing import List, Dict, Any, Optional, Callable


def clean_and_aggregate(
    records: List[Dict[str, Any]],
    group_by: str,
    metric: str,
    aggregation: str = "mean",
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> Dict[str, float]:
    """
    Filter, clean, and aggregate a list of dictionary records by a grouping key.

    Args:
        records (List[Dict[str, Any]]): List of records (each record is a dict).
        group_by (str): The dictionary key to group records by.
        metric (str): The numeric dictionary key to aggregate.
        aggregation (str): Aggregation function: "sum", "mean", "min", "max", or "count".
        filter_fn (Optional[Callable]): Optional predicate function to filter records before aggregation.

    Returns:
        Dict[str, float]: Aggregated dictionary mapping group names to calculated float metrics.

    Raises:
        ValueError: If records is empty, invalid aggregation type, or keys missing from records.
        TypeError: If records is not a list or metric values are not numeric.
    """

    valid_aggregations = {"sum", "mean", "min", "max", "count"}
    agg_op = aggregation.lower()
    if agg_op not in valid_aggregations:
        raise ValueError(f"Invalid aggregation '{aggregation}'. Must be one of {valid_aggregations}")
    if not records:
        raise ValueError("Records cannot be empty")

    # Group data
    grouped_values: Dict[str, List[float]] = {}

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise TypeError(f"Record at index {i} must be a dictionary")
        if group_by not in record:
            raise ValueError(f"Record at index {i} is missing group_by key: '{group_by}'")
        if metric not in record:
            raise ValueError(f"Record at index {i} is missing metric key: '{metric}'")

        # Apply optional filter
        if filter_fn is not None and not filter_fn(record):
            continue

        raw_val = record[metric]
        if raw_val is None:
            continue  # Skip None / missing values

        if not isinstance(raw_val, (int, float)) or isinstance(raw_val, bool):
            raise TypeError(f"Metric value '{raw_val}' in record {i} is not numeric")

        group_key = str(record[group_by])
        if group_key not in grouped_values:
            grouped_values[group_key] = []
        grouped_values[group_key].append(float(raw_val))

    # Compute aggregations
    results: Dict[str, float] = {}
    for group_key, values in grouped_values.items():
        if not values:
            continue
        if agg_op == "sum":
            val = sum(values)
        elif agg_op == "mean":
            val = sum(values) / len(values)
        elif agg_op == "min":
            val = min(values)
        elif agg_op == "max":
            val = max(values)
        elif agg_op == "count":
            val = len(values)
        else:
            val = 0.0

        results[group_key] = round(val, 2)

    return results
