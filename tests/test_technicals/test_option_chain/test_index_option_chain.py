import pytest

from trade.nse.nse_configs.nse_indices_config import NSEIndexConfig
from trade.technicals.option_chain import IndexOptionChainAnalysis


@pytest.fixture
def index_option_chain_analysis():
    return IndexOptionChainAnalysis(
        symbol="NIFTY",
        oc_data={
            "records": {
                "data": [
                    {"strikePrice": 100, "CE_openInterest": 100, "PE_openInterest": 100}
                ]
            },
            "filtered": {"PE": {"totOI": 100}, "CE": {"totOI": 100}},
            "timestamp": "2022-01-01 00:00:00",
            "expiryDates": ["2022-01-15", "2022-02-15"],
            "strikePrices": [100, 110, 120],
            "underlyingValue": 100,
        },
        strike_multiples={"NIFTY": 10},
        Config=NSEIndexConfig,
    )


@pytest.mark.xfail(reason="Still not well integrated.")
def test_index_option_chain_analysis(index_option_chain_analysis):
    result = index_option_chain_analysis.index_option_chain_analysis(
        symbol="NIFTY", expiry_day=15, delta=5, expiry_delta=1
    )
    assert isinstance(result, dict)
    assert "symbol" in result
    assert "Expiry" in result
    assert "Max Put & Call OI" in result
    assert "Support at" in result
    assert "Resistance at" in result
    assert "Straddle" in result
    assert "Overall PCR" in result
    assert "Verdict" in result
