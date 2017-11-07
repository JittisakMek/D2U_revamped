import RPi.GPIO as GPIO
import motor
import sys
import time
import Sonar
import delivery
import numpy as np
import myFirebase
from multiprocessing import Process, Queue
from threading import Barrier
import threading
import VideoFilter
################################Using the one in run###########
ThreshTurnLeft = 100    #DO NOT ABRUPTLY TURN MY ROBOT !!!
ThreshTurnRight = 100   #DO NOT ABRUPTLY TURN MY ROBOT !!!
ThreshForwardRight = 50
ThreshForwardLeft = 50
ThreshFront = 50

cur = 0
isAscending = False
#shotest path
#justwalk
#finnish

#Things to update
#Finish() function have to use ultrasonic so function in control()?
#When reach corner detect after crossing detect destination or turn left or right
#Function cross -> runNoWall
#Separate function in VideoFilter

def ReadQueue(lock1,lock2,q):
        lock1.acquire()
        lock2.acquire()
        lock1.release()
        data = q.get()
        lock2.release()
        time.sleep(0.01)

def runWall(left, right, front):
    if front>40:
        if right<25:
            if right < 5:
                motor.robot_leftforward(50)
                
            else:
                motor.robot_leftforward(30)
                
        elif left<25:
            if left < 5:
                motor.robot_rightforward(50)
            else:
                motor.robot_rightforward(30)
                
        else:
            motor.robot_forward()
    else:
        motor.robot_stop()
        
def PRINT(q):
    while True:
        if not q.empty():
            print(q.get())

def cornerCheck(cur):
    if cur == 1 or cur == 7 or cur == 8 or cur == 14:
        corner = True

    else:
        corner = False

    return corner

def nodeAscendingCheck(source, destination)  :
    global isAscending
    if destination > source:
        ascending = True
    else:
        ascending = False
        
    isAscending = ascending

def decision(source, destination):
    #0=no turn
    #1=turnLeft
    #2=turnRight
    global cur
    global isAscending
    
    if cur == 1 and not isAscending:
        #robot cross
        pass
    elif cur == 14 and isAscending:
        #robot cross
        pass
    elif cur == 7 and isAscending:
        #robot cross
        pass
    elif cur == 8 and not isAscending:
        #robot cross
        pass
    else:
        if isAscending:
            motor.turn_left()
            motor.camLeft()  #YES Ascending
        else:
            motor.turn_right()
            motor.camRight() #NO Descending

def delivering():
        

def finish():
    if isAscending():
            motor.turn_left()
            
def Control(q,qprint,src,dest):
    global cur
    Sonar.ultraInit()
    On = Sonar.SoNarUse()
    On.Distance = 10
    SR = threading.Thread(target = Sonar.SoNarRight,args = (On.R,On.b,On.On))
    SL = threading.Thread(target = Sonar.SoNarLeft,args = (On.L,On.b,On.On))
    SF = threading.Thread(target = Sonar.SoNarFront,args = (On.F,On.b,On.On))

    SR.start()
    SL.start()
    SF.start()

    motor.QuickStart()
    nodeAscendingCheck(src,dest)
    decision(src,dest)
    
    while q.empty():
    
        On.b.wait()
        if cornerCheck(cur):
            decision(src,dest)
            runWall(On.L.Distance, On.R.Distance, On.F.Distance)
        else:
            runWall(On.L.Distance, On.R.Distance, On.F.Distance)
        On.b.wait()

    On.b.wait()
    On.On.Distance = 0;
    On.b.wait()
    
def auto():
    #input destination sorc
    [curQ, inQ] = myFirebase.readData()
    [src, dest] = myFirebase.getScrDest(myFirebase.getTaskDetail(curQ))
    print('Source = ',src,'\n','Destination = ',dest)
    global cur
    global isAscending
    cur = src
    
    qprint = Queue()
    qcontrol = Queue()
    qvideo = Queue()
    p_vid = Process(target = VideoFilter.videoFilter, args = (3,qvideo))
    p_control = Process(target = Control, args = (qcontrol,qprint, src, dest))
    p_print = Process(target = PRINT, args = (qprint,))
    p_print.start()
    p_vid.start()
    p_control.start()
   
    while(cur!=dest):
        qprint.put(cur)
        time.sleep(0.1)
        #CURRENT NODE UPDATE
        if not(qvideo.empty()):
            
            if isAscending:
                cur = cur+(ReadQueue(lock1,lock2,qvideo))  
            else:
                cur = cur-(ReadQueue(lock1,lock2,qvideo))
                
            if cur == 15:
                cur = 1
            elif cur == 0:
                cur = 14
        else:
            pass
        
    qcontrol.put(1)
        
    #start thread video filter
    #process or thread Control(q)
    #while(not destination
    #if get node node+++ where is the robot
    # if destination q.put(1)
    #join with video process
    #finish()

    
def main():
    try:
        auto()
    except KeyboardInterrupt:
        GPIO.cleanup()
    

if __name__ == "__main__":
    main()
