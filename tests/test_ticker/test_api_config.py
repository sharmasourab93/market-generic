from pathlib import Path

import pytest

from trade.ticker.api_config import APIConfig


@pytest.fixture(scope="function")
def nse_config():
    class NSEConfig(APIConfig):
        pass

    return NSEConfig


def test_api_config(nse_config):

    config = Path("configs/nse.json")
    if config.exists():
        nse_conf = nse_config(config)
    else:
        config = Path(__file__).parent.parent.parent.resolve() / config
        nse_conf = nse_config(config)

    columns = ("industry", "market", "nse", "api", "block_deal", "fii_dii_report")
    assert all([hasattr(nse_conf, i) for i in columns])
