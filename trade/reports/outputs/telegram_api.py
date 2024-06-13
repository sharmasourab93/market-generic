import asyncio
from datetime import datetime
from functools import cache
from os import getenv
from typing import Any, Dict, Union

import telegram
from pandas import DataFrame

from trade.reports.outputs.output_generics import OutputGenerics


def textualize_data(telegram_method):
    def execute_method(
        self,
        data: Union[DataFrame, str],
        *,
        additional_text: str = None,
        order: str = "Top",
        cols: list = None,
        index: bool = False,
        tablefmt: str = "rst",
        stralign: str = "center",
        date_format: str = "%d-%b-%Y %H:%M",
    ):
        if isinstance(data, DataFrame):
            if cols is None:
                cols = data.columns.tolist()

            data = tabulate(
                data[cols],
                headers="keys",
                showindex=index,
                tablefmt=tablefmt,
                stralign=stralign,
            )

            if additional_text is not None:
                additional_text = "**" + additional_text + "**"

                if order.capitalize() == "Top":
                    data = additional_text + "\n" + data

                else:
                    data += "\n" + additional_text

        telegram_method(self, data, date_format)

    return execute_method


class TelegramBot(OutputGenerics):
    """
    TelegramBot method is built on the Singleton Pattern
    wherein at any given point we do not replicate creation of
    TelegramBot objects. This helps in using the same object
    over and over again in an optimized manner.
    """

    @classmethod
    def communicate_data(
        cls,
        data: Union[Dict[Any, Any], str],
        chat_id: str,
        telegram_token: str,
        telegram_bot_enabled: bool,
        telegram_signature: str,
        *,
        additional_text: str = None,
        order: str = "Top",
        cols: list = None,
        index: bool = False,
        tablefmt: str = "rst",
        stralign: str = "center",
        date_format: str = "%d-%b-%Y %H:%M",
    ) -> None:

        obj = cls(telegram_bot_enabled, chat_id, telegram_token, telegram_signature)
        obj.send_message(
            data,
            additional_text=additional_text,
            order=order,
            cols=cols,
            index=index,
            tablefmt=tablefmt,
            stralign=stralign,
            date_format=date_format,
        )

    def __init__(
        self,
        telegram_bot_enabled: bool,
        chat_id: str,
        telegram_token: str,
        telegram_sign: str,
    ):
        self.telegram_enabled = telegram_bot_enabled
        self.chat_id = chat_id
        self.telegram_sign = telegram_sign

        if self.telegram_enabled:
            if self.telegram_token is None:
                logger_msg = "TELEGRAM_TOKEN Key not set."
                raise KeyError(logger_msg)

            self.bot = telegram.Bot(self.telegram_token)

    @cache
    async def get_chat_id(self) -> int:
        """
        Method to get the chat_id of the group to which
        both has to send message to.
        This method is cached in order to reuse the exisiting chat box
        since we are only dealing with posting messages to
        one Telegram group.
        """

        if self.chat_id is None:
            bot_updates = await self.bot.get_updates()
            chat_id = bot_updates[1].effective_chat
            return chat_id.id

        return self.chat_id

    @textualize_data
    def send_message(self, text: str, date_format: str = "%d-%b-%Y %H:%M"):
        """
        If the Telegram_enabled bool is True, we send a message
        else do nothing.

        :param text:
        :param date_format:

        :return:
        """

        if self.telegram_enabled:
            chat_id = asyncio.run(self.get_chat_id())
            if self.telegram_sign is not None:
                text += self.telegram_sign.format(datetime.now().strftime(date_format))
            else:
                text += "\n{0}".format()
            asyncio.run(self.bot.send_message(text=text, chat_id=chat_id))
