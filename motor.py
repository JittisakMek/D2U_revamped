import RPi.GPIO as GPIO
import time

#Set speed from 0-100
M1_SPEED = 55
M2_SPEED = 50
#Delay time.sleep() in seconds
DT_LEFT = 0.50
DT_RIGHT = 0.5
#M1 = right motor
M1_A = 31
M1_B = 33
M1_PWMPIN = 29
M1_DUTY = 100

#M2 = left motor
M2_A = 35
M2_B = 37
M2_PWMPIN = 40
M2_DUTY = 100

#SERVO and LED pin
SERVO_KNOCK_PIN = 22
SERVO_KNOCK_DUTY = 50

#SERVO camera
SERVO_CAM_PIN = 5
SERVO_CAM_DUTY = 50

#SWITCH
SW = 36

#initialised PINS
GPIO.setmode(GPIO.BOARD)
#MOTOR INIT
GPIO.setup(M1_A,GPIO.OUT)
GPIO.setup(M1_B,GPIO.OUT)
GPIO.setup(M1_PWMPIN,GPIO.OUT)
GPIO.setup(M2_A,GPIO.OUT)
GPIO.setup(M2_B,GPIO.OUT)
GPIO.setup(M2_PWMPIN,GPIO.OUT)
GPIO.setup(SERVO_KNOCK_PIN,GPIO.OUT)
GPIO.setup(SERVO_CAM_PIN,GPIO.OUT)
#PWM INIT
M1_P = GPIO.PWM(M1_PWMPIN,M1_DUTY)
M2_P = GPIO.PWM(M2_PWMPIN,M2_DUTY)
SERVO_KNOCK_P = GPIO.PWM(SERVO_KNOCK_PIN,SERVO_KNOCK_DUTY)
SERVO_CAM_P = GPIO.PWM(SERVO_CAM_PIN,SERVO_CAM_DUTY)

#SW INIT
GPIO.setup(SW,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

# set M1
def setMotorPinM1(A,B):
    M1_A = A
    M1_B = B
    
def setM2PWMPIN(pin):
    M2_PWMPIN = pin

def setM1DUTY(duty):
    M1_DUTY = duty

def setMotorSpeedM1(spd):
    M1_SPEED = spd


# set M2

def setMotorPinM2(A,B):
    M2_A = A
    M2_B = B

def setM1PWMPIN(pin):
    M1_PWMPIN = pin 

def setM2DUTY(duty):
    M2_DUTY = duty
    
def setMotorSpeedM2(spd):
    M2_SPEED = spd


    
#Set Knock
    
def setKnockPWMPIN(pin):
    SERVO_KNOCK= pin

def setKnockDUTY(duty):
    SERVO_KNOCK_DUTY = duty

    
#Set Camera 

def setCamPWMPIN(pin):
    SERVO_CAM = pin

def setCamDUTY(duty):
    SERVO_CAM_DUTY = duty


#Set Delays

def setDelayR(delay):
    DT_RIGHT = delay

def setDelayL(delay):
    DT_LEFT = delay

#START

def startM1():
    M1_P.start(0)

def startM2():
    M2_P.start(0)

def startKNOCK():
    SERVO_KNOCK_P.start(7)

def startCAM():
    SERVO_CAM_P.start(0)

#STOP

def stopM1():
    M1_P.stop()

def stopM2():
    M2_P.stop()

def stopKNOCK():
    SERVO_KNOCK_P.stop()

def stopCAM():
    SERVO_CAM_P.stop()

    
#Moving Motor

def M1_reverse(x):
    GPIO.output(M1_A, True)
    GPIO.output(M1_B, False)
    M1_P.ChangeDutyCycle(x)

def M1_forward(x):

    GPIO.output(M1_A, False)
    GPIO.output(M1_B, True)
    M1_P.ChangeDutyCycle(x)

def M1_stop():
    GPIO.output(M1_A, False)
    GPIO.output(M1_B, False)
    M1_P.ChangeDutyCycle(0)

def M2_reverse(y):
    GPIO.output(M2_A, True)
    GPIO.output(M2_B, False)
    M2_P.ChangeDutyCycle(y)

def M2_forward(y):
    GPIO.output(M2_A, False)
    GPIO.output(M2_B, True)
    M2_P.ChangeDutyCycle(y)

def M2_stop():
    GPIO.output(M2_A, False)
    GPIO.output(M2_B, False)
    M2_P.ChangeDutyCycle(0)

# Movements

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
    
#Servo functinos
def camLeft():
    SERVO_CAM_P.ChangeDutyCycle(3)
    time.sleep(1)
    
def camRight():
    SERVO_CAM_P.ChangeDutyCycle(11)
    time.sleep(1)
    
def knock():
    SERVO_KNOCK_P.ChangeDutyCycle(10)
    time.sleep(3)
    SERVO_KNOCK_P.ChangeDutyCycle(7)
def QuickStart():
    startKNOCK()
    startM1()
    startM2()
    startCAM()
def QuickStop():
    stopM1()
    stopM2()
    stopCAM()
    stopKNOCK()

def testMov():
    QuickStart()
    time.sleep(2)
    robot_forward()
    time.sleep(2)
    turn_right()
    time.sleep(2)
    turn_left()
    time.sleep(2)
    robot_reverse()
    time.sleep(2)
    knock()
    QuickStop()
    GPIO.cleanup()


    
