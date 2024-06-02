import pandas as pd
import pytest

from trade.technicals.indicators.pivot_points.pivot_points import PivotPoints


@pytest.mark.parametrize(
    "ohlc",
    [
        {"open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5},
        {"open": 22568.10, "high": 22653.75, "low": 22465.10, "close": 22530.70},
    ],
)
def test_pivot_points_with_dict(ohlc):
    indicator = PivotPoints.apply_indicator(ohlc)
    assert isinstance(indicator, dict)


@pytest.mark.parametrize(
    "ohlc",
    [
        {
            "open": [10.0, 11.0, 12.0, 13.0, 14.0],
            "high": [11.0, 12.0, 13.0, 14.0, 15.0],
            "low": [9.0, 10.0, 11.0, 12.0, 13.0],
            "close": [10.5, 11.5, 12.5, 13.5, 14.5],
        },
        {
            "open": [23038.95, 22977.15, 22762.75, 22617.45, 22568.1],
            "high": [23110.8, 22998.55, 22825.5, 22705.75, 22653.75],
            "low": [22871.2, 22858.5, 22685.45, 22417.0, 22465.1],
            "close": [22932.45, 22888.15, 22704.7, 22488.65, 22530.7],
            "volume": [260000, 217900, 269900, 373400, 572100],
        },
    ],
)
def test_pivot_points_with_dataframe(ohlc):
    data = ohlc
    df = pd.DataFrame(data)
    indicator = PivotPoints.apply_indicator(df)
    assert isinstance(indicator, pd.DataFrame)


@pytest.mark.parametrize(
    "ohlc", [(10.0, 11.0, 9.0, 10.5), (22568.10, 22653.75, 22465.10, 22530.70)]
)
def test_pivot_points_with_ohlc_args(ohlc):
    result = PivotPoints.apply_indicator(ohlc)
    assert isinstance(result, dict)
