#!/usr/bin/python
import sys
sys.path = ['', '/usr/lib/python39.zip', '/usr/lib/python3.9', '/usr/lib/python3.9/lib-dynload', '/home/pi/.local/lib/python3.9/site-packages', '/usr/local/lib/python3.9/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.9/dist-packages']


from evdev import InputDevice
from gpiozero import LED
from select import select
import threading
import csv
import time
import socket

ledIN = LED(6)
ledIn = LED(5)

#  Added led output pin for gpio pin 7
ledinn = LED(7)

def startup():
    while True:
        ledIn.on()
        time.sleep(1)
        ledIn.off()
        time.sleep(1)



def deleteIN(name):
    lines = list()

    with open('/home/pi/Desktop/Run/DatabaseIn.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == name:
                    lines.remove(row)

    with open('/home/pi/Desktop/Run/DatabaseIn.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

def deleteOUT(name):
    lines = list()

    with open('/home/pi/Desktop/Run/DatabaseOut.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == name:
                    lines.remove(row)

    with open('/home/pi/Desktop/Run/DatabaseOut.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)




def checkRFidTagIN(tagId):
    fields = ['id']
    rows = []
    datas= []
    sent = ""
    if tagId != "":
        RFidRegistered = False
        print(tagId)
        with open("/home/pi/Desktop/Run/DatabaseIn.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["RFID"] == tagId[:10]:
                    RFidRegistered = True
                    st = row["RFID"]
                    name = row["name"]
                    stat = "in"
                    deleteIN(name)
                    rows.append(st)		
                    rows.append(name+".")
                    rows.append(stat)
                    ledIN.on()
                    time.sleep(2)
                    ledIN.off()

              
            
                    for word in rows:
                        sent += str(word) + ","
                    datas.append(sent)
                    
            
                    			
                    print(f"Welcome: {name}")
                    
                    with open("/home/pi/Desktop/Run/DatabaseOut.csv", 'a') as csvfile: 
                        csvwriter = csv.writer(csvfile) 
                        csvwriter.writerow(rows)
                        csvfile.close()

        if RFidRegistered == False:
            print("Access denied!")
 
def checkRFidTagOUT(tagId):
    fields = ['id']
    rows = []
    datas = []
    sent = ""
    if tagId != "":
        RFidRegistered = False
        print(tagId)
        with open("/home/pi/Desktop/Run/DatabaseOut.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["RFID"] == tagId[:10] and row["status"] == "in":
                    RFidRegistered = True
                    st = row["RFID"]
                    name = row["name"]
                    stat = "out"
                    rows.append(st)	
                    rows.append(name[:-1])
                    rows.append(stat)
                    # ledIN.on()
                    # time.sleep(2)
                    # ledIN.off()
                    
                    ledinn.on()
                    time.sleep(2)
                    ledinn.off()
		       
                    
                    for word in rows:
                        sent += str(word) + ","
                    datas.append(sent)
                    print(f"Bye: {name[:-1]}")
               
                    
                    with open("/home/pi/Desktop/Run/DatabaseIn.csv", 'a') as csvfile: 
                        csvwriter = csv.writer(csvfile) 
                        csvwriter.writerow(rows)
                        csvfile.close()
                        deleteOUT(name)
                    

        if RFidRegistered == False:
            print("RFID Not known!")        



def reader_out():
        
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event3')
    rfid_presented = ""
    while True:
        r,w,x = select([dev], [], [])
        for event in dev.read():
            if event.type==1 and event.value==1:
                if event.code==28:
                    print(f"this is reader 1: {rfid_presented}")
                    checkRFidTagOUT(rfid_presented)
                    rfid_presented = ""

        
                else:
                    rfid_presented += keys[ event.code ]


def reader_in():
        
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event0')
    rfid_presented = ""

    while True:
        r,w,x = select([dev], [], [])
        for event in dev.read():
            if event.type==1 and event.value==1:
                if event.code==28:
                    print(f"this is reader 2: {rfid_presented}")
                    checkRFidTagIN(rfid_presented)
                    rfid_presented = ""
            
                else:
                    rfid_presented += keys[ event.code ]




ledStarts = threading.Thread(target=startup)
readerTwo = threading.Thread(target=reader_in)
out_read = threading.Thread(target=reader_out)

readerTwo.start()
out_read.start()
ledStarts.start()

out_read.join()
ledStarts.join()
readerTwo.join()





