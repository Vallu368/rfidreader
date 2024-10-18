import serial
import serial.tools.list_ports
import MySQLdb
import maskpass
import hashlib
from datetime import datetime
import config

#simple program to access the sql database for the rfid so creating nicknames and such is easier
def login():
    user = config.manager
    password = config.managerPass
    return user, password
def getTime():
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M')
    return formatted_date
login_information = login()
try:
    #Establish sql connection
    dbConn = MySQLdb.connect(config.ip, user=login_information[0], passwd=login_information[1], db=config.database)
    print("Connected to database")
    cursor = dbConn.cursor() #Open cursor to database
    dbConn.autocommit(True) #Commits inserts automatically
    print("RFID Scanner Manager v0.1")
    action =f"{login_information[0]} logged into RFID Manager"
    formatted_date = getTime()
    cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
    while True: #Program loops until exited
        print("Input help for command list: ")
        com = input("") #User input for commands
        if com.lower() == "exit": #Close program
            print("Closing program")
            formatted_date = getTime()
            action = f"{login_information[0]} logged out of RFID Manager"
            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
            break
        elif com.lower() == "help": #Shows a description to everything you can do with this program
            print("showall - Show amount of tags and current  ID's with associated nicknames")
            print("add - Add a new nickname to an existing tag")
            print("remove - Remove an existing nickname")
            print("new - Add a new tag or card into the database (Requires RFID Scanner)")
            print("error - Show RFID Scanner error logs")
            print("action - Show RFID Manager action logs")
            print("reset - Log out everyone currently logged in on the database")
            print("exit - Close the program")
        
        elif com.lower() == "new": #Add a new tag/card into sql db
            device = ""
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "Arduino" in p[1]:
                    print(f"Arduino detected in {p[0]}")
                    device = p[0]
            try:
                print(f"Connecting to {device}...")
                arduino = serial.Serial(device, 9600) #Start connection to arduino
                print("Connected succesfully")
                print("Please scan the tag or card you wish to add to the database")
                while True:
                    data = arduino.readline().decode('utf-8')
                    uid_check = data[1:4]
                    if str(uid_check) == "UID":
                        uid = str(data[6:])
                        uid = uid.strip()
                        h = hashlib.sha256()
                        h.update(uid.encode('utf-8'))  # Convert UID to bytes and hash it
                        hashed_uid = h.hexdigest()
                        print(f"Hashed UID: {hashed_uid}")  # Print the hashed UID
                        cursor.execute("select id from tags where rfid_uid = %s", (hashed_uid,))
                        check_if_exists = cursor.fetchone()
                        #print(check_if_exists)ar
                        if check_if_exists is not None:
                            print(f"Tag already exists with ID number of {check_if_exists[0]}")
                            arduino.close()
                            break
                        else:
                            cursor.execute("select max(id) from tags") ## if 0 shit breaks fix tomoro, add a 0 card to sql already or smthhing
                            max = cursor.fetchone()[0]
                            if max == None:
                                max = -1
                            max = int(max) + 1
                            cursor.execute("INSERT INTO tags(id, rfid_uid) VALUES (%s,%s)", (max, h.hexdigest()))
                            print(f"Tag added to database ID: {max} UID: {h.hexdigest()}")
                            formatted_date = getTime()
                            action = f"{login_information[0]} added new tag {max}"
                            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
                            print("Add a nickname? yes/no")
                            addnick = input("")
                            if addnick.lower() == "yes":
                                print(f"Input nickname for {max}")
                                nick_fromnewtag = input("")
                                cursor.execute("INSERT INTO nicknames(tag_id, nick) VALUES (%s,%s)", (max, nick_fromnewtag))
                                print(f"{max}'s nickname now is {nick_fromnewtag}")
                                action =f"{login_information[0]} changed tag {max} nickname to {nick_fromnewtag}"
                                formatted_date = getTime()
                                cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
                                arduino.close()
                                break
                            else:
                                break

            except Exception as e: 
                print(f"Failed connection to {device}: ", e) 
                continue
        elif com.lower() == "reset": #Log everyone out in case theres issues with rfid scanner
            print("This is for logging out everyone who is currently in, in case there is an error")
            print("continue? yes/no")
            cont = input("")
            if cont.lower() == "yes":
                cursor.execute("SELECT uid FROM access_log t1 WHERE in_out = 1 AND (SELECT MAX(t2.id) FROM access_log t2 WHERE t2.uid = t1.uid) = t1.id;")
                result = cursor.fetchall()
                am = 0
                for i in result:
                    am += 1
                    i = i[0]
                    print(f"Logging out {i}...")
                    formatted_date = getTime()
                    cursor.execute("INSERT INTO access_log (date,uid,in_out) VALUES (%s,%s,%s)", (formatted_date,i,0))
                print(f"Reset complete, logged out {am} IDs")
                formatted_date = getTime()
                action = f"{login_information[0]} logged out {am} IDs"
                cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
        elif com.lower() == "action": #Show action logs
            print("Showing database action_log table")   
            print("How many rows? Leave blank for all")
            many = input("")
            if many == "":
                cursor.execute("SELECT * from action_log ORDER BY id ASC")
                errors = cursor.fetchall()
                for i in errors:
                    print(i)
            elif many.isdigit is False:
                print("Invalid user input")
                continue
            else:
                many = int(many)
                cursor.execute("SELECT * from action_log ORDER BY id DESC limit %s", (many,))
                errors = cursor.fetchall()
                for i in errors:
                    print(i)
            formatted_date = getTime()
            action = f"{login_information[0]} opened action log"
            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
        elif com.lower() == "error": #Show error logs
            print("Showing database Error_Log table")   
            print("How many rows? Leave blank for all")
            many = input("")
            if many == "":
                cursor.execute("SELECT * from error_log ORDER BY id ASC")
                errors = cursor.fetchall()
                for i in errors:
                    print(i)
            elif many.isdigit is False:
                print("Invalid user input")
                continue
            else:
                many = int(many)
                cursor.execute("SELECT * from error_log ORDER BY id DESC limit %s", (many,))
                errors = cursor.fetchall()
                for i in errors:
                    print(i)
            formatted_date = getTime()
            action = f"{login_information[0]} opened error log"
            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
        elif com.lower() == "showall": #Show amount of tags in database and which ones have a set nickname
            cursor.execute("SELECT MAX(id) from tags") #Get the amount of tags in database
            max = cursor.fetchone()[0]
            cursor.execute("SELECT * from nicknames ORDER BY tag_id DESC") #Get every nickname in database
            nicks = cursor.fetchall()
            print(f"Amount of tags: {max}")            #Show amount of tags to user
            print(f"ID and associated nickname:")
            for i in nicks:
                print(i)
            formatted_date = getTime()
            action = f"{login_information[0]} opened active tags(showall)"
            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))

        elif com.lower() == "add":  #Code to add a new nickname
            newid = input("Input id of tag: ") #User inputs ID of the tag to get a new nickname
            if newid.isdigit() == False:  #Check if user input is a number
                print("invalid input, please input a number") #Return if the user input is weird
                continue
            else:
                newid = int(newid) #Turn user input string into an integer
                cursor.execute("SELECT rfid_uid from tags where id = %s", (newid,)) #Execute SQL command to get the UID of the tag that has the user inputted ID number
                idresult = cursor.fetchone() 
                if idresult is None:    #Check if the number exists, ie if the user inputs number 16 and there's only 15 tags it will not go through
                    print("ID does not exist")
                else:
                    cursor.execute("SELECT nick from nicknames where tag_id = %s", (newid,)) #Checking if tag already has a nickname
                    nickresult = cursor.fetchone()
                    if nickresult is None: #If there isn't one already, the user gets to create a new one
                        newnick = input("Nickname: ")
                        cursor.execute("INSERT INTO nicknames(tag_id, nick) VALUES (%s,%s)", (newid, newnick))
                        print(f"{newid}'s nickname now is {newnick}")
                        formatted_date = getTime()
                        action = f"{login_information[0]} changed tag {newid} nickname to {newnick}"
                        cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
                    else:
                        print(f"Tag with the ID of {newid} already has a nickname: {nickresult[0]}. If you wish to assign it a new one, delete the old one first")
                        # run removenick to remove an existing nick if the user wants to replace it
        elif com.lower() == "remove": #Code to remove existing nickname
            newid = input("Input id of tag: ") #Get ID number
            if newid.isdigit() == False:
                print("invalid input, please input a number") #If input is not a digit
                continue
            else:
                newid = int(newid)
                cursor.execute("SELECT rfid_uid from tags where id = %s", (newid,)) #Checking if ID exists
                idresult = cursor.fetchone()
                if idresult is None:
                    print("ID does not exist")
                else:
                    cursor.execute("SELECT nick from nicknames where tag_id = %s", (newid,))
                    nickresult = cursor.fetchone() #Checking if tag already has a nick
                    if nickresult is None:
                        print(f"{newid} does not have a nickname assigned to it") 
                    else: #Remove existing nickname, with a safety check too so if the user changes their mind they can cancel
                        print(f"Are you sure you want to delete nickname {nickresult[0]} from the tag {newid}?")
                        print("If you wish to delete the nickname, input YES")
                        yes = input("")
                        if yes == "YES":
                            cursor.execute("DELETE from nicknames where tag_id = %s; ", (newid,))
                            print("Deletion successful")
                            formatted_date = getTime()
                            action = f"{login_information[0]} removed tag {newid} nickname"
                            cursor.execute("INSERT INTO action_log(date, action) VALUES (%s,%s)", (formatted_date, action))
except Exception as e:
    print("Failed to connect to database: ", e)
    exit()
