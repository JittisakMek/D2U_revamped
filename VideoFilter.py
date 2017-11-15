# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
from multiprocessing import Process, Queue

door_upper = 10000
door_lower = 1000

def setUpperThreshold(thresh):
        global door_upper
        door_upper = thresh

def setLowerThreshold(thresh):
        global door_lower
        door_lower = thresh

def displayFrame(image):
        cv2.imshow("Frame", image) 

def imageSave(image):
        cv2.imwrite('/home/pi/Desktop/D2U-master/images/image{0:04d}.jpg'.format(i),image)

def outputText(pixel, nodeCount, i):
        with open("Output.txt",'a') as myFile:
                myOut= "White Pixel: "+str(pixel)+"  From Video: "+ str(nodeCount)
                count = "\n---------------------------------Iteration: "+str(i)+"---------------------------------"
                myFile.write(count)
                myFile.write(myOut)
                                
def videoFilter(qvideo,qauto):
        print("starting Video....")
        i = 0 #For iteration in text Output
        flag = False #Ensures that one door is not counted twice
        flag2 = False #Ensures that first door is not counted

        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 2
        
        # converted to use with openCV funciton
        rawCapture = PiRGBArray(camera, size=(640, 480)) 

        # allow the camera to warmup
        time.sleep(0.1)
        # capture frames from the camera
        try:
                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                        #start_time = time.time()
                        # grab the raw NumPy array representing the image, then initialize the timestamp
                        # and occupied/unoccupied text
                        image = frame.array #numpy array for matlab 

                        #Hue [0-179], Saturation [0,255], Light [0,255]
                        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                        lower_green = np.array([50,50,50])
                        upper_green = np.array([70,255,255])
                        #Image Filter
                        mask = cv2.inRange(hsv, lower_green, upper_green)
                        result = cv2.bitwise_and(image, image, mask = mask)
                        #Image Enhancement
                        blur = cv2.medianBlur(mask, 15)
                        
                        #count white pixel
                        pixel = cv2.countNonZero(mask)
                        
                        #DoorCount
                        if flag2 == False and pixel<door_lower:
                            flag2 = True
                                
                        if flag == False and flag2 == True and pixel>=door_upper:
                            print('Node Detected')
                            qvideo.put(1)
                            flag = True
                                
                        elif flag == True and pixel<door_lower: #distance b/w two rooms very close so need door_lower
                            flag = False

                        if qauto.empty() == False:
                            print('Exiting Video....')
                            break

                        i += 1
                        outputText(pixel, nodeCount, i)
                        
                        # clear the stream in preparation for the next frame
                        rawCapture.truncate(0)
                        time.sleep(0.1)
        except:
                
                print('no frame')
        print('VIDEO FINISHED')

            
                        
                        #print('time = ', time.time()-start_time)
                        #print(time.ctime(time.time()) ) 
                        #b.wait()
