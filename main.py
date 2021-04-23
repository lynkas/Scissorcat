from telegram.utils.request import Request
from telegram import Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)
import os
from handler import FHandler
from threading import Thread

def main():
    url = None
    token = os.environ["token"]
    proxy = None
    if "dev" in os.environ:
        import logging

        if "proxy" in os.environ:
            proxy = os.environ["proxy"]
            proxy = Request(proxy_url=proxy)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        bot = Bot(token=token, request=proxy)
        updater = Updater(token)
    else:
        url = os.environ["url"]
        bot = Bot(token=token, request=proxy)
        updater = Updater(bot=bot)

    dispatcher = updater.dispatcher
    fileHandler = FHandler()

    dispatcher.add_handler(MessageHandler(Filters.photo, fileHandler.photoHandler()))
    dispatcher.add_handler(
        MessageHandler(Filters.document, fileHandler.documentHandler())
    )
    if "dev" in os.environ:
        updater.start_polling()

    else:
        port = os.environ["port"]
        # fuck it
        updater.start_webhook(port=int(port),url_path=token,webhook_url=f"{url}/{token}",)
    Thread(target=fileHandler.work).start()
    updater.idle()


if __name__ == "__main__":
    main()
