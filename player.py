# simple, full screen and scaled video player
import cv2

framesize=(800,480)
file='1280x720.mp4'

cap = cv2.VideoCapture(file)

if (cap.isOpened()== False): 
  print("Error opening video stream or file")

while(cap.isOpened()):
  ret, frame = cap.read()
  if ret == True:
    frame = cv2.resize(frame, framesize)
    cv2.imshow('Frame', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
  else: 
    break

cap.release()
cv2.destroyAllWindows()

