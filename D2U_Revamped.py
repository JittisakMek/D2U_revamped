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
videoFlag = False # signal Video to start
cornerFlag = False #run cornerDecision only once
runNoWallFlag = False

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
            elif right >= 100:
                motor.robot_forward()
                    
            elif right > 30 or left < 30:
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
                        
                elif left >= 100:
                    motor.robot_forward()
                        
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

def runNoWallR(left, right, front):
    if front > 40:
        if right > 100:
            motor.robot_forward()
            
        elif right < 20:
            
            if right < 5:
                motor.robot_leftforward(50)
                
            else:
                motor.robot_leftforward(30)
                        
        elif left < 30 or right > 30:
            motor.robot_rightforward(30)
                    
        else:
            motor.robot_forward()
    else:
        motor.robot_stop()

def runNoWallL(left, right, front):
    if front > 40:
        if left>100:
            motor.robot_forward()
            
        elif left<20:
            
            if left < 5:
                motor.robot_rightforward(50)
                
            else:
                motor.robot_rightforward(30)
                        
        elif right<30 or left>30:
            motor.robot_leftforward(30)
                    
        else:
            motor.robot_forward()
    else:
        motor.robot_stop()
                
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

def startDecision(isAscending):
    global cur
    global cornerFlag

    if cur == 1 and isAscending:
        #Cross front
        motor.camStraight()
        cornerFlag = True
    elif cur == 14 and not isAscending:
        #Cross front
        motor.camStraight()
        cornerFlag = True
    elif cur == 7 and isAscending:
        #Cross back
        motor.camStraight()
        cornerFlag = True
    elif cur == 8 and not isAscending:
        #Cross back
        motor.camStraight()
        cornerFlag = True
    else:
        if isAscending:
            motor.turn_left()
            motor.camLeft()  #YES Ascending
        else:
            motor.turn_right()
            motor.camRight() #NO Descending
            
def cornerDecision(isAscending):
#TURN LEFT or TURN RIGHT or FORWARD
    global cur
    
    if cur == 1 and isAscending:
        motor.turn_left()
    elif cur == 14 and not isAscending:
        motor.turn_right()
    elif cur == 7 and isAscending:
        motor.camStraight()
        motor.turn_right()
    elif cur == 8 and not isAscending:
        motor.turn_left()
    else:
        if isAscending:
            motor.turn_left()
        else:
            motor.turn_right()

def runNoWallSet():
    if cur == 7 and runNoWallFlag == False:
        node = 7
        runNoWallFlag = True
    elif cur == 8 and runNoWallFlag == False:
        node = 8
        runNoWallFlag = True
    elif cur == 1 and runNoWallFlag == False:
        node = 1
        runNoWallFlag = True
    elif cur == 14 and runNoWallFlag == False:
        node = 14
        runNoWallFlag = True
    else:
        
    
def Control(q,src,dest):
    global cur
    global cornerFlag
    global videoFlag
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
    startDecision(isAscending) #decision check before loop because turning does not happen all the time except for corners
    videoFlag = True;
    
    while q.empty():
    
        On.b.wait()
        if cornerCheck(cur):
            if cornerFlag == False:
                cornerDecision(isAscending)
                cornerFlag = True
            elif cornerCheck(dest):
                if cur == 7 or cur == 14:
                    runNoWallR()
                elif cur == 1 or cur == 8:
                    runNoWallL()
            else:
                
                
        else:
            runR(On.L.Distance, On.R.Distance, On.F.Distance)
        On.b.wait()

    #Turn when destination reach, if corner is destination skip this step
    if cornerCheck(dest) == False:
        if isAscending():
            motor.turn_left()
        else:
            motor.turn_right()
        
    #Delivering to door
    while True:
        On.b.wait()
        if On.F.Distance>36:
            if cur == 7 or cur == 14:
                runNoWallL()
            elif cur == 1 or cur == 8:
                runNoWallR()
            else:
                motor.robot_forward()
        else:
            break
        On.b.wait()
        

    On.b.wait()
    On.On.Distance = 0;
    On.b.wait()

    motor.robot_stop()
    motor.knock()
    print('***PUSH***')
    while GPIO.input(motor.SW) != True:
        pass
    turn_back()
    robot_stop()
    cornerFlag = False
    
def auto():
    global cur
    global videoFlag
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
    while videoFlag == false:
        print('Waiting for VideoSignal...')
        time.sleep(0.2)
        pass
    p_vid.start()
    p_print.start()
   
    while(cur!=dest):
        qprint.put(cur)
        time.sleep(0.1)

        if qvideo.empty() == false:
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
    p_vid.join()
    p_control.join()
    p_print.join()

'''
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
    flag = False;
    
    print('***PUSH***')
    while GPIO.input(motor.SW) != True:
        pass
    turn_back()
    robot_stop()
'''            
    
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
