#!/usr/bin/env python3
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
import signal
from os import getenv
from random import randint
from evdev import InputDevice
from select import select
from dbops import Database

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT) 

continue_reading = True

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
                     GPIO.output(21,GPIO.HIGH)
                     time.sleep(10)
                     GPIO.output(21,GPIO.LOW)  
         else:
            # CREATE ENTRY
            db.add_log_entry(rf_id=rf_id, state=state)  
            print("ALLOW")
            GPIO.output(21,GPIO.HIGH)
            time.sleep(10)
            GPIO.output(21,GPIO.LOW)    
     else:
         print(f"user with card {rf_id} does not exist")    
         

def reader_in():  
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event7')
    rfid_presented = ""

    while continue_reading:
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

    while continue_reading:
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

 
 
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.output(20,GPIO.LOW)
 
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)   
                 
if __name__ == '__main__':
    db = Database(getenv('DATABASE_USERNAME'), getenv('DATABASE_PASSWORD'), getenv('DATABASE_PORT'), getenv('DATABASE_HOST'), getenv('DATABASE_DB_NAME'))
    db.get_connection()
    GPIO.output(20,GPIO.HIGH)
    readerOne = threading.Thread(target=reader_in)
    readerTwo = threading.Thread(target=reader_out)
    readerOne.start()
    readerTwo.start()
    readerOne.join()
    readerTwo.join()
