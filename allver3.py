"""
TO DO:
Get camera image ./
and send data to website. check if done properly./
DO TIMEOUT OF NET CONNECION WNET WONET WnetTHENwo WOthenWNET

ANOTHER IMPORTANT: ask jols wat if long and lat is more than 3 digits


IMPORTANT: ask jols what the hppened
TO DO:
Have a checker when phone received a new message.
more likely global storage_id
Make sure command from phone sticks
Discuss commands with groupmates.
GPS / OFF IGNITION / ON IGNITION / WHATEVER
If there is change in command (HAVE CHECKER), update reports on website before applying!!!! IMPORTANT reorganize flow of prog
first is get status, then get sms then if change send data to website then grab info from web or directly use sms command
should be working with the online db dont use relay_func. use apply

***HAVE TIMEOUT IF THERE IS NO CONNECTION***
sample prog
import os
import time
import urllib2 

os.system("gpio mode 6 out && gpio mode 5 out")

while True:
    try:
        urllib2.urlopen("http://www.google.com").close()
    except urllib2.URLError:
        print "Not Connected"
        os.system("gpio write 6 0 && gpio write 5 1")
        time.sleep(1)
    else:
        print "Connected"
        os.system("gpio write 6 1 && gpio write 5 0")
        break

"""
import json, requests, picamera
import RPi.GPIO as GPIO
import serial, time, sys, datetime
GPIO.setmode(GPIO.BOARD)

#declaration of values
PLATE_NO = "TEJ123"
web_status="https://"
website="acarjsystem.herokuapp.com"
#website="192.168.1.5:8000"
#image
photo_folder='images/'
images_taken=1
#for GSM Module & relay
scflag = 0
scflag1 = 0
relay_pin = 7
#temporary
contact_no = "+639202192964"
time_out=5

#getting of vital user information
#CHANGE PLAN TO ONLY COMPARE INTERNET DB TO TEXT COMMAND
#Ver2 WEB already tested


#actual start of program
try:	
	#methods here
	def get_time():
		timenow = str(datetime.datetime.now().time())
		#datenow = str(datetime.date.today())
		print ("timenow = %s" % (timenow))
		#print ("datenow = %s" % (datenow))

	def take_photo():
		global photo_loc
		photo_loc = photo_folder+'first_take'+str(images_taken)+'.jpg'
		camera.capture(photo_loc)
		time.sleep(3)
		print ("photo taken")

	def gsm_setup():
		#GSM Setup
		serial_port = "/dev/ttyS0"
		global ser
		global res
		ser = serial.Serial(serial_port, baudrate = 115200, timeout = 5) 
		ser.write("AT+CGPSPWR=1"+"\r\n") #AT command for triggering on the GPS location finder
		res = ser.readlines()
		print res	
		ser.write('AT+CMGD=1,4'+'\r\n') #AT command for deleting all texts saved in the gsm storage
		res = ser.readlines() 
		print res
		ser.write("AT+CMGF=1"+"\r\n") #AT command for setting gsm to text mode
		res = ser.readlines()
		print res
		
	def gps_check(): #this is for initialization
		global loc
		global res
		global posit
		print ("in gps check")
		ser.write("AT+CGPSSTATUS?"+"\r\n") #AT command to know whether the gps has locked a fixed location, should output "Location 3D Fixed", if the result is "Location unknown" there is problem with gps, if the result is "Location not fixed" the gps is trying to fix a location wait for 5-10 mins or more
		res = ser.readlines()
		print res
		print res[1] #Outputs the first line which is "+ATCGPSSTATUS: Loc..."
		try:
			posit = res[1].index(":") #Indexing ":" on "+ATCGPSSTATUS: Loc..."
		except ValueError:
			loc = "Location Not Fix"
			print("message was received while trying to find location")
			mes = "Retry sending command."
			ser.write('AT+CMGS="'+contact_no+'"'+'\r\n') #AT command for sending sms from module to owner
			time.sleep(5) #This should delay 5 second before sending, this part is important should not be deleted
			ser.write(mes+chr(26)) #Content of variable mes and chr26 which is ctrl+z, this character is vital for sending sms because it ends whatever content you put before it and triggers for content to be sent
			res = ser.readlines() 
			print res
			mes=""
		else:
			loc = res[1][posit+2:posit+18] #Gets the string with parameter posit+2 and posit+17 in the statements "+ATCGPSSTATUS: Loc..." statement using ":" as guide
			print loc #Prints whether the Location is fixed or not 
			
			timenow = str(datetime.datetime.now().time())
			times = "%s%s%s" % (timenow[0:2],timenow[3:5],timenow[6:8])
			start = int(times)
			datenow = str(datetime.date.today())
			print ("timenow = %s" % (timenow))
			print ("datenow = %s" % (datenow))
			while loc != "Location 3D Fix" : #Variable loc should output "Location 3D Fix" to skip this part, if not this will continue on loop until variable loc is equal to "Location 3D Fix"
				time.sleep(5)
				ser.write("AT+CGPSSTATUS?"+"\r\n")
				res = ser.readlines()
				print res
				loc = res[1][posit+2:posit+18]
				print loc
				timenow = str(datetime.datetime.now().time())
				times = "%s%s%s" % (timenow[0:2],timenow[3:5],timenow[6:8])
				print (times)
				currentstart = int(times)
				if start<(currentstart-50):
					ser.write("AT+CGPSSTATUS?"+"\r\n")
					res = ser.readlines()
					print res
					loc = res[1][posit+2:posit+18]
					print loc
					print ("time limit")
					break


	def gps_func():
		#include the gps_check
		global mes
		gps_check()
		if loc == "Location Not Fix":
			mes = (loc+"ed.") #Content of the text from module to owner, there is str before latitude and longitude because variable latitude and longitude should be concatenated to from "Float" to "String" type 
			print(mes)
			if sms_gps == "True":
				ser.write('AT+CMGS="'+contact_no+'"'+'\r\n') #AT command for sending sms from module to owner
				time.sleep(5) #This should delay 5 second before sending, this part is important should not be deleted
				ser.write(mes+chr(26)) #Content of variable mes and chr26 which is ctrl+z, this character is vital for sending sms because it ends whatever content you put before it and triggers for content to be sent
				res = ser.readlines() 
				print res
		else:			
			 #For loop for gsm/gps module to keep looking for the coordinates and send it the owner the location of the car, (naglo-loop lang yan ng dalawang beses kasi ayaw ko ubusin load) 
			ser.write("AT+CGPSINF=32"+"\r\n") #AT command for getting the gps information on line 32 which is reserved for getting the latitude and longitude
			res = ser.readlines()
			print res
			print res[1] #Outputs the first line which starts with "+CGPSINF: ..."
			if(res[1].startswith("+CGPSINF:")):	
				posi = res[1].index("A") #Indexing "A" on the result of res[1], "A" if the gps module has finally locked a 3D fix, or "V" if it doesn't, this should output "A" only since we already set that program will continue to this part if on the setup it has already outputs "Location 3D Fix"
				lat = res[1][posi+2:posi+11] #Output is the latitude which is from position 2 and 11 after the the character "A", in gps coordinates this is in this format 0000.00000 *0000.0000 is sample only
				lon = res[1][posi+14:posi+24] #Output is the longitude which is from position 14 and 24 after the the character "A", in gps coordinates this is in this format 00000.00000 *00000.0000 is sample only
				lat1 = res[1][posi+2:posi+4] #Variable lat1 is the the first two "String" on the value output by variable lat, in gps coordinates this is the location of zero in this format 0032.12345 *32.12345 is sample only
				lat11 = int(lat1) #Convert "String" to "int"
				lat2 = res[1][posi+4:posi+11] #Variable lat2 is the "String" after variable lat1, in gps coordinates this is the location of zero in this format 1400.00000 *14 is sample only
				lat3 = float(lat2) #Convert "String" to "float"
				lat4 = lat3/60 
				latitude = lat11+lat4 #From variable lat1 to this part is the code for converting gps style to decimal degrees LATITUDE
				print latitude #Outputs latitude in decimal degrees style
				lon1 = res[1][posi+14:posi+17] #Variable lon1 is the the first three "String" on the value output by variable lon, in gps coordinates this is the location of zero in this format 00032.12345 *32.12345 is sample only
				lon11 = int(lon1) #Convert "String" to "int"
				lon2 = res[1][posi+17:posi+24] #Variable lon2 is the "String" after variable lon1, in gps coordinates this is the location of zero in this format 14000.00000 *14 is sample only
				lon3 = float(lon2) #Convert "String" to "float"
				lon4 = lon3/60
				longitude = lon11+lon4 #From variable lat1 to this part is the code for converting gps style to decimal degrees LONGITUDE
				print longitude #Outputs longitude in decimal degrees style
				#This should delay 5 second before sending, this part is important should not be deleted
				mes = ("Latitude: " + str(latitude) + '\n' +"Longitude: " + str(longitude)) #Content of the text from module to owner, there is str before latitude and longitude because variable latitude and longitude should be concatenated to from "Float" to "String" type 
				if sms_gps == "True":
					ser.write('AT+CMGS="'+contact_no+''+'\r\n') #AT command for sending sms from module to owner
					time.sleep(5) 
					ser.write(mes+chr(26)) #Content of variable mes and chr26 which is ctrl+z, this character is vital for sending sms because it ends whatever content you put before it and triggers for content to be sent
					res = ser.readlines() 
					print res
	
	def relay_setup():
		#GSM Pin setup
		GPIO.setup(relay_pin, GPIO.OUT)
		GPIO.output(relay_pin,GPIO.HIGH)

	def main_gsmgps(): #IMPORTANT: KEYWORDS ARE HERE
		print("IN maingpsgsm")
		global storage_id
		global sms_ignition
		global sms_gps
		global car_stat
		global loc_stat
		global ignition
		if loc_stat == "True":
			time.sleep(5)
			print("WAITING FOR MESSAGES")

		res = ser.readline()
		if(res.startswith("+CMTI:")): #AT command for incoming text, not necessarily be printed but it looks like this "+CMTI: "SM", 1" where "SM" is the status and 1 is the message ID
			print ("MESSAGE RECEIVED.")
			pos = res.index(",") #Indexing "," in "+CMTI: "SM", 1"
			storage_id = res[pos+1:] #Locate the message ID
			print storage_id #Prints message ID
			ser.write("AT+CMGR=") #AT command for reading the incoming text
			ser.write(storage_id) #AT command to trigger the module to read the text on the given message ID
			res = ser.readlines()
			print res
			print res[2] #Line 2 on the on the output of res, which is basically the content of the text sent to the module
			if(res[2].startswith("on")): #ON SYSTEM = CAROFF
					car_stat = "True"
					sms_ignition = "True"
					ignition = "True"
			elif(res[2].startswith("gpson")): #ON GPS
					car_stat = "True"
					sms_gps = "True" #If the owner sends "gps" it will proceed to function "gps_func"
					loc_stat = "True"
			elif(res[2].startswith("gpsoff")): #OFF GPS
					car_stat = "True"
					sms_gps = "False" #If the owner sends "gps" it will proceed to function "gps_func"
					loc_stat = "False"
			elif(res[2].startswith("off")): # OFF SYSTEM = CARON
					car_stat = "False"
					sms_ignition = "False"
					ignition = "False"

	def get_user_number(): #create method where if net stops in the middle of sending data it cancels
		print("in user number")	
		url = web_status + website + "/userdata/"
		print "getting contactno"
		global contact_no
		global username

		get_time()
		req_info = {
			'plate_no':PLATE_NO
		}
		#con error			requests.exceptions.ConnectionError
		
		try:
			response = requests.post(url=url, data=req_info, timeout=time_out)

		except requests.exceptions.ConnectionError:
			print ("NO INTERNET - get user num")
			get_time()
		except requests.exceptions.ReadTimeout:
			print ("Connection ERROR - timeout get user num")
			get_time()
		#except requests.exceptions.Timeout:
		#	print ("Connection Timeout- user phone number")
		else:
			print ("Connected - get user num")
			print (response.json())
			print (response.json()['cont_no'])
			contact_no=response.json()['cont_no']
			username=response.json()['username']
			if contact_no.startswith("0"):#chnge the 0 to +63
				cont_part = contact_no[0:1].replace("0","+63")
				contact_no = "%s%s" % (cont_part,contact_no[1:])

	def get_car_stat():
		#this method is for getting initial values
		#assigning of global variables
		print("in get car stat")
		global car_stat
		global car_id
		global user
		global ignition
		global taser
		global loc_stat
		global photo_stat
		global date_reported
		url = web_status + website + "/cardetail/"
		
		print "getting carstat"
		req_info = {
			'plate_no':PLATE_NO
		}
		try:
			get_time()
			response = requests.post(url=url, data=req_info, timeout=time_out)
		except requests.exceptions.ConnectionError:
			print ("CONNECTION ERROR - no net carstat")
			get_time()
		except requests.exceptions.ReadTimeout:
			print ("Connection ERROR - timeout get user num")
			get_time()
		else:
			print ("Connected - get car stat")
			print (response.json())
			if response.json()['Error'] == "True":
				print ("BAD REQUEST")
			else:
				#print (response.json()['car'])
				#print (response.json()['car_stat'])
				car_stat = response.json()['car_stat']
				if car_stat == "True":			
					car_id = response.json()['car_id']			
					user = response.json()['user']
					ignition = response.json()['ignition']
					taser = response.json()['taser']
					loc_stat = response.json()['loc_stat']
					photo_stat = response.json()['photo_stat']
					date_reported = response.json()['date_reported']
					#print(ignition)
					#print(car_id)
				else:
					print ("CAR IS NOT TURNED ON")

	def post_report_stat(): #Add if storage_id!= prev
		print("in post report stat")
		#for sending report stat when there is a difference in command from sms and db standard is time
		#checking whether carstat = true so report can add
		global sms_ignition
		global sms_gps
		global car_stat
		print (sms_ignition+"sms igni")
		print (sms_gps+"sms gps")
		if sms_ignition !="" or sms_gps != "":
			url = web_status + website + "/changecarstat/"			
			req_info = {
				'plate_no':PLATE_NO,
				'car_stat':car_stat
			}
			try:
				get_time()
				response = requests.post(url=url, data=req_info, timeout=time_out)
			except requests.exceptions.ConnectionError:
				print ("CONNECTION ERROR - no net post reportstat")
				get_time()
			except requests.exceptions.ReadTimeout:
				print ("Connection ERROR - tpost report statchangecarstat")
				get_time()
			else:		
				#print (response.json())
				print ("Connected sent - command difference")
				if response.json()['Error'] == "True":
					print ("BAD REQUEST")
				else:
					car_stat = response.json()['car_stat']
					if car_stat == "True":	
						url = web_status + website + "/addreport/"
						req_info = {
							'car_id' : car_id,
							'user' : user,
							"car_ignition": ignition, #change this when data is finalized
							"taser_stat": taser, #change this when data is finalized
							"car_loc_stat": loc_stat, #change this when data is finalized
							"car_photo_stat": photo_stat, #change this when data is finalized
							'report_stat':''	#change this when report is no longer filed
						}
						try:
							response = requests.post(url=url, data=req_info, timeout=time_out)
						except requests.exceptions.ConnectionError:
							print ("CONNECTION ERROR - no net postreport stat")
						#print (response.json())
						except requests.exceptions.ReadTimeout:
							print ("Connection ERROR - timeout post report stat")
							get_time()
						else:
							sms_ignition =""
							sms_gps = ""
					else:
						sms_ignition =""
						sms_gps = ""
						print ("CAR IS NOT TURNED ON")	

	def apply_command():
		print("in apply command")
		if car_stat == "True":
		#this will apply all the states received by the rpi ie send photo and location
		#get data for image and location here
			if ignition == "True":
				GPIO.output(relay_pin,GPIO.LOW)
				print "led OFF"
			else:
				GPIO.output(relay_pin,GPIO.HIGH)
				print "led on"

			if loc_stat == "True":
				#call gps
				print ("loc_stat true")
				time.sleep(2)
				gps_func()
				
			else:
				#call gps
				print ("loc_stat false")

			if photo_stat == "True":
				take_photo()
			else:
				print ("photostat=false")
				

		else:
			GPIO.output(relay_pin,GPIO.HIGH)
			time.sleep(0.5)
			print "led on"
		
	def post_rep_info():
		global mes
		print("in post rep info")
		
		url = web_status + website + "/addreport/"
		if loc_stat == "True" or photo_stat=="True":					
			req_info = {
				'car_id' : car_id,
				'user' : user,
				'car_loc':mes, 	#place coordinates here
				#'rep_photo':''	#place image here
			}
			file = {
				'rep_photo':open(photo_loc, 'rb')	#place image here
			}
			
			try:
				response = requests.post(url=url, data=req_info, files=file, timeout=time_out)
			except requests.exceptions.ConnectionError:
				print ("Not connected timeout or no error - post repinfo")
			except requests.exceptions.ReadTimeout:
				print ("Connection ERROR - timeout post rep info")
				get_time()
			else:
				print ("Connected sent - postrepinfo")
				mes=""
				print (response.json())
				images_taken = images_taken + 1 #find ++ equivalent in python
		else:
			print ("no command for photo or coord") #place coordiantes and photo here


	print("in try")
	#gsmmod_setup()#sets up gsm

	relay_setup()
	print("relay setup")
	
	gsm_setup()
	print("gsm setup")

	print("camera setup")
	camera = picamera.PiCamera()

	car_stat = "False"
	car_id = "False"
	user = "False"
	ignition = "False"
	taser = "False"
	loc_stat = "False"
	photo_stat = "False"
	date_reported = "False"
	sms_ignition =""
	sms_gps =""

	while True:
		#main_gsmgps()

		get_user_number()
		#check if there is an sms then store values given to a different variable
		get_car_stat()
		#compare it against the car_stat with whatever state
		main_gsmgps()
		main_gsmgps()
		#if sms is newer(check_sms_and_db) and is not equal to the DB's status update DB using (post_report_stat) dont send car loc and photo yet
		#only use the next method if there is a change when comparing data from sms and data from db okay? tnx
		apply_command()
		post_report_stat() #remove comment when change/can be found
		#get the final status of commands then apply to the hardware
		#gps_func() #testing of gpsremove if when okay
		#then after updating, (activate the status ordered by the user) use (post_rep_info) send car loc and photo here
		post_rep_info()
		print("loop done")
except KeyboardInterrupt:
	#GPIO.cleanup()
	print("end prog")

finally:
	GPIO.cleanup()
	print("end finlly")