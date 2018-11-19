#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import time
import Q #import Dr.Freudenthal's Queue

emptySem = threading.Semaphore() #empty queue
fullSem = threading.Semaphore() #full queue
emptySem2 = threading.Semaphore() #empty queue
fullSem2 = threading.Semaphore() #full queue

def extractFrames(fileName, extractionQueue):

    #ORIGINAL WORKED WITH 1 PRODUCER 1 CONSUMER
    #fullSem.acquire()

    #attempt 2, works with 1P1C and no queue limit
    #emptySem.acquire()
    
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
        emptySem.acquire()
        extractionQueue.put(jpgAsText)
        fullSem.release()
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    #ORIGINAL WORKED  WITH 1 PRODUCER 1 CONSUMER
    #emptySem.release()
    
    print("End extract")

    #works with no queue limit
    #fullSem.release()


def convertToGray(extractionQueue, displayQueue):
     #THIS ONE WORKED!!  WITH 1 PRODUCER 1 CONSUMER
     #emptySem.acquire()

     #works with no queue limit
     #fullSem.acquire()
     #emptySem2.acquire()
     
     print("start grey!")
     outputDir    = 'frames' #global

     count = 0 #initialize frame count
     
     
     #while True:
     while not extractionQueue.empty() or not displayQueue.full():
     
       #CONSUMER, takes extracted frame
       fullSem.acquire()
       frameAsText = extractionQueue.get()
       emptySem.release()
       
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

       #PRODUCER, stores to display
       #fullSem.acquire()
       emptySem2.acquire()
       displayQueue.put(jpgAsText)
       #emptySem.release()
       fullSem2.release()

      
       count += 1


     #ORIGINAL ONE, WORKED FOR 1 PRODUCER 1 CONSUMER!!
     #fullSem.release()

     print("end grey!")

     #Works with no queue limit
     #emptySem.release()
     #fullSem2.release()


def displayFrames(displayQueue):

   
    print("start display! ") 
    # initialize frame count
    count = 0
    # go through each frame in the buffer until the buffer is empty
    while True:
    #while not displayQueue.empty():
        if not displayQueue.empty():

           #CONSUMER 2
           #get the next frame
           fullSem2.acquire()
           frameAsText = displayQueue.get()
           emptySem2.release()

           # decode the frame 
           jpgRawImage = base64.b64decode(frameAsText)

           # convert the raw frame to a numpy array
           jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
           # get a jpg encoded frame
           img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

           print("Displaying frame {}".format(count))        

           # display the image in a window called "video" and wait 42ms
           # before displaying the next frame
           if img:
                cv2.imshow("Video", img)
                if cv2.waitKey(42) and 0xFF == ord("q"):
                     break
        
           count += 1

     
    print("end displaying")
    # cleanup the windows
    cv2.destroyAllWindows()

    #emptySem2.release()



filename = 'clip.mp4' #name of clip to load

extractionQueue = queue.Queue(10) #extract->grey queue
displayQueue = queue.Queue(10)    #grey->display queue

extractT = threading.Thread(target = extractFrames, args=(filename,extractionQueue))
grayT = threading.Thread(target = convertToGray, args=(extractionQueue,displayQueue)) 
displayT = threading.Thread(target = displayFrames, args=(displayQueue,)) 

#while True:
extractT.start()
grayT.start()
displayT.start()


class producerThread(threading.Thread):
     def run(self):
          while True:
               print("setting producer ")
               #sem_wait -> acquire
               #sem_post -> release
               #emptySem.acquire()
               
               print("starting producer thread")
               #t.start()
               mutex.release()
               #fullSem.release()
               print("release all sems")

class consumerThread(threading.Thread):
     def run(self):
          while True:
               print(" starting consumer ")
               #fullSem.acquire()
               mutex.acquire()
               if not extractionQueue.empty() or displayQueue.empty():
                    print ("One or both queues are empty, wasting runtime anyways")
               print("starting consumer process")
               #t.start()
               mutex.release()
               #emptySem.release()

#debugging, methods run through threads
#Starting multithreads works with both eqs for ext and gray
#display ends early on however
#extractT.start()
#grayT.start()
#displayT.start()


#maybe needs init 
#producerThread(extractT).start()
#consumerThread(grayT).start()

#freud said: The threads that obtain and decode the frames should communicate via PC sync
