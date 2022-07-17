
from csv import reader
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


def process_rf_card(rf_id, state):
     # CHECK IF THE USER EXISTS
     user = db.check_if_user_exists(rf_id=rf_id)
     if user:
         # GET LAST LOG ENTRY
         last_entry = db.get_last_log_entry(rf_id=rf_id)
         if last_entry:
             for row in last_entry:
                 print(row)
                 if state == row['current_state']:
                     print("REFUSE")
                 else:
                     db.add_log_entry(rf_id=rf_id, state=state)
                     print("ALLOW")  
         else:
            # CREATE ENTRY
            db.add_log_entry(rf_id=rf_id, state=state)  
            print("ALLOW")  
     else:
         print(f"user with card {rf_id} does not exist")    
         

def reader_in():  
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event7')
    rfid_presented = ""

    while True:
        r,w,x = select([dev], [], [])
        for event in dev.read():
            if event.type==1 and event.value==1:
                if event.code==28:
                    print(f"Verifying state: {rfid_presented}")
                    print(f"gate being used: IN")
                    process_rf_card(rf_id=rfid_presented, state="IN")    
                    rfid_presented = ""
                else:
                    rfid_presented += keys[ event.code ]


def reader_out():  
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev1 = InputDevice('/dev/input/event8')
    rfid_presented = ""

    while True:
        r,w,x = select([dev1], [], [])
        for event in dev1.read():
            if event.type==1 and event.value==1:
                if event.code==28:
                    print(f"Verifying state: {rfid_presented}")
                    print(f"gate being used: OUT")
                    process_rf_card(rf_id=rfid_presented, state="OUT")    
                    rfid_presented = ""
                else:
                    rfid_presented += keys[ event.code ]                    
    
                 
if __name__ == '__main__':
    db = Database('sql8507066', '8Dh6qETGM5', 3306, 'sql8.freemysqlhosting.net', 'sql8507066')
    db.get_connection()
    readerOne = threading.Thread(target=reader_in)
    readerTwo = threading.Thread(target=reader_out)
    readerOne.start()
    readerTwo.start()
    readerOne.join()
    readerTwo.join()
