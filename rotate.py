# import the opencv library 
import cv2 
import numpy as np

# define a video capture object 
vid = cv2.VideoCapture(0) 

colums = 540
rows = 380

rotation = 90

while(True): 
	
	# Capture the video frame 
	# by frame 
	ret, frame = vid.read() 
	
	# Resize to get the colums and rows
	frame = cv2.resize(frame, (colums, rows), fx = 0, fy = 0,
                         interpolation = cv2.INTER_CUBIC)
	
	# rotate the frame using transformation matrix
	# input is certerpoint, angle, scale
	M = cv2.getRotationMatrix2D(((colums-1)/2.0,(rows-1)/2.0),rotation,1)
	frame = cv2.warpAffine(frame,M,(colums,rows))

	# Display the resulting frame 
	cv2.imshow('frame', frame) 
	
	# example of processing different keys
	pressedKey = cv2.waitKey(1) & 0xFF
	if pressedKey == ord('q'): 
		break
	if pressedKey == ord('r'):
		rotation = rotation + 9q0
		if rotation == 360:
			rotation = 0
		print(rotation)



# After the loop release the cap object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 

