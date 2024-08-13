import serial
import MySQLdb
from datetime import datetime

def send_buzz_error(): #Red light twice & beeps from Arduino
    arduino.write(b"BUZZ_ERROR\n")

def send_buzz_green():
   arduino.write(b"BUZZ_GREEN\n")

def send_buzz_blue():
   arduino.write(b"BUZZ_BLUE\n")

def check_in_or_out(uid: str, in_or_out: int):
   going_in = 1
   going_out = 0
   #print(in_or_out)
   now = datetime.now()
   formatted_date = now.strftime('%Y-%m-%d %H:%M')
   try:
      #Establish sql connection
      dbConn = MySQLdb.connect("localhost","root","","rfid", unix_socket = "/opt/lampp/var/mysql/mysql.sock")
   except Exception as e:
      print("Failed to connect to database: ", e)
      send_buzz_error()
      exit()
   cursor = dbConn.cursor() #Open cursor to database
   dbConn.autocommit(True) #commits inserts automatically
   uid = uid.strip()
   cursor.execute("SELECT id FROM latka WHERE rfid_uid = %s", (uid,))
   result = cursor.fetchone()
        
   if result is None:
      print(f"UID {uid} not in database.")
      send_buzz_error()
      errorType = "UID not in Database"
      cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
      return
        
   tag_id = result[0]
   #print(f"TAG NUMBER IS {tag_id}")
   cursor.execute("SELECT nick FROM nicknames WHERE latka_id = %s", (tag_id,))
   nickresult = cursor.fetchone()

   if nickresult is None:
      print("No nickname in database")
      send_buzz_error()
      errorType = f"No assigned nickname in database"
      cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
      #nickresult = uid #make nickname the uid
      return

   print(f"Hello {nickresult[0]}")

   if in_or_out == 1: #GOING IN
      cursor.execute(f"SELECT in_out FROM `rfid_data` WHERE uid = '{uid}' order by id DESC limit 1;")
      check = cursor.fetchone()
      if check is not None:
         if str(check[0]) == "1":
            print("Already in")
            errorType = "Duplicate enter"
            cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
            send_buzz_error()
            return


      cursor.execute("INSERT INTO rfid_data (date, uid,in_out) VALUES (%s,%s,%s)", (formatted_date,uid,going_in))
      print(f"{nickresult[0]} has gone in at {formatted_date}")

   elif in_or_out == 0: #GOING OUT
    send_buzz_blue()
    cursor.execute(f"SELECT in_out FROM `rfid_data` WHERE uid = '{uid}' order by id DESC limit 1;")
    check = cursor.fetchone()
    if check is not None:
       if str(check[0]) == "0":
          print("Already out")
          errorType = "Duplicate exit"
          cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
          send_buzz_error()
          return
          
    #insert data into database
    cursor.execute("INSERT INTO rfid_data (date,uid,in_out) VALUES (%s,%s,%s)", (formatted_date,uid,going_out))
    print(f"{nickresult[0]} has gone out at {formatted_date}")
   else:
      print(f"Error checking in, no button pressed, current time: {formatted_date}")
      errorType = "No button pressed"
      cursor.execute("INSERT INTO error_log (date,tag_uid,error_type) VALUES (%s,%s,%s)", (formatted_date,uid,errorType))
      send_buzz_error()

   amount = cursor.execute("SELECT uid FROM rfid_data t1 WHERE in_out = 1 AND (SELECT MAX(t2.id) FROM rfid_data t2 WHERE t2.uid = t1.uid) = t1.id;")
   print(f"currently {amount} in class")
   cursor.close()
      

device = "/dev/ttyACM0" #port the arduino is plugged into
try:
  print(f"Connecting to...{device}")
  arduino = serial.Serial(device, 9600) #start connection to arduino
  print(f"Connected to {device}")
  while True: 
     data = arduino.readline().decode('utf-8') #decodes data to be more useful
     print(data)
     in_out_check = data[0:1] #check number to see if person is coming in or going out, or if its erroring
     uid_check = data[1:4]    #checks if the 3 letters of data are UID
     if str(uid_check) == "UID":
        uid = str(data[6:]) #length and position of the UID in data
         #check_in_or_out(uid, arduino) #run function to put data into the database
        check_in_or_out(uid, int(in_out_check))

        

except Exception as e: 
  print(f"Failed connection to {device}: ", e) 



