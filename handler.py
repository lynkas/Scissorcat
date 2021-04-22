from queue import Queue,Empty
from telegram import Document,PhotoSize
from threading import Thread

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
                Thread(target=self.update_processor,args=(updates,)).start()

    def update_processor(self,updates):
        for update in updates:
            self.offset = max(update.update_id, self.offset)
            attachments = update.message.effective_attachment
            files = []
            if attachments:
                if isinstance(attachments,Document):
                    try:
                        files.append(attachments.get_file(timeout=10))
                    except:
                        pass
                if isinstance(attachments,list):
                    for i in attachments:
                        if isinstance(i, PhotoSize):
                            files.append(i.get_file(timeout=10))
            for file in files:
                self.fileHandler.push(Job(file,update))