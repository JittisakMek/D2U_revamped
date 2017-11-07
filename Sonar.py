import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Queue
from threading import Barrier
TRIG_LEFT = 11
ECHO_LEFT = 12

TRIG_FRONT = 13
ECHO_FRONT = 18

TRIG_RIGHT = 15
ECHO_RIGHT = 16

TRIG_RIGHT2 = 7
ECHO_RIGHT2 = 23

class SoNarBack:
    Distance = 0.0
    def __init__(self):
        self.Distance = 0.0
       
class SoNarUse:

    def __init__(self):
        
        self.R = SoNarBack()
        self.F = SoNarBack()
        self.L = SoNarBack()
        self.On = SoNarBack()
        self.On.Distance = 10
        self.b = Barrier(4, timeout=10)

def ultraSetFrontPin(trig,echo):

    TRIG_FRONT = front
    ECHO_FRONT = front2
    
def ultraSetLeftPin(trig,echo):

    TRIG_LEFT = left
    ECHO_LEFT = left2

def ultraSetRightPin(trig,echo):

    TRIG_RIGHT = right
    ECHO_RIGHT = right2

def ultraInit():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG_LEFT,GPIO.OUT)                  #Set pin as GPIO out
    GPIO.setup(ECHO_LEFT,GPIO.IN)                   #Set pin as GPIO in
    GPIO.setup(TRIG_FRONT,GPIO.OUT)                  
    GPIO.setup(ECHO_FRONT,GPIO.IN)
    GPIO.setup(TRIG_RIGHT,GPIO.OUT)                  
    GPIO.setup(ECHO_RIGHT,GPIO.IN)
    GPIO.setup(TRIG_RIGHT2,GPIO.OUT)                  
    GPIO.setup(ECHO_RIGHT2,GPIO.IN)


def getDistance(TRIG, ECHO):

    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)

    while GPIO.input(ECHO)==0:              
        pass
    pulse_start = time.time()                 

    while GPIO.input(ECHO)==1:                
        pass
    pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    
    distance = pulse_duration * 17150        
    distance = round(distance, 2)

    if distance == 0:
        distance = 9999
        
   
    return distance

def getLeft():
    return getDistance(TRIG_LEFT,ECHO_LEFT)
def getRight():
    return getDistance(TRIG_RIGHT,ECHO_RIGHT)
def getFront():
    return getDistance(TRIG_FRONT,ECHO_FRONT)


                
def SoNarRight(s,b,on):
    
    while True:
        if(on.Distance>0):
            s.Distance = getRight()
            try:
                b.wait()
                b.wait()
                
            except:
                print('Broken Barrier')
        

def SoNarFront(s,b,on):
    while True:
        if(on.Distance>0):
            s.Distance = getFront()
            try:
                b.wait()
                b.wait()
                
            except:
                print('Broken Barrier')
        else:
            break
        
            
def SoNarLeft(s,b,on):
    while True:
        if(on.Distance>0):
            s.Distance = getLeft()
            try:
                b.wait()
                b.wait()
                
            except:
                print('Broken Barrier')
        else:
            break
        
                
            
         
    

    
 
        
   
    

    

