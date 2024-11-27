import serial
import serial.tools.list_ports
import MySQLdb
import hashlib
from datetime import datetime
import time
import threading
import config

def send_buzz_error(arduino): #Red light twice & beeps from Arduino
    arduino.write(b"BUZZ_ERROR\n")

def send_buzz_green(arduino):
   arduino.write(b"BUZZ_GREEN\n")

def send_buzz_blue(arduino):
   arduino.write(b"BUZZ_BLUE\n")

def WaitForButton(uid, arduino):
   print("Button...")
   now = datetime.now()
   formatted_date = now.strftime('%Y-%m-%d %H:%M')
   try:
      #Establish sql connection
      dbConn = MySQLdb.connect(config.ip, config.manager,config.managerPass,config.database)
   except Exception as e:
      print("Failed to connect to database: ", e)
      send_buzz_error(arduino)
      send_buzz_error(arduino)
      send_buzz_error(arduino)
      return
   cursor = dbConn.cursor() #Open cursor to database
   dbConn.autocommit(True) #commits inserts automatically
   uid = uid.strip()
   cursor.execute("SELECT id FROM tags WHERE rfid_uid = %s", (uid,))
   result = cursor.fetchone()

   if result is None:
      print(f"UID {uid} not in database.")
      send_buzz_error(arduino)
      errorType = "UID not in Database"
      arduino.write(b"DATABASE\n")
      cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
      time.sleep(3)
      arduino.write(b"KORTTI\n")
      return 2
   else:
      tag_id = result[0]
      cursor.execute("SELECT nick FROM nicknames WHERE tag_id = %s", (tag_id,))
      nickresult = cursor.fetchone()

      if nickresult is None:
         print("No nickname in database")
         send_buzz_error(arduino)
         errorType = f"No assigned nickname in database"
         cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
         #nickresult = uid #make nickname the uid
         arduino.write(b"DATABASE\n")
         time.sleep(3)
         arduino.write(b"KORTTI\n")
         return 2

      arduino.write(b"NAPPI\n")
      print("Waiting for button")
      

      startTime = time.time()
      timeToRun = 5  # Timeout duration in seconds
      endTime = startTime + timeToRun

      while True:
         # Check if timeout has occurred
         if time.time() >= endTime:
               print("Timeout")
               send_buzz_error(arduino)
               arduino.write(b"KORTTI\n")
               return 2
         
         # Check if there is data waiting to be read
         if arduino.in_waiting > 0:
               data = arduino.readline().decode('utf-8').strip()
               print(data)
               if len(data) == 0:
                  continue  # Skip if data is empty

               in_out_check = data[0]
               if in_out_check == "0":
                  return 0
               elif in_out_check == "1":
                  return 1
         else:
               time.sleep(0.1)
         



def check_in_or_out(uid: str, in_or_out: int, arduino):
 
   going_in = 1
   going_out = 0
   now = datetime.now()
   formatted_date = now.strftime('%Y-%m-%d %H:%M')
   try:
      #Establish sql connection
      dbConn = MySQLdb.connect(config.ip, config.manager,config.managerPass,config.database)
   except Exception as e:
      print("Failed to connect to database: ", e)
      send_buzz_error(arduino)
      exit()
   cursor = dbConn.cursor() #Open cursor to database
   dbConn.autocommit(True) #commits inserts automatically
   uid = uid.strip()
   cursor.execute("SELECT id FROM tags WHERE rfid_uid = %s", (uid,))
   result = cursor.fetchone()
   if result is None:
      return
   
        
   tag_id = result[0]
   #print(f"TAG NUMBER IS {tag_id}")
   cursor.execute("SELECT nick FROM nicknames WHERE tag_id = %s", (tag_id,))
   nickresult = cursor.fetchone()

   if nickresult is None:
      return

   if in_or_out == 1: #GOING IN
      cursor.execute(f"SELECT in_out FROM `access_log` WHERE uid = '{uid}' order by id DESC limit 1;")
      check = cursor.fetchone()
      if check is not None:
         if str(check[0]) == "1":
            print("Already in")
            errorType = "Duplicate enter"
            cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
            send_buzz_error(arduino)
            arduino.write(b"DUPE\n")
            time.sleep(3)
            arduino.write(b"KORTTI\n")
            return


      cursor.execute("INSERT INTO access_log (date, uid,in_out) VALUES (%s,%s,%s)", (formatted_date,uid,going_in))
      print(f"{nickresult[0]} has gone in at {formatted_date}")
      send_buzz_green(arduino)
      arduino.write(b"WELCOME\n")
      time.sleep(3)
      arduino.write(b"KORTTI\n")

   elif in_or_out == 0: #GOING OUT
    send_buzz_blue(arduino)
    cursor.execute(f"SELECT in_out FROM `access_log` WHERE uid = '{uid}' order by id DESC limit 1;")
    check = cursor.fetchone()
    if check is not None:
       if str(check[0]) == "0":
          print("Already out")
          errorType = "Duplicate exit"
          cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
          send_buzz_error(arduino)
          arduino.write(b"DUPEX\n")
          time.sleep(3)
          arduino.write(b"KORTTI\n")
          return
    cursor.execute(f"SELECT date FROM `access_log` WHERE uid = '{uid}' order by id DESC limit 1;")
    result = cursor.fetchone()
    print(f"{nickresult[0]} entered at: {result[0]}")
    #insert data into database
    cursor.execute("INSERT INTO access_log (date,uid,in_out) VALUES (%s,%s,%s)", (formatted_date,uid,going_out))
    print(f"{nickresult[0]} has gone out at {formatted_date}")
    

    
   else:
      print(f"Error checking in, no button pressed, current time: {formatted_date}")
      errorType = "No button pressed"
      cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
      send_buzz_error(arduino)
      arduino.write(b"TIMEOUT\n")
      time.sleep(3)
      arduino.write(b"KORTTI\n")

   if in_or_out == 0:
      send_buzz_blue(arduino)
      arduino.write(b"GOODBYE\n")
      time.sleep(3)
      arduino.write(b"KORTTI\n")
      

   amount = cursor.execute("SELECT uid FROM access_log t1 WHERE in_out = 1 AND (SELECT MAX(t2.id) FROM access_log t2 WHERE t2.uid = t1.uid) = t1.id;")
   print(f"currently {amount} in class")
   cursor.close()
   
def Reset():
   hasResetToday = False
   while True:
      date = datetime.now()
      formatted_date = date.strftime('%Y-%m-%d %H:%M')
      now = datetime.now().hour
      if now >= 19 and hasResetToday == False:
         print("RESET")
         hasResetToday = True
         dbConn = MySQLdb.connect(config.ip, config.manager,config.managerPass,config.database)
         cursor = dbConn.cursor() #Open cursor to database
         cursor.execute("SELECT uid FROM access_log t1 WHERE in_out = 1 AND (SELECT MAX(t2.id) FROM access_log t2 WHERE t2.uid = t1.uid) = t1.id;")
         result = cursor.fetchall()
         am = 0
         for i in result:
            am += 1
            i = i[0]
            print(f"logging out {i}")
            check_in_or_out(i, 0)
         print(f"Reset complete, logged out {am} IDs")
      if now == 6 and hasResetToday == True:
         hasResetToday = False
         print("hasResetToday = False")


def Main():
   print("Starting main")
   device = ""
   ports = list(serial.tools.list_ports.comports())
   for p in ports:
      if "Arduino" in p[1]:
         print(f"Arduino detected in {p[0]}")
         device = p[0]
   try:
      print(f"Connecting to...{device}")
      arduino = serial.Serial(device, 9600) #start connection to arduino
      print(f"Connected to {device}")
      while True: 
         data = arduino.readline().decode('utf-8') #decodes data to be more useful
         print(data)
         arduino.write(b"KORTTI\n")
         in_out_check = data[0:1] #check number to see if person is coming in or going out, or if its erroring
         uid_check = data[1:4]    #checks if the 3 letters of data are UID
         if str(uid_check) == "UID":
            uid = str(data[6:]) #length and position of the UID in data
            uid = uid.strip()
            h = hashlib.new('sha256')
            print(uid)
            h.update(uid.encode('utf-8'))
            print(h.hexdigest())
               #check_in_or_out(uid, arduino) #run function to put data into the database
            #check_in_or_out(h.hexdigest(), int(in_out_check))+
            button = WaitForButton(h.hexdigest(), arduino)
            if button != 2:
               check_in_or_out(h.hexdigest(), button, arduino)
            button = 2        
   except Exception as e: 
      print(f"Failed connection to {device}: ", e) 
      
def StatusCheck():
   print("Status check starting...")
   while True:
      now = datetime.now()
      formatted_date = now.strftime('%Y-%m-%d %H:%M')
      dbConn = MySQLdb.connect(config.ip, config.manager,config.managerPass,config.database)
      cursor = dbConn.cursor() #Open cursor to database
      cursor.execute("UPDATE status SET time = %s WHERE id = %s;", (formatted_date, 0))
      dbConn.commit()
      print(formatted_date)

      time.sleep(60)
t1 = threading.Thread(target=Reset)
t2 = threading.Thread(target=StatusCheck)
t1.start()
t2.start()





