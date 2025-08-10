import Copyfile

import makefolder

import msvcrt
import time
import subprocess
import os


process1 = subprocess.Popen(["python", "main.py"])
def countdown(time_sec):
    while time_sec:
        mins, secs = divmod(time_sec, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        if msvcrt.kbhit():
            print("entered ",msvcrt.getch().decode('ASCII'),"so now i will quit")
            break       
        print( end='\r')
        time.sleep(1)
        time_sec -= 1

countdown(1)


process2 = subprocess.Popen(["python", "watcher.py"])







