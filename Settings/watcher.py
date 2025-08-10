import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from glob import glob

print ("Crop sub area VideoSubFinder")


# RGBImages

class EventHandler(FileSystemEventHandler):

    @staticmethod
    def on_created(event):
        action, path = (event.event_type, event.src_path)
        if not "." in path.split(os.sep)[-1]:
            return
        path = ".".join(path.split("."))
        extension = path.split(".")[-1]
        RGBImages = os.path.basename(path)

        files = os.path.splitext(RGBImages)

        print(f" Crop images RGBImages : {RGBImages} Done")



if __name__ == "__main__":
    
    png = glob('../*/RGBImages')
for bit in png:
    path = os.path.join(bit)
    if not os.path.isdir(bit):
        raise FileNotFoundError
    observer = Observer()
    observer.schedule(EventHandler(), path, recursive=True)
    observer.start()


# TXTImages


class EventHandler(FileSystemEventHandler):

    @staticmethod
    def on_created(event):
        action, path1 = (event.event_type, event.src_path)
        if not "." in path1.split(os.sep)[-1]:
            return
        path1 = ".".join(path1.split("."))
        extension = path.split(".")[-1]
        TXTImages = os.path.basename(path1)

        files = os.path.splitext(TXTImages)

        print(f" Cleared Text Images TXTImages : {TXTImages} Done")



if __name__ == "__main__":
    
    png1 = glob('../*/TXTImages')
for bit1 in png1:
    path1 = os.path.join(bit1)
    if not os.path.isdir(bit1):
        raise FileNotFoundError
    observer = Observer()
    observer.schedule(EventHandler(), path1, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
