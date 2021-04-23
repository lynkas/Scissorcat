from queue import Queue,Empty
from telegram import Document,PhotoSize
from threading import Thread
import logging
from scissor import Job


class FileHandler:
    def __init__(self):
        self._queue=Queue()
        self.working=False

    def push(self,obj):
        self._queue.put(obj)

    def work(self):
        self.working=True
        while self.working:
            try:
                job = self._queue.get(timeout=1)
                job.process()
            except Empty:
                pass


class MessageHandler:
    def __init__(self,bot,fileHandler):
        self.bot = bot
        self.offset = 0
        self.fileHandler = fileHandler

    def work(self):
        while True:
            updates = self.bot.getUpdates(timeout=10, offset=self.offset + 1)
            if updates:
                logging.debug(f"updates {len(updates)}")
                for update in updates:
                    logging.debug(update.message.__dict__)
                    self.offset = max(update.update_id, self.offset)
                Thread(target=self.update_processor,args=(updates,)).start()

    def update_processor(self,updates):
        for update in updates:
            attachments = update.message.effective_attachment
            files = []
            if attachments:
                logging.debug(f"have att")

                if isinstance(attachments,Document):
                    logging.debug(f"is document")
                    if not attachments.mime_type.startswith("image/"):
                        update.message.reply_text(f"the file {attachments.file_name} is not an image ({attachments.mime_type})")
                    else:
                        try:
                            files.append(attachments.get_file(timeout=10))
                            logging.warning(f"document got ")

                        except:
                            logging.debug(f"document got error")
                            pass
                if isinstance(attachments,list):
                    logging.debug(f"is list, {len(attachments)}")
                    if len(attachments)!=0:
                        i=attachments[-1]
                        if isinstance(i, PhotoSize):
                            logging.debug(f"is photo")
                            files.append(i.get_file(timeout=10))
                            logging.debug(f"photo got ")
            logging.debug(f"total {len(files)} file")
            for file in files:
                self.fileHandler.push(Job(file,update))