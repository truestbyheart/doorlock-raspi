
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
from random import randint
from evdev import InputDevice
from select import select

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
        

def listen_rfid():
        global pin
        global accessLogId
        
        keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        dev = InputDevice('/dev/input/event7')
        rfid_presented = ""

        while True:
           r,w,x = select([dev], [], [])
           for event in dev.read():
               print(f"{event.type} :::: {event.value} ::: {event.code} ::: {event}")
               if event.type ==1 and event.value==1:
                   if event.code == 28:
                       print(rfid_presented)
            #  if event.type==1 and event.value==1:
            #     if event.code==28:
            #       print(f"this is reader 2: {rfid_presented}")

if __name__ == '__main__':
    readerOne = threading.Thread(target=listen_rfid)
    readerOne.start()
