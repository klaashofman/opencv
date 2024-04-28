# simple, full screen and scaled video player
import cv2
import glob
from ffpyplayer.player import MediaPlayer

framesize=(800,480)
# path to the video files, can be relative or absolute path

# videodir="/Users/klaashofman/Development/Rimshot/sandbox/opencv/video"
videodir="video"

# set the video to full screen
fullscreen = False

# play audio
playaudio = True


def play(file, framesize=(800,480)):
    rv = True
    cap = cv2.VideoCapture(file)
    player = MediaPlayer(file) if playaudio else None

    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    if fullscreen:
        cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while(cap.isOpened()):
        ret, frame = cap.read()
        audio_frame, val = player.get_frame() if playaudio else (None, None)

        if ret == True:
            frame = cv2.resize(frame, framesize)
            cv2.imshow('Frame', frame)
            
        else: 
            print ("eof video")
            break
        
        if playaudio and val != 'eof' and audio_frame is not None:
            #audio
            img, t = audio_frame

        elif playaudio and val == 'eof':
            print("eof audio")
            break
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            rv = False
            break

    cap.release()
    cv2.destroyAllWindows()
    return rv

if __name__ == "__main__":
    # find all video files in the current directory
    files = glob.glob("video/*.mp4")

    # play all in a loop
    while True:
        for file in files:
            if not play(file, framesize):
                exit(0)