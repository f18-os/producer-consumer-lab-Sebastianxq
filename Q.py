import threading
import time

emptySem = threading.Semaphore(10) #stops from insetions to an full queue
fullSem = threading.Semaphore() #stops from insertions in a empty queue
lock = threading.Lock() #mutual exclusion when putting/getting queue

class Queue:

  def __init__(self):
      self.queue = list()

  def put(self,dataval):
      #if dataval not in self.queue:
      self.queue.insert(0,dataval)
     
# Pop method to remove element
  def get(self):
      if len(self.queue)>0:
          return self.queue.pop()
      
  
#class Queue1:
 #   def __init__(self):
  #      self.items = []

   # def isEmpty(self):
    #    return self.items == []

    #"consumer"
   # def put(self, item):
        #emptySem.acquire()
        #lock.acquire()
    #    self.items.insert(0,item)
        #lock.release()
        #fullSem.release()

    #"producer"
   # def get(self):
        #fullSem.acquire()
        #lock.acquire()
    #    return self.items.pop()
        #lock.release()
        #emptySem.release()

#freudenthal's queue class
#class Queue:
 #   def __init__(self, initArray = []):
  #      self.a = []
   #     self.a = [x for x in initArray]
    #def put(self, item):
     #   emptySem.acquire()
      #  lock.acquire()
       # self.a.append(item)
      #  lock.release()
      #  fullSem.release()
   # def get(self):
    #    fullSem.acquire()
     #   lock.acquire()
      #  a = self.a
       # item = a[0]
     #   del a[0]
     #   lock.release()
      #  emptySem.release()
      #  return item
   # def __repr__(self):
    #    return "Q(%s)" % self.a

 

#old attempt at queue implementation
#---------------------------------------------------
        #class Q:
    #create queue with a default size
#    def __init__(self, length):
#        self.length = length
#        self.head = None

 #   def is_empty(self):
  #      return self.length == 0

    #"produce"
   # def put(self, info):
    #    node = Node(info)
     #   emptySem.acquire()
      #  lock.acquire()
       # if self.head is None:
            # If list is empty the new node goes first
        #    self.head = node
       # else:
            # Find the last node in the list
   #         last = self.head
   #         while last.next:
   #             last = last.next
            # Append the new node
   #         last.next = node
   #     self.length += 1
   #     lock.release()
   #     fullSem.release()

    #"consume"
  #  def get(self):
   #     fullSem.acquire()
    #    lock.acquire()
     #   info = self.head.info
      #  self.head = self.head.next
       # self.length -= 1
       # lock.release()
        #emptySem.release()
        #return info
