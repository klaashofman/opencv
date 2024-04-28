# simple, full screen and scaled video player
import cv2
import os, glob

framesize=(800,480)
# path to the video files, can be relative or absolute path

# videodir="/Users/klaashofman/Development/Rimshot/sandbox/opencv/video"
videodir="video"

fullscreen = False

def play(file, framesize=(800,480)):
    cap = cv2.VideoCapture(file)

    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    if fullscreen:
        cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, framesize)
            cv2.imshow('Frame', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else: 
            print ("eof")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # find all video files in the current directory
    # os.chdir(videodir)
    files = glob.glob("video/*.mp4")

    # play all in a loop
    while True:
        for file in files:
            print(file)
            play(file, framesize)
