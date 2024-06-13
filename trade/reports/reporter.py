from typing import Any
from os import getenv
from trade.reports.outputs import TelegramBot, GoogleSheetBot


TELEGRAM_SIGNATURE = "\n Generated on {0}."


class Reporter:

    def to_telegram(self,
                    data: Any,
                    telegram_signature: str = TELEGRAM_SIGNATURE,
                    chat_id: str = getenv("TELEGRAM_CHATID", None),
                    telegram_token: str = getenv("GSHEET_KEY", None)) -> None:
        TelegramBot.communicate_data(data, chat_id, telegram_token, True,
                                     telegram_signature)

    def to_gsheet_for_index(self, index_report:dict, analysis_date,
                  sheet_key:str = "index",
                  credentials:str = getenv("GSHEET_CRED", None),
                  cred_key:str = getenv("GSHEET_KEY", None)) -> None:

        GoogleSheetBot.communicate_data(index_report, analysis_date, sheet_key,
                                        credentials, cred_key)
