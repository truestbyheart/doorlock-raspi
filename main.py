
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
from random import randint
from evdev import InputDevice
from select import select
from dbops import Database

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)

class DeviceReader:
    db = None
    
    def __init__(self):
        db = Database('sql8507066', '8Dh6qETGM5', 3306, 'sql8.freemysqlhosting.net', 'sql8507066')
        db_instance = db.get_connection()
        self.db = db
    
    def listen_rfid(self):
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
                        data = self.db.query_runner(f"SELECT * FROM access_logs WHERE rf_id={rfid_presented} ORDER BY id  DESC LIMIT 1;")
                        print(data)
                       
 
                       
if __name__ == '__main__':
    device = DeviceReader()
    readerOne = threading.Thread(target=device.listen_rfid)
    readerOne.start()
