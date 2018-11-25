
#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import time
import Q

emptySem = threading.Semaphore(10) #empty queue
fullSem = threading.Semaphore(0) #full queue
lock = threading.Lock() #mutex
emptySem2 = threading.Semaphore(10) #empty queue
fullSem2 = threading.Semaphore(0) #full queue
lock2 = threading.Lock() #mutex

def extractFrames(fileName, extractionQueue):
    print("start extract frames!")
     
    count = 0 #frame count
    
    vidcap = cv2.VideoCapture(fileName) #open video file
    success,image = vidcap.read() #read first image
    
    while success:

        #Producer 1, stores frame into queue
        emptySem.acquire()
        lock.acquire()
        extractionQueue.put(image)
        lock.release()
        fullSem.release()
       
        success,image = vidcap.read()
        #print('Reading frame {} {}'.format(count, success))
        count += 1
    
    print("End extract")

    #Create and enqueue flag (black frame) to signal EOF
    blank_image = np.zeros((0,0,0), np.uint8)
    emptySem.acquire()
    lock.acquire()
    extractionQueue.put(blank_image)
    lock.release()
    fullSem.release()
        
def convertToGray(extractionQueue, displayQueue):
     print("start grey!")

     #creates and encodes local black frame for flag comparison
     blank_image = np.zeros((0,0,0), np.uint8)
     blankText = base64.b64encode(blank_image)

     count = 0 #initialize frame count
     
     while True:
     
       #Consumer 1, takes extracted frame
       fullSem.acquire()
       lock.acquire()
       colorFrame = extractionQueue.get()
       lock.release()
       emptySem.release()

       #print("Converting frame {}".format(count))

       #flag checker, if flag found, end loop
       colorText = base64.b64encode(colorFrame)    
       if(colorText==blankText):
           emptySem2.acquire()
           lock2.acquire()
           displayQueue.put(blank_image)
           lock.release()
           fullSem2.release()
           break

       #convert the frame to grayscale
       greyFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)
       
       #Producer 2, stores to display
       emptySem2.acquire()
       lock2.acquire()
       displayQueue.put(greyFrame)
       lock2.release()
       fullSem2.release()

       count += 1


     print("end grey!")

       

def displayFrames(displayQueue):
    #vars for ensuring 24fps
    frameInterval_s = 0.042         # inter-frame interval, in seconds
    nextFrameStart = time.time()

    #Creates and endcodes an EOF frame
    blank_image = np.zeros((0,0,0), np.uint8)
    blankText = base64.b64encode(blank_image)

    print(" start display! ") 
    
    count = 0 #frameCount

    while True:
        
           #Consumer 2, gets frame to display
           fullSem2.acquire()
           lock2.acquire()
           frameAsText = displayQueue.get()
           lock2.release()
           emptySem2.release()

           #print("Displaying frame {}".format(count))        

           #checks for flag, if found, end loop and finish thread
           colorText = base64.b64encode(frameAsText)
           if(colorText==blankText):
               print("Finished processing file!")
               break
                                      
           #display the image in a window called "video" and wait 42ms
           cv2.imshow("Video", frameAsText)


           #delay to ensure a consistent framerate during execution
           delay_s = nextFrameStart - time.time()
           nextFrameStart += frameInterval_s
           delay_ms = int(max(1, 1000 * delay_s))
           #print ("delay = %d ms" % delay_ms)
           if cv2.waitKey(delay_ms) and 0xFF == ord("q"):
               break
           
           #old delay
           #if cv2.waitKey(42) and 0xFF == ord("q"):
           #    break
        
           count += 1

     
    print("end displaying")
    # cleanup the windows
    cv2.destroyAllWindows()


filename = 'clip.mp4' #name of clip to load

#extractionQueue = queue.Queue(10) #extract->grey queue
#displayQueue = queue.Queue(10)    #grey->display queue

extractionQueue = Q.Queue() #Extract Queue
displayQueue = Q.Queue()    #Display Queue

extractT = threading.Thread(target = extractFrames, args=(filename,extractionQueue))
grayT = threading.Thread(target = convertToGray, args=(extractionQueue,displayQueue)) 
displayT = threading.Thread(target = displayFrames, args=(displayQueue,)) 

extractT.start()
grayT.start()
displayT.start()

#TODO
#update to allow self defined queue
#own queue should include the semaphores and mutex with get and put



