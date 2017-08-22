import json, requests, picamera,time

photo_folder='images/'
#images_taken=1
camera = picamera.PiCamera()

for images_taken in range(1,3): 
	photo_loc=photo_folder+'first_take'+str(images_taken)+'.jpg'
	camera.capture(photo_loc)
	time.sleep(3)
	print ("photo taken")
print ("photo taken")
