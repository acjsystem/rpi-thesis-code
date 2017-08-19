import RPi.GPIO as GPIO
import serial, time, sys
import datetime
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

plate_number = "TEJ123"
scflag = 0
scflag1 = 0
relay_pin = 7

try:
	def gms_setup():
	  GPIO.setup(relay_pin, GPIO.OUT)
	  GPIO.output(relay_pin,GPIO.HIGH)
	  
	serial_port = "/dev/ttyS0"
	ser = serial.Serial(serial_port, baudrate = 115200, timeout = 5) 
	gsm_setup()
	ser.write("AT+CGPSPWR=1"+"\r\n") #AT command for triggering on the GPS location finder
	res = ser.readlines()
	print res	
	ser.write('AT+CMGD=1,4'+'\r\n') #AT command for deleting all texts saved in the gsm storage
	res = ser.readlines() 
	print res
	ser.write("AT+CMGF=1"+"\r\n") #AT command for setting gsm to text mode
	res = ser.readlines()
	print res
	ser.write("AT+CGPSSTATUS?"+"\r\n") #AT command to know whether the gps has locked a fixed location, should output "Location 3D Fixed", if the result is "Location unknown" there is problem with gps, if the result is "Location not fixed" the gps is trying to fix a location wait for 5-10 mins or more
	res = ser.readlines()
	print res
	print res[1] #Outputs the first line which is "+ATCGPSSTATUS: Loc..."
	posit = res[1].index(":") #Indexing ":" on "+ATCGPSSTATUS: Loc..."
	loc = res[1][posit+2:posit+17] #Gets the string with parameter posit+2 and posit+17 in the statements "+ATCGPSSTATUS: Loc..." statement using ":" as guide
	print loc #Prints whether the Location is fixed or not 
	while loc != "Location 3D Fix": #Variable loc should output "Location 3D Fix" to skip this part, if not this will continue on loop until variable loc is equal to "Location 3D Fix"
		ser.write("AT+CGPSSTATUS?"+"\r\n")
		res = ser.readlines()
		print res

	print("Setup OK")

	def relay_func(): #Function for relay
		GPIO.output(relay_pin,GPIO.LOW)
		time.sleep(0.5)
		print "relay off"
	
	def gps_func():
		for i in range(1,3): #For loop for gsm/gps module to keep looking for the coordinates and send it the owner the location of the car, (naglo-loop lang yan ng dalawang beses kasi ayaw ko ubusin load) 
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
				ser.write('AT+CMGS="+639067643874"'+'\r\n') #AT command for sending sms from module to owner
				time.sleep(5) #This should delay 5 second before sending, this part is important should not be deleted
				mes = ("Latitude: " + str(latitude) + '\n' +"Longitude: " + str(longitude)) #Content of the text from module to owner, there is str before latitude and longitude because variable latitude and longitude should be concatenated to from "Float" to "String" type 
				ser.write(mes+chr(26)) #Content of variable mes and chr26 which is ctrl+z, this character is vital for sending sms because it ends whatever content you put before it and triggers for content to be sent
				res = ser.readlines() 
				print res

	while True:
		res = ser.readline()
		if(res.startswith("+CMTI:")): #AT command for incoming text, not necessarily be printed but it looks like this "+CMTI: "SM", 1" where "SM" is the status and 1 is the message ID
			pos = res.index(",") #Indexing "," in "+CMTI: "SM", 1"
			storage_id = res[pos+1:] #Locate the message ID
			print storage_id #Prints message ID
			ser.write("AT+CMGR=") #AT command for reading the incoming text
	 		ser.write(storage_id) #AT command to trigger the module to read the text on the given message ID
	 		res = ser.readlines()
	 		print res
	 		print res[2] #Line 2 on the on the output of res, which is basically the content of the text sent to the module
	 		if(res[2].startswith("off")): 
	 			relay_func() #If the owner sends "off" it will proceed to function "relay_func"
	 		elif(res[2].startswith("gps")):
	 			gps_func() #If the owner sends "gps" it will proceed to function "gps_func"
		
except KeyboardInterrupt:
	GPIO.cleanup()

finally:
	GPIO.cleanup()
	
	
	
