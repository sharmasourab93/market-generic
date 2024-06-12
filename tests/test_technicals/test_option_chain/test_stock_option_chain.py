import pytest
from datetime import datetime
from trade.nse.nse_configs.nse_config import NSEConfig
from trade.technicals.option_chain import OptionChain
from trade.technicals.option_chain.stock_option_chain import StockOptionChainAnalysis


@pytest.fixture
def dated():
    return datetime.today().date().strftime("%d-%b-%Y")


@pytest.fixture
def as_month():
    return datetime.today().date().strftime("%b-%y")


@pytest.fixture
def config(dated):
    return NSEConfig(dated)


@pytest.fixture
def fno_list(config):
    return config.get_fno_stocks()


@pytest.fixture(scope="function")
def stock_option_chain(dated, config, as_month):
    option_chain = []
    items = ("RELIANCE", "HDFCBANK", "SBIN", "TATACHEM")
    for value in items:
        oc_data = config.get_option_chain_data(value)
        strike_multiples = config.get_strike_mul_by_symbol(value)[value]
        lot_size = config.get_ticker_folots(value, as_month)
        oc_obj = OptionChain.analyze_option_chain(value, dated, oc_data,
                                                  lot_size, strike_multiples)
        option_chain.append(oc_obj)

    return option_chain


def test_option_chain_object(stock_option_chain, dated, fno_list):

    for oc_obj in stock_option_chain:
        assert isinstance(oc_obj, StockOptionChainAnalysis)
        assert oc_obj.symbol in fno_list
        assert oc_obj.dated == dated


def test_pcr_verdict(stock_option_chain):
    for oc_obj in stock_option_chain:
        assert oc_obj.pcr_verdict(0.3) == "Over Sold"
        assert oc_obj.pcr_verdict(0.5) == "Very Bearish"
        assert oc_obj.pcr_verdict(0.7) == "Bearish"
        assert oc_obj.pcr_verdict(0.9) == "Mildly Bullish"
        assert oc_obj.pcr_verdict(1.1) == "Bullish"
        assert oc_obj.pcr_verdict(1.4) == "Very Bullish"
        assert oc_obj.pcr_verdict(1.6) == "Over Bought"
        assert oc_obj.pcr_verdict(-0.1) == "Invalid"


def test_overall_pcr(stock_option_chain):
    for oc_obj in stock_option_chain:
        assert isinstance(oc_obj.overall_pcr, float)


def test_strikes(stock_option_chain):
    for oc_obj in stock_option_chain:
        assert isinstance(oc_obj.strike_price, int) or isinstance(oc_obj.strike_price, float)
        assert isinstance(oc_obj.strike_min, int) or isinstance(oc_obj.strike_min,
                                                              float)
        assert isinstance(oc_obj.strike_max, int) or isinstance(oc_obj.strike_max,
                                                              float)
        assert isinstance(oc_obj.strike_range, range)


def test_option_chain_output(stock_option_chain):
    for oc_obj in stock_option_chain:
        result = oc_obj.option_chain_output()
        assert isinstance(result, dict)
        assert "near_strike_info" in result.keys()
        assert "Verdict" in result.keys()
        assert "Straddle" in result.keys()
        assert "Nearest Support" in result.keys()
        assert "Resistance at" in result.keys()
