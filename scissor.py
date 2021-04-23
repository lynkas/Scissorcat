import io
from collections import namedtuple

from telegram import Document,File,Update,InputMediaPhoto
import PIL.Image as Image

chunk = 2048


class Job:
    def __init__(self, file:File, update_object:Update):
        self.files = []
        self.update=update_object
        if file.file_size>20*1024*1024:
            update_object.message.reply_text(f"the file is too large")
        else:
            self.file=file

    def process(self):
        ba = self.file.download_as_bytearray()
        image = Image.open(io.BytesIO(ba))
        result = crop(image)
        image.close()
        if len(result) == 0:
            message = self.update.message.reply_text("nothing to crop.")
        elif len(result)==1:
            imgIO = result[0]
            message = self.update.message.reply_photo(imgIO,reply_to_message_id=self.update.message.message_id,)
            imgIO.close()
        else:
            message = self.update.message.bot.sendMediaGroup(
                chat_id=self.update.message.chat_id,
                media=[InputMediaPhoto(i) for i in result],
                reply_to_message_id=self.update.message.message_id,
                allow_sending_without_reply=True,
                timeout=10
            )
        for i in result:
            i.close()
        return message



def crop(image:Image):
    seg = Crop(*image.size)
    ret = []
    for coo in seg:
        output = io.BytesIO()
        image.crop(coo).save(output, quality=80, format="png")
        output.seek(0)
        ret.append(output)
    return ret

class Crop:
    def __init__(self,width,height):

        self.size={"width":width,"height":height}
        self.crop_length = max(width, height)
        if width>=height:
            self.direction = "width"
            self.another_direction = "height"
        else:
            self.direction = "height"
            self.another_direction = "width"
        self.piece = self.crop_length // (chunk - 24)
        self.last = self.crop_length % (chunk - 24)
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        remaining = self.size[self.direction]-self.position
        if remaining <=0:
            raise StopIteration
        src = {"width":0,"height":0}
        to = {"width":0,"height":0}

        src[self.direction]=self.position
        src[self.another_direction]=0
        to[self.direction]=self.position+chunk
        to[self.another_direction]=self.size[self.another_direction]

        if remaining<chunk+100:
            to[self.direction] = self.size[self.direction]
            self.position = self.size[self.direction]
        else:
            self.position += chunk-24

        return src["width"],src["height"],to["width"],to["height"]