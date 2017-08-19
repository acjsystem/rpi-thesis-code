import picamera

photo_folder='images/'

camera = picamera.PiCamera()
camera.capture(photo_folder+'first_take.jpg')
print ("photo taken")
