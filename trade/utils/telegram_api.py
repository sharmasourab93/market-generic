import asyncio
from datetime import datetime
from functools import cache
from os import getenv

import telegram

from trade.utils.meta_utils.singleton_meta import SingletonMeta

TELEGRAM_SIGNATURE = "\n Generated on {0}."


class TelegramBot(metaclass=SingletonMeta):
    """
    TelegramBot method is built on the Singleton Pattern
    wherein at any given point we do not replicate creation of
    TelegramBot objects. This helps in using the same object
    over and over again in an optimized manner.
    """

    def __init__(
        self,
        telegram_bot_enabled: bool = False,
        chat_id: str = getenv("CHAT_ID", None),
        telegram_sign: str = TELEGRAM_SIGNATURE,
    ):
        self.telegram_enabled = telegram_bot_enabled
        self.chat_id = chat_id
        self.telegram_sign = telegram_sign

        if self.telegram_enabled:
            self.telegram_token = getenv("TELEGRAM_TOKEN", None)

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
