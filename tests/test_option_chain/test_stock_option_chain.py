# import pytest
#
# from trade.nse.nse_config import NSEConfig
# from trade.option_chain.stock_option_chain import StockOptionChain
#
#
# @pytest.fixture
# def stock_option_chain():
#     return StockOptionChain(
#         symbol="TATASTEEL",
#         oc_data={
#             "records": {
#                 "data": [
#                     {"strikePrice": 100, "CE_openInterest": 100, "PE_openInterest": 100}
#                 ]
#             },
#             "filtered": {"PE": {"totOI": 100}, "CE": {"totOI": 100}},
#             "timestamp": "2022-01-01 00:00:00",
#             "expiryDates": ["2022-01-15", "2022-02-15"],
#             "strikePrices": [100, 110, 120],
#             "underlyingValue": 100,
#         },
#         strike_multiples={"TATASTEEL": 10},
#         Config=NSEConfig,
#     )
#
#
# pytest.mark.xfail(reason="Not Integrated yet.")
# def test_get_select_stock_options_bhavcopy(stock_option_chain):
#     result = stock_option_chain.get_select_stock_options_bhavcopy(
#         symbol="TATASTEEL", expiry="2022-01-15"
#     )
#     assert isinstance(result, tuple)
#     assert len(result) == 2
#     assert isinstance(result[0], pd.DataFrame)
#     assert isinstance(result[1], pd.DataFrame)
#     assert result[0].shape[0] > 0
#     assert result[1].shape[0] > 0
#
#
# pytest.mark.xfail(reason="Not Integrated.")
#
#
# def test_stock_option_chain(stock_option_chain):
#     result = stock_option_chain.stock_option_chain(
#         symbol="TATASTEEL", delta=5, expiry_delta=1
#     )
#     assert isinstance(result, dict)
#     assert "OptionChain" in result
#     assert "Expiry" in result
#     assert "underlying_value" in result
