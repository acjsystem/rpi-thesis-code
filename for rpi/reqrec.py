import json,requests

#changeable
#change the urls on prod
PLATE_NO = "TEJ123"
web_status="https://"
website="acarjsystem.herokuapp.com"

def get_user_number():
	#this method is for getting user's number
	global cont_no
	url = web_status + website + "/userdata/"
	req_info = {
		'plate_no':PLATE_NO
	}
	response = requests.post(url=url, data=req_info)
	print (response.json())
	print (response.json()['cont_no'])
	contact_no=response.json()['cont_no']
	
def get_car_stat():
	#this method is for getting initial values
	#assigning of global variables
	global car_id
	global user
	global ignition
	global taser
	global loc_stat
	global photo_stat
	global date_reported
	url = web_status + website + "/cardetail/"
	req_info = {
		'plate_no':PLATE_NO
	}
	response = requests.post(url=url, data=req_info)
	print (response.json())
	if response.json()['Error'] == "True":
		print ("BAD REQUEST")
	else:
		print (response.json()['car'])
		print (response.json()['car_stat'])
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
		else:
			print ("CAR IS NOT TURNED ON")

def post_report_stat():
	#for sending report stat when there is a difference in command from sms and db standard is time
	#checking whether carstat = true so report can add
	url = web_status + website + "/cardetail/"
	req_info = {
		'plate_no':PLATE_NO
	}
	response = requests.post(url=url, data=req_info)
	print (response.json())
	if response.json()['Error'] == "True":
		print ("BAD REQUEST")
	else:
		print (response.json()['car'])
		print (response.json()['car_stat'])
		car_stat = response.json()['car_stat']
		if car_stat == "True":	
			url = web_status + website + "/addreport/"
			req_info = {
				'car_id' : car_id,
				'user' : user,
				"car_loc_stat": "", #change this when data is finalized
				"car_ignition": "", #change this when data is finalized
				"taser_stat": "", #change this when data is finalized
				"car_loc_stat": "", #change this when data is finalized
				"car_photo_stat": "", #change this when data is finalized
				'report_stat':''	#change this when report is no longer filed
			}
			response = requests.post(url=url, data=req_info)
			print (response.json())
		else:
			print ("CAR IS NOT TURNED ON")
	

def apply_command():
	#this will apply all the states received by the rpi ie send photo and location
	#get data for image and location here
	pass
	
def post_rep_info():
	#for sending/uploading photo and location
	#check wthere car stat = true to update db
	url = web_status + website + "/cardetail/"
	req_info = {
		'plate_no':PLATE_NO
	}
	response = requests.post(url=url, data=req_info)
	print (response.json())
	if response.json()['Error'] == "True":
		print ("BAD REQUEST")
	else:
		print (response.json()['car'])
		print (response.json()['car_stat'])
		car_stat = response.json()['car_stat']
		if car_stat == "True":
			url = web_status + website + "/addreport/"
			req_info = {
				'car_id' : car_id,
				'user' : user,
				'car_loc':'', 	#place coordinates here
				'rep_photo':''	#place image here
			}
			response = requests.post(url=url, data=req_info)
			print (response.json())
		else:
			print ("car is not on")

	
get_user_number()
#check if there is an sms then store values given to a different variable
get_car_stat()
#compare it against the car_stat using date and time
#if sms is newer(check_sms_and_db) and is not equal to the DB's status update DB using (post_report_stat) dont send car loc and photo yet
#only use the next method if there is a change when comparing data from sms and data from db okay? tnx
post_report_stat()
#get the final status of commands then apply to the hardware
#then after updating, (activate the status ordered by the user) use (post_rep_info) send car loc and photo here
post_rep_info()