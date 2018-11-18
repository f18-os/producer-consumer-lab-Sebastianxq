#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import time


#issue getting from buff
def convertToGray(extractionQueue, displayQueue):
     print("start grey!")
     outputDir    = 'frames' #global

     count = 0 #initialize frame count
     
     while not extractionQueue.empty() or not displayQueue.full():
       #gets next frame
       frameAsText = extractionQueue.get()
       
       # decode the frame 
       jpgRawImage = base64.b64decode(frameAsText)

       # convert the raw frame to a numpy array
       jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
       # get a jpg encoded frame
       img = cv2.imdecode(jpgImage ,cv2.IMREAD_UNCHANGED)
       
       print("Converting frame {}".format(count))
        
       # convert the image to grayscale
       greyFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

       #encode the frame as base 64 to make debugging easier
       jpgAsText = base64.b64encode(greyFrame)

       # add the frame to the next buffer
       displayQueue.put(jpgAsText)
       
       count += 1
 
     print("end grey!")

def extractFrames(fileName, extractionQueue):
    print("start extract frames!")
    # Initialize frame count 
    count = 0
    
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print("Reading frame {} {} ".format(count, success))
    #while success:
    while success and not extractionQueue.full():
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        extractionQueue.put(jpgAsText)
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("End extract")


def displayFrames(displayQueue):
    print("start display! ") 
    # initialize frame count
    count = 0
    # go through each frame in the buffer until the buffer is empty
    while not displayQueue.empty():
        # get the next frame
        frameAsText = displayQueue.get()

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

    print("end displaying")
    # cleanup the windows
    cv2.destroyAllWindows()



filename = 'clip.mp4' #name of clip to load

emptySem = threading.Semaphore() #empty queue
fullSem= threading.Semaphore() #full queue
mutexSem= threading.Semaphore() #for mutual exclusion
mutex = threading.Lock()

extractionQueue = queue.Queue(10) #extract->grey queue
displayQueue = queue.Queue()    #grey->display queue

extractT = threading.Thread(target = extractFrames, args=(filename,extractionQueue))
grayT = threading.Thread(target = convertToGray, args=(extractionQueue,displayQueue)) 
displayT = threading.Thread(target = displayFrames, args=(displayQueue,)) 

def producer(t):
     while True:
          print("setting producer ")
          #sem_wait -> acquire
          #sem_post -> release
          emptySem.acquire()
          mutex.acquire()
          print("starting producer thread")
          t.start()
          mutex.release()
          fullSem.release()
          print("release all sems")
          
def consumer(t):
     while True:
          print(" starting consumer ")
          fullSem.acquire()
          mutex.acquire()
          if not extractionQueue.empty() or displayQueue.empty():
               print ("One or both queues are empty, wasting runtime anyways")
          print("starting consumer process")
          t.start()
          mutex.release()
          emptySem.release()

#test relationship with extrac->grey so no limit on grey queue
#likely cant modulate grey->display however
#extractT,grayT,displayT


#debugging, methods run normally
#extractFrames(filename,extractionQueue)
#convertToGray(extractionQueue)

#debugging, methods run through threads
extractT.start()
grayT.start()
#methods run through PC
#consumer(grayT)
#producer(extractT)
