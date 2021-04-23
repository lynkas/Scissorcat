from queue import Queue, Empty
import logging
from scissor import Job

class FHandler:
    def __init__(self):
        self._queue = Queue()
        self.working = False

    def photoHandler(self):
        def func(update, context):
            attachments = update.message.effective_attachment
            i = attachments[-1]
            file = i.get_file(timeout=10)
            self.push(Job(file, update))

        return func

    def documentHandler(self):
        def func(update, context):
            attachments = update.message.effective_attachment
            if not attachments.mime_type.startswith("image/"):
                update.message.reply_text(
                    f"the file {attachments.file_name} is not an image ({attachments.mime_type})"
                )
                return
            else:
                try:
                    file = attachments.get_file(timeout=10)
                    self.push(Job(file, update))
                except:
                    logging.debug(f"document got error")

        return func

    def push(self, obj):
        self._queue.put(obj)

    def work(self):
        self.working = True
        while self.working:
            try:
                job = self._queue.get(timeout=1)
                job.process()
            except Empty:
                pass
