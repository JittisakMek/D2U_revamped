from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import numpy as np
import cv2
import VideoFilter
import ReadUltra
import myFirebase
from multiprocessing import Process, Queue

#Set speed from 0-100
M1_SPEED = 55
M2_SPEED = 50
#Delay time.sleep() in seconds
DT_LEFT = 0.50
DT_RIGHT = 0.5
#M1 = right motor
M1_A = 31
M1_B = 33
M1_PWM = 29
#M2 = left motor
M2_A = 35
M2_B = 37
M2_PWM = 40
#Ultrasonic pins
TRIG_LEFT = 11
ECHO_LEFT = 12

TRIG_FRONT = 13
ECHO_FRONT = 18

TRIG_RIGHT = 15
ECHO_RIGHT = 16

TRIG_RIGHT2 = 7
ECHO_RIGHT2 = 23

#SERVO and LED pin
SERVO = 22
#SERVO camera
SERVO_CAM = 5
#SWITCH
SW = 36

#initialised PINS
GPIO.setmode(GPIO.BOARD)
#motor INIT
GPIO.setup(M1_A,GPIO.OUT)
GPIO.setup(M1_B,GPIO.OUT)
GPIO.setup(M1_PWM,GPIO.OUT)
GPIO.setup(M2_A,GPIO.OUT)
GPIO.setup(M2_B,GPIO.OUT)
GPIO.setup(M2_PWM,GPIO.OUT)
#ultrasonic INIT
GPIO.setup(TRIG_LEFT,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO_LEFT,GPIO.IN)                   #Set pin as GPIO in
GPIO.setup(TRIG_FRONT,GPIO.OUT)                  
GPIO.setup(ECHO_FRONT,GPIO.IN)
GPIO.setup(TRIG_RIGHT,GPIO.OUT)                  
GPIO.setup(ECHO_RIGHT,GPIO.IN)
GPIO.setup(TRIG_RIGHT2,GPIO.OUT)                  
GPIO.setup(ECHO_RIGHT2,GPIO.IN)
#SERVO INIT
GPIO.setup(SERVO,GPIO.OUT)
GPIO.setup(SERVO_CAM,GPIO.OUT)
#SW INIT
GPIO.setup(SW,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#set up pwm to motor
p_servo = GPIO.PWM(SERVO,50)
p_servoCam = GPIO.PWM(SERVO_CAM, 50)
p = GPIO.PWM(M1_PWM,100)
p2 = GPIO.PWM(M2_PWM,100)
#pwm START
p_servo.start(7)
p_servoCam.start(0)
p.start(0)
p2.start(0)

#robot functions
def turn_left():
    M1_forward(M1_SPEED)
    M2_reverse(M2_SPEED)
    time.sleep(DT_LEFT)
    M1_stop()
    M2_stop()

def turn_right():
    M1_reverse(M1_SPEED)
    M2_forward(M2_SPEED)
    time.sleep(DT_RIGHT)
    M1_stop()
    M2_stop()

def turn_back():
    M1_reverse(M1_SPEED)
    M2_forward(M2_SPEED)
    time.sleep(DT_RIGHT*1.9)
    M1_stop()
    M2_stop()

def robot_stop():
    M1_stop()
    M2_stop()

def robot_forward():
    M1_forward(M1_SPEED)
    M2_forward(M2_SPEED)
    
def robot_reverse():
    M1_reverse(M1_SPEED)
    M2_reverse(M2_SPEED)

def robot_rightforward(x):
  M1_forward(M1_SPEED-x);
  M2_forward(M2_SPEED);

def robot_leftforward(x): 
  M1_forward(M1_SPEED);
  M2_forward(M2_SPEED-x);

    
#Motor functions
        
def M1_reverse(x):
    GPIO.output(M1_A, True)
    GPIO.output(M1_B, False)
    p.ChangeDutyCycle(x)

def M1_forward(x):
    GPIO.output(M1_A, False)
    GPIO.output(M1_B, True)
    p.ChangeDutyCycle(x)

def M1_stop():
    GPIO.output(M1_A, False)
    GPIO.output(M1_B, False)
    p.ChangeDutyCycle(0)

def M2_reverse(y):
    GPIO.output(M2_A, True)
    GPIO.output(M2_B, False)
    p2.ChangeDutyCycle(y)

def M2_forward(y):
    GPIO.output(M2_A, False)
    GPIO.output(M2_B, True)
    p2.ChangeDutyCycle(y)

def M2_stop():
    GPIO.output(M2_A, False)
    GPIO.output(M2_B, False)
    p2.ChangeDutyCycle(0)

#Servo functinos
def camLeft():
    p_servoCam.ChangeDutyCycle(15)
    
def camRight():
    p_servoCam.ChangeDutyCycle(3)
    
def knock():
    p_servo.ChangeDutyCycle(10)
    time.sleep(3)
    p_servo.ChangeDutyCycle(7)
    
#Ultrasonic function
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

def crossCheck(source, destination):
    if source <= 7 and destination > 7:
        cross = True
    elif source >= 8 and destination < 8 :
        cross = True
    else:
        cross = False
        
    return cross

def decision(source):
    #location
    #0 = left
    #1 = right
    if source <= 7:
        location = 0
    elif source > 7:
        location = 1

    return location

def nodeOrder(nodeDistance):
    if nodeDistance > 0:
        ascending = True
    else:
        ascending = False

    return ascending

#SPECIAL CONDITION FOR CORNERS
def cornerCheck(source, destination):
    if source == 1 or source == 7 or source == 8 or source == 14:
        corner = True

    elif destination == 1 or destination == 7 or destination == 8 or destination == 14:
        corner = True

    else:
        corner = False

    return corner

def shortestPath(source, destination, nodeDistance):
    #0 = cross back
    #1 = cross front
    if nodeDistance <= 7:
        cross = 0
    elif nodeDistance < 7:
        cross = 1
    return cross
    
def wallR(nodeDistance,q):
    turn_left()
    camLeft()
    ReadUltra.runR(nodeDistance,q,0)

def wallL(nodeDistance,q):
    turn_right()
    camRight()
    ReadUltra.runL(nodeDistance,q,0)  
    
def delivery(source, destination , nodeDistance, q):
    left = 0
    right = 1

    location = decision(source)
    ascending = nodeOrder(nodeDistance)
    corner = cornerCheck(source, destination)
    cross = crossCheck(source, destination)
    
    if nodeDistance == 0:
        print('No destination to deliver')
    else:
        if cross:
            if location == left:
                
            elif location == right:
                
                

#Main Delivery function!!!!
def delivery(source, destination, nodeDistance, q):
    #START: robot should face wall   
    #Case LEFT side
    if nodeDistance != 0:
        #LEFT SIDE
        if source <= 7 and destination <= 7:
                
            if nodeDistance > 0: #lower to higher node
                turn_left()
                camLeft()
                if source==1:
                    if destination==2:
                        ReadUltra.runToWallR()
                        #print('Wall Reached 2') 
                        ReadUltra.runR(nodeDistance,q,0)
                    elif destination==7:
                        ReadUltra.runToWallR()
                        print("Finished runToWall")
                        ReadUltra.runR(nodeDistance-2,q,1)
                        print("Finished runR")
                        ReadUltra.runL(1,q,2)
                    else:
                        ReadUltra.runToWallR()
                        ReadUltra.runR(nodeDistance-1,q,0)
                elif destination==7:
                    ReadUltra.runR(nodeDistance-1,q,1)
                    ReadUltra.runL(1,q,2)
                else:
                    ReadUltra.runR(nodeDistance,q,0)
                        
                
            else:   #higher to lower
                turn_right()
                camRight()
                #Start at 7
                if source==7:
                    if destination==6:
                        ReadUltra.runToWallL()
                        ReadUltra.runL(nodeDistance,q,0)
                    elif destination==1:
                        ReadUltra.runToWallL()
                        print("Finished runToWallL")
                        ReadUltra.runL(abs(nodeDistance)-2,q,1)
                        print("Finished runL")
                        ReadUltra.runR(1,q,0)
                    else:
                        ReadUltra.runToWallL(1,q,1)
                        ReadUltra.runL(nodeDistance-1,q,0)
                #End at 1
                elif destination==1:
                    ReadUltra.runL(abs(nodeDistance)-1,q,1)
                    ReadUltra.runR(1,q,2)
                else:
                    ReadUltra.runL(abs(nodeDistance),q,0)
            
        #CROSS        
        elif source <= 7 and destination > 7:
        #cross left to right follow right wall
            t=1
            if nodeDistance <= 7: #Cross at the back
                if source == 7:
                    ReadUltra.crossB(source,destination)
                    ReadUltra.runToWallR()
                    ReadUltra.runR(abs(nodeDistance)-1,q,0) 
                else:
                    turn_left()
                    ReadUltra.runR(abs(source-6),q,t)
                    ReadUltra.runL(1,q,t)
                    ReadUltra.crossB(source,destination)
                    ReadUltra.runR(destination-8,q,0)
                
                '''if destination == 8:
                    pass
                else:
                    turn_right()
                    runR(abs(8-destination),q,t)'''
            elif nodeDistance > 7: # Cross at front
                if source == 1:
                    crossF(source,destination)
                else:
                    turn_right()
                    run(14-destination,q)
                    crossF(source,destination)

        #CROSS        
        elif source >= 8 and destination < 8 :
        #cross left to right follow right wall
            t=1
            if nodeDistance <= 7: #Cross at the back
                if source == 7:
                    ReadUltra.crossB(source,destination)
                    ReadUltra.runL(abs(nodeDistance)-1,q,0)
                else:
                    turn_left()
                    ReadUltra.runR(abs(source-6),q,t)
                    ReadUltra.runL(1,q,t)
                    ReadUltra.crossB(source,destination)
                    ReadUltra.runR(destination-8,q,0)
                
                '''if destination == 8:
                    pass
                else:
                    turn_right()
                    runR(abs(8-destination),q,t)'''
            elif nodeDistance > 7: # Cross at front
                if source == 1:
                    crossF(source,destination)
                else:
                    turn_right()
                    run(14-destination,q)
                    crossF(source,destination)
                    
        #RIGHT SIDE            
        elif source>7 and destination>7:
            if nodeDistance>0: #lower to higher node
                turn_right()
                camRight()
                if source==14:
                    if destination==13:
                        ReadUltra.runToWallL()
                        print("Finished runToWall")
                        ReadUltra.runL(nodeDistance,q,0)
                    elif destination==8:
                        ReadUltra.runToWallL()
                        print("Finished runToWall")
                        ReadUltra.runL(nodeDistance-2,q,1)
                        print("Finished runR")
                        ReadUltra.runR(1,q,2)
                    else:
                        ReadUltra.runToWallL()
                        ReadUltra.runL(nodeDistance-1,q,0)
                elif destination==8:
                    ReadUltra.runL(nodeDistance-1,q,1)
                    ReadUltra.runR(1,q,2)
                else:
                    ReadUltra.runL(nodeDistance,q,0)
                
            else:                #higher to lower
                turn_left()
                camLeft()
                #Start at 8
                if source==8:
                    if destination==9:
                        ReadUltra.runToWallR()
                        print("Finished runToWall")
                        ReadUltra.runR(nodeDistance,q,0)
                    elif destination==14:
                        ReadUltra.runToWallR()
                        print("Finished runToWall")
                        ReadUltra.runR(abs(nodeDistance)-2,q,1)
                        print("Finished runR")
                        ReadUltra.runL(1,q,2)
                    else:
                        ReadUltra.runToWallR()
                        ReadUltra.runR(nodeDistance-1,q,0)
                #End at 14
                elif destination==14:
                    ReadUltra.runR(abs(nodeDistance)-1,q,1)
                    ReadUltra.runL(1,q,2)
                else:
                    ReadUltra.runR(abs(nodeDistance),q,0)
    else:
        print('No destination to deliver')
    
        
def auto():
    #temp = input('press to start')
    src = input('Input current position:')
    dest = input('Input destination position:')
    nodeDistance = int(dest)-int(src)
    q = Queue()

    p_vid = Process(target = VideoFilter.videoFilter, args = (abs(nodeDistance),q))
    p_vid.start()
    delivery(int(src),int(dest),nodeDistance,q)
    p_vid.join()
    
def main():
    try:
        myFirebase.readData()
        while True:
            auto()
            #Robot finish delivery
            print('***PUSH***')
            while GPIO.input(SW) != True:
                pass
            turn_back()
            robot_stop()
            
            ans = input('Continue [C] | Quit[Q]: ')
            if ans.lower() == 'q':
                break
            
        p_servo.stop()
        p_servoCam.stop()
        p.stop()
        p2.stop()
        GPIO.cleanup()

    except KeyboardInterrupt:
        p_servo.stop()
        p_servoCam.stop()
        p.stop()
        p2.stop()
        GPIO.cleanup()
        
if __name__ == "__main__":
    main()
        





