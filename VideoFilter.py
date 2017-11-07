# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import queue

def videoFilter(nodeDistance, q):
        #Specify no. of white pixel for one door        
        door_upper = 10000
        door_lower = 1000
        nodeCount = 0
        nodeCountN = 0
        i = 0
        flag = False
        flag2 = False
        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 2
        rawCapture = PiRGBArray(camera, size=(640, 480)) # converted to use with openCV funciton

        # allow the camera to warmup
        time.sleep(0.1)
        # capture frames from the camera
        try:
                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                        #start_time = time.time()
                        # grab the raw NumPy array representing the image, then initialize the timestamp
                        # and occupied/unoccupied text
                        image = frame.array #numpy array for matlab sht

                        #Hue [0-179], Saturation [0,255], Light [0,255]
                        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                        lower_green = np.array([50,50,50])
                        upper_green = np.array([70,255,255])
                        
                        mask = cv2.inRange(hsv, lower_green, upper_green)
                        result = cv2.bitwise_and(image, image, mask = mask)

                        blur = cv2.medianBlur(mask, 15)
                        
                        #count white pixel
                        pixel = cv2.countNonZero(mask)
                        #print("White pixel: ", pixel)
                        
                        #DoorCount
                        if flag2==False and pixel<door_lower:
                                flag2 = True
                        if flag == False and pixel>=door_upper and flag2==True:
                                nodeCountN = nodeCount
                                nodeCount = nodeCount + 1                                
                                print('Video: ',nodeCount,' ', nodeDistance)
                                flag = True
                                
                        elif flag == True and pixel<door_lower: #distance b/w two rooms very close so need door_lower
                                flag = False
                                
                        #No need to q.put() everytime
                        if nodeCountN != nodeCount:
                                nodeCountN = nodeCount
                                q.put(1)
                                
                        if nodeCount == nodeDistance:
                                break
                        #Display filtered Video frame
                        #cv2.imshow("Frame", image) #return 1 if inRange
                        cv2.imshow("blur", blur)
                        #cv2.imwrite('/home/pi/Desktop/images/image{0:04d}.jpg'.format(i),image)
                        #cv2.imwrite('/home/pi/Desktop/blur/blur{0:04d}.jpeg'.format(i),blur)
                        i += 1
                        #print('iteration: ',i)
                        #key = cv2.waitKey(1) & 0xFF
                        with open("Output.txt",'a') as myFile:
                                myOut= "White Pixel: "+str(pixel)+"  From Video: "+ str(nodeCount)
                                count = "\n---------------------------------Iteration: "+str(i)+"---------------------------------"
                                myFile.write(count)
                                myFile.write(myOut)
                        # clear the stream in preparation for the next frame
                        rawCapture.truncate(0)
        except:
                print('no frame')
        print('VIDEO FINISHED')
                        
                        
                        #print('time = ', time.time()-start_time)
                        #print(time.ctime(time.time()) ) 
                        #b.wait()
