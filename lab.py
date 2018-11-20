#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import time

emptySem = threading.Semaphore(10) #empty queue
fullSem = threading.Semaphore() #full queue
lock = threading.Semaphore(0) #mutex
emptySem2 = threading.Semaphore(10) #empty queue for display
fullSem2 = threading.Semaphore() #full queue for display
lock2 = threading.Semaphore(0) #mutex for display

def extractFrames(fileName, extractionQueue):
    
    print("start extract frames!")
    # Initialize frame count 
    count = 0
    
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print("Reading frame {} {} ".format(count, success))
    while success:
    #while success and not extractionQueue.full():

        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #debugging, ensures a picture is actually there
        #cv2.imshow("extractImg",jpgImage)
        
        
        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        #definitelyText
        #print("producing the following for 1st queue")
        #print(jpgAsText)
        
        # add the frame to the buffer
        emptySem.acquire()
        #lock.acquire()
        extractionQueue.put(jpgAsText)
        #lock.release()
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
     print("start grey!")

     count = 0 #initialize frame count
     
     while True:
     #while not extractionQueue.empty() or not displayQueue.full():
     
       #CONSUMER, takes extracted frame
       fullSem.acquire()
       #lock.acquire()
       frameAsText = extractionQueue.get()
       #lock.release()
       emptySem.release()

       #consumer1 debugger, seems like it works
       #print("below is what is taken from queue1")
       #print(frameAsText)
       
       # decode the frame 
       jpgRawImage = base64.b64decode(frameAsText)

       # convert the raw frame to a numpy array
       jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
       #get a jpg encoded frame
       img = cv2.imdecode(jpgImage ,cv2.IMREAD_UNCHANGED)
       
       print("Converting frame {}".format(count))
        
       # convert the image to grayscale
       #originally img
       greyFrame = cv2.cvtColor(frameAsText, cv2.COLOR_BGR2GRAY)

       #encode the frame as base 64 to make debugging easier
       jpgAsText = base64.b64encode(greyFrame)

       #producer 2 debugger, is definitely a bunch of text
       #print("below is what is going into queue 2")
       #print(jpgAsText)
       
       #PRODUCER, stores to display
       emptySem2.acquire()
       #lock2.acquire()
       displayQueue.put(greyFrame)
       #lock2.release()
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
        #if not displayQueue.empty():
        
           #CONSUMER 2, gets frame to display
           fullSem2.acquire()
           #lock2.acquire()
           frameAsText = displayQueue.get()
           #lock2.release()
           emptySem2.release()

           #debugging
           #print("consumer 2 is going to get the following")
           #print(frameAsText)

           # decode the frame 
           jpgRawImage = base64.b64decode(frameAsText)

           # convert the raw frame to a numpy array
           jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
           # get a jpg encoded frame
           img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

           print("Displaying frame {}".format(count))        

           
           #print(img)
           # display the image in a window called "video" and wait 42ms
           # before displaying the next frame
           #if img is not None:
           #print("really showing the image!")
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



#freud said: The threads that obtain and decode the frames should communicate via PC sync


#print the type of data at each encode and decode to ensure that you dont goof something
#don't need conversion of data?
#FOR DEBUGGING do a base64 encode and then ensure that the same digits are the same before and after each queue to ensure that everything works


#NOTES:
#Extract Does it's job fine
#Display does it's job fine

#ISSUES
#Need to fix GREYSCALE CONVERSION
#Need to fix  LOCKS
#Need to fix an exit protocol when it's done

#Extract/Display work with Sems and any size que
   #need to test out with lock??
#went over sem implementation on Oct23
