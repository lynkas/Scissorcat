from telegram.utils.request import Request
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from handler import FileHandler, MessageHandler
from threading import Thread


def main():
    proxy = None

    token = os.environ["token"]

    if "dev" in os.environ:
        import logging
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        proxy = Request(proxy_url='http://127.0.0.1:2081')

    bot = Bot(token=token, request=proxy)

    fileHandler = FileHandler()
    messageHandler = MessageHandler(bot,fileHandler)

    works = []

    works.append(Thread(target=fileHandler.work))
    works.append(Thread(target=messageHandler.work))

    for i in works:
        i.start()
    for i in works:
        i.join()


if __name__ == '__main__':
    main()
