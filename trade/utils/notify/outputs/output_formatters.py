def format_market_data(data):
    message = ""

    # Index Data
    message += "**Index Data:**\n"
    for index in data["index"]:
        message += f"*{index['symbol']}*\n"
        for key, value in index.items():
            if key != "symbol":
                if isinstance(value, dict):
                    message += f"- {key.capitalize()}:\n"
                    for k, v in value.items():
                        message += f"  - {k.capitalize()}: {v}\n"
                elif isinstance(value, list):
                    message += f"- {key.capitalize()}: {', '.join(map(str, value))}\n"
                else:
                    message += f"- {key.capitalize()}: {value}\n"
        message += "\n"

    message += "**Advances, Declines, Unchanged:**\n"
    for key, value in data["adv_dec"].items():
        message += f"- {key}: {value}\n"
    message += "\n"

    message += "**FII/DII Data:**\n"
    for fii_dii in data["fii_dii"]:
        message += f"*{fii_dii['category']}*\n"
        for key, value in fii_dii.items():
            if key != "category":
                message += f"- {key.capitalize()}: {value}\n"
        message += "\n"

    message += "**Top 5 Stocks:**\n"
    for top_stock in data["top_bottom"]["top_n"]:
        message += f"- {top_stock['symbol']}: {top_stock['pct_change']}%\n"
    message += "\n**Bottom 5 Stocks:**\n"
    for bottom_stock in data["top_bottom"]["bottom_n"]:
        message += f"- {bottom_stock['symbol']}: {bottom_stock['pct_change']}%\n"

    return message
