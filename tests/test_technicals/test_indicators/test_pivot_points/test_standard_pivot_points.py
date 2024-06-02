import pandas as pd
import pytest

from trade.technicals.indicators.pivot_points.standard_pivot_points import (
    StandardPivotPoints,
)


def test_standard_pivot_points_properties():
    data = {
        "open": [10.0, 11.0, 12.0, 13.0, 14.0],
        "high": [11.0, 12.0, 13.0, 14.0, 15.0],
        "low": [9.0, 10.0, 11.0, 12.0, 13.0],
        "close": [10.5, 11.5, 12.5, 13.5, 14.5],
    }
    df = pd.DataFrame(data)
    pivot_points = StandardPivotPoints.apply_pivot_points(
        df["open"], df["high"], df["low"], df["close"]
    )
    assert pivot_points.pivot is not None
    assert pivot_points.bcpr is not None
    assert pivot_points.tcpr is not None
    assert pivot_points.cpr_width is not None
    assert pivot_points.cpr_classification is not None
    assert pivot_points.resistances is not None
    assert pivot_points.supports is not None


def test_standard_pivot_points_consolidate():
    data = {
        "open": [10.0, 11.0, 12.0, 13.0, 14.0],
        "high": [11.0, 12.0, 13.0, 14.0, 15.0],
        "low": [9.0, 10.0, 11.0, 12.0, 13.0],
        "close": [10.5, 11.5, 12.5, 13.5, 14.5],
    }
    df = pd.DataFrame(data)
    pivot_points = StandardPivotPoints(df["open"], df["high"], df["low"], df["close"])
    consolidated = pivot_points.consolidate()
    assert isinstance(consolidated, dict)
    assert "pivot" in consolidated
    assert "bcpr" in consolidated
    assert "tcpr" in consolidated
    assert "resistances" in consolidated
    assert "supports" in consolidated
    assert "length" in consolidated
    assert "cpr_width" in consolidated
    assert "cpr" in consolidated
