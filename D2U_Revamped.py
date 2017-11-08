import RPi.GPIO as GPIO
import motor
import sys
import time
import Sonar
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
flag = False # signal Video to start
#Things to update
#Finish() condition for destination == corner
#Complete the condition decision for corner
#Function cross -> runNoWall

def ReadQueue(lock1,lock2,q):
        lock1.acquire()
        lock2.acquire()
        lock1.release()
        data = q.get()
        lock2.release()
        time.sleep(0.01)

def PRINT(q):
    while True:
        if not q.empty():
            print(q.get())

def runR(left, right, front):
    if front>40:
            if right<25:
                if right < 5:
                    motor.robot_leftforward(50)
                    
                else:
                    motor.robot_leftforward(30)
                    
            elif right>30 or left<30:
                if right < 40:
                    motor.robot_rightforward(20)
                else:
                    motor.robot_rightforward(30)

            else:
                motor.robot_forward()
        
    else:
        motor.robot_stop()
        
def runL(left, right, front):
        if front>40:
                if left<25:
                    if left < 5:
                        motor.robot_rightforward(50)
                        
                    else:
                        motor.robot_rightforward(30)
                        
                elif left>30 or right<30:
                    if left < 40:
                        motor.robot_leftforward(20)
                    else:
                        motor.robot_leftforward(30)
                else:
                    motor.robot_forward()
                    #print('robot_forward')
        else:
                motor.robot_stop()
                #print('robot_stop')
                
def cornerCheck(cur):
    if cur == 1 or cur == 7 or cur == 8 or cur == 14:
        corner = True

    else:
        corner = False

    return corner

def nodeAscendingCheck(source, destination):
    if destination > source:
        ascending = True
    else:
        ascending = False
        
    return ascending

def decision(isAscending):
#TURN LEFT or TURN RIGHT or FORWARD
    global cur
    
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

def finish():
    #No need for ultraInit() and motor.QuickStart() again
    On = Sonar.SonarUse()
    On.Distance = 10
    SF = threading.Thread(target = Sonar.SoNarFront,args = (On.F,On.b,On.On))
    
    if isAscending():
        motor.turn_left()
    else:
        motor.turn_right()

    SF.start()
    On.b.wait()
    while True:
        On.b.wait()
        if On.F.Distance>36:
                motor.robot_forward()
        elif On.F.Distance<=36:
                break
        On.b.wait()
    #Turn OFF Ultrasonic  
    On.b.wait()
    On.On.Distance = 0;
    On.b.wait()
    #KNOCK
    motor.robot_stop()
    motor.knock()
    
    print('***PUSH***')
    while GPIO.input(motor.SW) != True:
        pass
    turn_back()
    robot_stop()
               
def Control(q,src,dest):
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
    isAscending = nodeAscendingCheck(src,dest)
    decision(isAscending) #decision check before loop because turning does not happen all the time except for corners
    flag = True;
    while q.empty():
    
        On.b.wait()
        if cornerCheck(cur):
            decision(src,dest)
            runR(On.L.Distance, On.R.Distance, On.F.Distance)
        else:
            runR(On.L.Distance, On.R.Distance, On.F.Distance)
        On.b.wait()

    On.b.wait()
    On.On.Distance = 0;
    On.b.wait()
    
def auto():
    global cur
    
    [curQ, inQ] = myFirebase.readData()
    [src, dest] = myFirebase.getScrDest(myFirebase.getTaskDetail(curQ))
    src = int(src)
    dest = int(dest)
    
    while(src<1 or src>14 or dest<1 or dest>14):
            print('Retrieving source and destination.....')
            time.sleep(0.3)
    print('Source = ',src,'\n','Destination = ',dest)

    cur = src
    isAscending = nodeAscendingCheck(src,dest)
    
    qvideo = Queue()
    qcontrol = Queue()
    qprint = Queue()
    p_vid = Process(target = VideoFilter.videoFilter, args = (qvideo))
    p_control = Process(target = Control, args = (qcontrol, src, dest))
    p_print = Process(target = PRINT, args = (qprint,))
    p_control.start()
    while flag == false:
        print('Waiting for VideoSignal...')
        time.sleep(0.2)
        pass
    p_vid.start()
    p_print.start()
   
    while(cur!=dest):
            qprint.put(cur)
            time.sleep(0.1)

            if qvideo.empty() != true:
            #CURRENT NODE UPDATE
                if isAscending:
                    cur = cur+qvideo.get() 
                else:
                    cur = cur-qvideo.get()
                    
                if cur == 15:
                    cur = 1
                elif cur == 0:
                    cur = 14
    qvideo.put(0)
    qcontrol.put(0)
    finish()
    p_vid.join()
    p_control.join()
    p_print.join()
    
def main():
   try:
       while True:
         
          auto()
          #For Debug only
          ans = input('Continue [C] | Quit[Q]: ')
          if ans.lower() == 'q':
             break
            
   except KeyboardInterrupt:
      motor.QuickStop()
      GPIO.cleanup()
    
if __name__ == "__main__":
    main()
