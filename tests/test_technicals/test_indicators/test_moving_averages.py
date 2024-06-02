import pytest
import pandas as pd
from pandas import DataFrame
import pandas_ta as ta

from trade.technicals.indicators.moving_averges import (
    MovingAverages,
    MOVING_AVERAGE_INTS_TYPE,
    MOVING_AVERAGES,
    TYPICAL_MOVING_AVERAGES,
    INVALID_MOVING_AVERAGES,
    CROSSOVERS,
)


@pytest.fixture(scope='module')
def sample_data():
    data = {'open': [10, 12, 11, 13, 14, 15, 16, 17, 18, 19],
            'high': [12, 14, 13, 15, 16, 17, 18, 19, 20, 21],
            'low': [9, 11, 10, 12, 13, 14, 15, 16, 17, 18],
            'close': [11, 13, 12, 14, 15, 16, 17, 18, 19, 20]}
    return pd.DataFrame(data)


def test_init(sample_data):
    ma = "EMA"
    on_col = "close"
    ma_range = (10, 20, 50)

    indicator = MovingAverages(sample_data, ma, on_col, ma_range)

    assert indicator.data.equals(sample_data)
    assert indicator.ma == ma
    assert indicator.on_col == on_col
    assert indicator.ma_range == ma_range


def test_add_moving_averages_ema(sample_data):
    ma = "EMA"
    on_col = "close"
    ma_range = (10, 20, 50)

    indicator = MovingAverages(sample_data, ma, on_col, ma_range)
    result = indicator.add_moving_averages()

    assert isinstance(result, pd.DataFrame)
    assert result.shape == sample_data.shape
    assert all(col in result.columns for col in [f"{ma}{i}" for i in ma_range])


def test_add_moving_averages_sma(sample_data):
    ma = "SMA"
    on_col = "close"
    ma_range = (10, 20, 50)

    indicator = MovingAverages(sample_data, ma, on_col, ma_range)
    result = indicator.add_moving_averages()

    assert isinstance(result, pd.DataFrame)
    assert result.shape == sample_data.shape
    assert all(col in result.columns for col in [f"{ma}{i}" for i in ma_range])


def test_add_moving_averages_dma(sample_data):
    ma = "DMA"
    on_col = "close"
    ma_range = (10, 20, 50)

    indicator = MovingAverages(sample_data, ma, on_col, ma_range)
    result = indicator.add_moving_averages()

    assert isinstance(result, pd.DataFrame)
    assert result.shape == sample_data.shape
    assert all(col in result.columns for col in [f"{ma}{i}" for i in ma_range])


def test_add_moving_averages_invalid(sample_data):
    ma = "Invalid"
    on_col = "close"
    ma_range = (10, 20, 50)

    indicator = MovingAverages(sample_data, ma, on_col, ma_range)

    with pytest.raises(KeyError) as exc_info:
        indicator.add_moving_averages()


def test_moving_average_crossover(sample_data):
    ma1 = "EMA10"
    ma2 = "EMA20"
    sample_data[ma1] = 15
    sample_data[ma2] = 10

    result = MovingAverages.moving_average_crossover(sample_data, ma1, ma2)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert not result[0]
    assert result[1] == "No Crossover"
