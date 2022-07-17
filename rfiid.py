from evdev import InputDevice
from gpiozero import LED
from select import select
import threading
import csv
import time
import socket

ledIN = LED(6)


host = '192.168.137.228'
port = 54321


def server():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind((host,port))
	s.listen(5)

	while True:
		conn,address = s.accept()
		
		print(f"connection from {address} has been started")
		message = input ("enter the message: ")
		data = checkRFidTagOUT(message)
		data = checkRFidTagIN(message)
		
		if data is not None:conn.send(bytes(data[0],"utf-8"))
		

def deleteIN(name):
    lines = list()

    with open('DatabaseIn.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == name:
                    lines.remove(row)

    with open('DatabaseIn.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

def deleteOUT(name):
    lines = list()

    with open('DatabaseOut.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == name:
                    lines.remove(row)

    with open('DatabaseOut.csv', 'w') as writeFile:
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
        with open("DatabaseIn.csv") as csvfile:
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
                    ledOUT.off()
            
                    for word in rows:
                        sent += str(word) + ","
                    datas.append(sent)
                    
            
                    			
                    print(f"Welcome: {name}")
                    
                    with open("DatabaseOut.csv", 'a') as csvfile: 
                        csvwriter = csv.writer(csvfile) 
                        csvwriter.writerow(rows)
                        csvfile.close()

        if RFidRegistered == False:
            print("Access denied!")
    return datas

def checkRFidTagOUT(tagId):
    fields = ['id']
    rows = []
    datas = []
    sent = ""
    if tagId != "":
        RFidRegistered = False
        print(tagId)
        with open("DatabaseOut.csv") as csvfile:
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
		            ledIN.off()
                    ledOUT.on()

                    
                    for word in rows:
                        sent += str(word) + ","
                    datas.append(sent)
                    print(f"Bye: {name[:-1]}")
               
                    
                    with open("DatabaseIn.csv", 'a') as csvfile: 
                        csvwriter = csv.writer(csvfile) 
                        csvwriter.writerow(rows)
                        csvfile.close()
                        deleteOUT(name)
                    

        if RFidRegistered == False:
            print("RFID Not known!")        

    return datas

def reader_out():
        
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event8')
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
    return dats

def reader_in():
        
    keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
    dev = InputDevice('/dev/input/event7')
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


    return dats

if __name__ in "__main__": 
	readerTwo = threading.Thread(target=reader_in)
	out_read = threading.Thread(target=reader_out)
	readerONe = threading.Thread(target=server)
	readerONe.start()
	readerTwo.start()
	out_read.start()
	out_read.join()
	readerONe.join()
	readerTwo.join()






