#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

#coordinate threads with binary/counting semaphores between 2 producers, 2 consumers
#thread 0 reads frames from file
#thread 1 will take the frames and convert to grayscale
#thread 2 will display the frames
#all threads run concurrently

#newSteps
#create producer consumer relationshipfor grayscale and extract
#create producer consumer for extract and display (already exists??)

#takes in file, outputs the frame in gray
def convertToGray(fileName, outputBuffer):
     print("going to convert to gray!")
     # globals
     outputDir    = 'frames'

     # initialize frame count
     count = 0

     # get the next frame file name
     inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

     # load the next file
     inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

     while inputFrame is not None:
       print("Converting frame {}".format(count))

       # convert the image to grayscale
       grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
       
       # generate output file name
       outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

       # write output file
       cv2.imwrite(outFileName, grayscaleFrame)

       count += 1
 
       # generate input file name for the next frame
       inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

       # load the next frame
       inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

def extractFrames(fileName, outputBuffer):
    print("going to extract frames!")
    # Initialize frame count 
    count = 0
    
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print("Reading frame {} {} ".format(count, success))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputBuffer.put(jpgAsText)
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")


def displayFrames(inputBuffer):
    print("going to display the frames now!") 
    # initialize frame count
    count = 0
    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():
        # get the next frame
        frameAsText = inputBuffer.get()

        # decode the frame 
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()



#start of "main"
filename = 'clip.mp4' #name of clip to load
#semaphore for the system LIKELY NOT NEEDED
syncSemaphore = threading.Semaphore()

extractionQueue = queue.Queue() #shared queue, limited to 10 objects at a time

grayT = threading.Thread(target = convertToGray, args= (filename,extractionQueue)) #make target = ConvertToGrayscale
extractT = threading.Thread(target = extractFrames, args=(filename,extractionQueue))# make target = extractFrames
displayT = threading.Thread(target = displayFrames, args=(extractionQueue,)) #make target = DisplayFrames

# extract the frames
#extractFrames(filename,extractionQueue)
# display the frames
#displayFrames(extractionQueue)

#gets to 10 frames in extract and deadlocks on extract with filled buffer
#gray has issues putting frames into buffer
try:
    #grayT.start()
    #extractT.start()
    displayT.start()
except:
    print ("error starting the threads")


