from random import uniform

import pandas as pd
import pytest

from trade.technicals.indicators.rsi import RSI


@pytest.fixture(scope="function")
def random_nos():
    return [round(uniform(85, 99), 2) for i in range(100)]


def test_rsi_init(random_nos):
    data = pd.DataFrame({"close": random_nos})
    rsi = RSI(data)
    assert rsi.data.equals(data)
    assert rsi.period == 14


def test_rsi_calculate_rsi(random_nos):
    data = pd.DataFrame({"close": random_nos})
    rsi = RSI(data).calculate_rsi()
    assert len(rsi.columns) == 2
    assert "RSI" in rsi.columns


def test_rsi_apply_indicator(random_nos):
    data = pd.DataFrame({"close": random_nos})
    result = RSI.apply_indicator(data)
    assert len(result.columns) == 2
    assert "RSI" in result.columns
