# market-generic - A Generic Python Package for Stock Market Analysis and Trading

### Overview

`market-generic` is a powerful and flexible Python library designed to simplify the process of working with stock market data. It provides a comprehensive set of tools and utilities to handle, analyze, and visualize stock data, enabling developers and analysts to build dynamic stock scanners, trading strategies, and other financial applications with ease.


### Key Features
- <b>Data Handling</b>: Seamless integration with popular data sources (e.g., Yahoo Finance, NSE APIs) to fetch and manage stock data.
- <b>Technical Indicators</b>: A wide range of technical indicators (e.g., Moving Averages, Pivot Points, RSI, MACD) for in-depth market analysis.
- <b>Generic Strategy Abstractions</b>: Tools to dynamically create trading strategies on the fly based on user-defined parameters.
- <b>Extensibility</b>: Modular design allows for easy integration with other Python libraries and frameworks.


### Installation
To install the AlgoTrade package, use pip:

```commandline
pip install market-generic
```

### Usage

Here's a simple example of how to use the Trade package to fetch and analyze stock data:
python

```python 
>>from trade.nse import NSEStock
>>stock = NSEStock("RELIANCE", "17-May-2024")
>>stock.symbol == "RELIANCE"
True 
>>stock.curr_ohlc 
# Will Display Reliance's latest Bhav 
{
"open": 2860.7,
"low": ...,
"high":...,
 "close": ...,
 "volume": ...
 "pct_change": ...
}
```

`AllNSEStocks` uses `NSEStock` module underneath to utilize stock functions.

```python
>>from trade.nse import AllNSEStocks
>>all_stocks = AllNSEStocks("17-May-2024", ["RELIANCE", "SBIN"])
>>all_stocks.symbols[0] == "RELIANCE"
True
>>all_stocks.symbols[1] == "SBIN"
True 
>>all_stocks.symbols[0].curr_ohlc
# Will Display Reliance's latest Bhav 
{
"open": 2860.7,
"low": ...,
"high":...,
 "close": ...,
 "volume": ...
 "pct_change": ...
}
```


### Documentation

For detailed documentation, examples, and API reference, please visit the 
[market-generic 
GitHub repository](https://github.com/sharmasourab93/market-generic).
