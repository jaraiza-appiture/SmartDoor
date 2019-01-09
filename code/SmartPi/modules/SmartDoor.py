import random
import re
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import face_recognition
import cv2
#import socket
import time
UDP_IP = "192.168.254.34"
UDP_PORT = 5005

MSG = "Open Door"
THRESH = 0

WORDS = ["OPEN DOOR", "OPENDOOR", "OPEN"]

def initialize_camera():
	# start the FPS counter
    # initialize the video stream and allow the camera sensor to warm up
    
    print("[SmartDoor] starting video stream...")
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(0.5)
    fps = FPS().start()
    return vs, fps
def connect_to_door(): #figure out how to disconnect connection properly 
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return sock
def handle(text, mic, profile,data,detector,sock):
    """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    mic.say("Identifying.")

    # sock = connect_to_door()
    vs, fps = initialize_camera()
    
    FramesProcessed = 0
    OpenDoor = False
    ThreshCount = {}
    
    # loop over frames from the video file stream
    while FramesProcessed < 15:
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speedup processing)
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        
        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        
        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],
                encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]

                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)
            # update the list of names
            names.append(name)

        # loop over the recognized faces
        #for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
        #   cv2.rectangle(frame, (left, top), (right, bottom),
        #       (0, 255, 0), 2)
        #   y = top - 15 if top - 15 > 15 else top + 15
        #   cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
        #       0.75, (0, 255, 0), 2)


        for name in names:
            ThreshCount[name] = ThreshCount.get(name, 0) + 1

        NamesFound = []
        for name, ocur in ThreshCount.items():
            if ocur > 5:
                NamesFound.append(name)
                OpenDoor = True
        

        # display the image to our screen
        #  cv2.imshow("Frame", frame)
        #  key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        #if key == ord("q"):
        #    break

        if OpenDoor:
            sock.sendto(MSG.encode(),(UDP_IP,UDP_PORT))
            mic.say("Welcome home.")
            for name in NamesFound:
                mic.say(name)
            break

        # update the FPS counter
        fps.update()

        FramesProcessed +=1

    # stop the timer and display FPS information

    fps.stop()
    if not OpenDoor:
        mic.say("Sorry. I can not let you in stranger. Kindly fuck off.")
    print("[SmartDoor] elasped time: {:.2f}".format(fps.elapsed()))
    print("[SmartDoor] approx. FPS: {:.2f}".format(fps.fps()))
    print("[SmartDoor] Names found: %s"%(ThreshCount))
	
	# do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()


def isValid(text):
    """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    Valid = bool(re.search(r'\bopen door\b', text, re.IGNORECASE)) or bool(re.search(r'\bopen\b', text, re.IGNORECASE))
    return Valid
