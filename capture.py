# import the opencv library 
import cv2 
import numpy as np

# define a video capture object 
vid = cv2.VideoCapture(0) 

while(True): 
	
	# Capture the video frame 
	# by frame 
	ret, frame = vid.read() 
	frame = cv2.resize(frame, (540, 380), fx = 0, fy = 0,
                         interpolation = cv2.INTER_CUBIC)

	# Display the resulting frame 
	cv2.imshow('frame', frame) 
	
	# conversion of BGR to grayscale is necessary to apply this operation
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    # adaptive thresholding to use different threshold 
    # values on different regions of the frame.
	Thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)


	cv2.imshow('Tresh', Thresh) 
	# the 'q' button is set as the 
	# quitting button you may use any 
	# desired button of your choice 
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

# After the loop release the cap object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 

