import D2U
import threading
from threading import Barrier
import time

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
        self.b = Barrier(4, timeout=5)

def GetFrontSoNar(n,b,On):

    while(On.Distance>0):
   
        n.Distance = D2U.getDistance(D2U.TRIG_FRONT,D2U.ECHO_FRONT)
        #print("main 1 wait \n")
        try:
            b.wait()
        except:
            print('Error broken barrier F')

def GetLeftSoNar(n,b,On):

    while(On.Distance>0):
        n.Distance = D2U.getDistance(D2U.TRIG_LEFT,D2U.ECHO_LEFT)
        #print("main 2 wait \n")
        try:
            b.wait()
        except:
            print('Error broken barrier L')

def GetRightSoNar(n,b,On):
    while(On.Distance>0):
        n.Distance = D2U.getDistance(D2U.TRIG_RIGHT,D2U.ECHO_RIGHT);
        #print("main 2 wait \n")
        try:
            b.wait()
        except:
            print('Error broken barrier R')
                
def CollectDistance(S):
    On = SoNarBack() #turn on or off sonar
    On.Distance = 10 #turn on
    
    thread_Front = threading.Thread(target = GetFrontSoNar, args = (S.F,S.b,S.On))
    thread_Left = threading.Thread(target = GetLeftSoNar, args = (S.L,S.b,S.On))
    thread_Right = threading.Thread(target = GetRightSoNar, args = (S.R,S.b,S.On))
    
    thread_Front.start()
    thread_Left.start()
    thread_Right.start()
    
    thread_Front.join()
    thread_Left.join()
    thread_Right.join()
    
def runR(nodeDistance, q,t):
    
    if nodeDistance != 0:
        S = SoNarUse()
        thread_S = threading.Thread(target = CollectDistance, args = (S,))
        thread_S.start()
        nodeCount = 0
        while not q.empty():
            nodeCount = q.get()
            
        while nodeCount != nodeDistance:
            try:
                S.b.wait()
            except:
                print('Error broken barrier')
                           
            front = S.F.Distance
            left = S.L.Distance
            right = S.R.Distance
            #print('\n===================================================')
            #print("LEFT: ", left - 0.5, "cm", "\t", "FRONT: ", front - 0.5, "cm","\t", "RIGHT: ", right -0.5, 'cm')
            while not q.empty():
                nodeCount = q.get()
                print('Ultra: ',nodeCount)
                
            #********************************************  
            if nodeCount == nodeDistance:
                #t=1 no turn, just stop
                print('KNOCK')
                if t == 0:
                    D2U.robot_stop()
                    time.sleep(1)
                    D2U.turn_left()
                    while front>36:
                        try:
                            S.b.wait()
                        except:
                            print('Error broken barrier')
                        front = S.F.Distance
                        D2U.robot_forward()
                    D2U.robot_stop()
                    time.sleep(0.2)
                    D2U.robot_reverse()
                    time.sleep(0.1)
                    D2U.robot_stop()
                    D2U.knock()
                    break
                elif t==1:
                    D2U.robot_stop()
                    print('Reached a corner')
                    break
                else:
                    D2U.robot_stop()
                    time.sleep(1)
                    D2U.turn_right()
                    while front>36:
                        try:
                            S.b.wait()
                        except:
                            print('Error broken barrier')
                        front = S.F.Distance
                        D2U.robot_forward()
                    D2U.robot_stop()
                    D2U.knock()
                    break
            #*********************************************    
            if front>40:
                    if right<25:
                        if right < 5:
                            D2U.robot_leftforward(50)
                            
                        else:
                            D2U.robot_leftforward(30)
                            
                    elif left<30 or right>30:
                        if right > 40:
                            D2U.robot_rightforward(20)
                        else:
                            D2U.robot_rightforward(30)

                    else:
                        D2U.robot_forward()
                        
            elif right > 100:
                D2U.robot_forward()
                
            else:
                D2U.robot_stop()
            
    print("Destination reached")
    S.On.Distance = 0    
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join()

def runL(nodeDistance,q,t):
    if nodeDistance != 0:
        S = SoNarUse()
        thread_S = threading.Thread(target = CollectDistance, args = (S,))
        thread_S.start()
        nodeCount = 0
        while not q.empty():
            nodeCount = q.get()
            
        while nodeCount != nodeDistance:
            try:
                S.b.wait()
            except:
                print('Error broken barrier')

            front = S.F.Distance
            left = S.L.Distance
            right = S.R.Distance

            while not q.empty():
                nodeCount = q.get()
                print('Ultra: ',nodeCount)
            #********************************************
            if nodeCount == nodeDistance:
                if t == 0:
                    D2U.robot_stop()
                    time.sleep(1)
                    D2U.turn_right()
                    while front>36:
                        try:
                            S.b.wait()
                        except:
                            print('Error broken barrier')
                        front = S.F.Distance
                        D2U.robot_forward()
                    D2U.robot_stop()
                    D2U.knock()
                    break
                elif t==1:
                    D2U.robot_stop()
                    print('Reached a corner')
                    break
                else:
                    D2U.robot_stop()
                    time.sleep(1)
                    D2U.turn_left()
                    while front>36:
                        try:
                            S.b.wait()
                        except:
                            print('Error broken barrier')
                        front = S.F.Distance
                        D2U.robot_forward()
                    D2U.robot_stop()
                    D2U.knock()
                    break
             #********************************************   
            if front>40:
                if left<25:
                    if left < 5:
                        D2U.robot_rightforward(50)
                        
                    else:
                        D2U.robot_rightforward(30)
                        
                elif right<30 or left>30:
                    if left > 40:
                        D2U.robot_leftforward(20)
                    else:
                        D2U.robot_leftforward(30)
                else:
                    D2U.robot_forward()
                    #print('robot_forward')
            elif left > 100:
                D2U.robot_forward()
                #print('turn_left')
            else:
                D2U.robot_stop()
                #print('robot_stop')
         
    print("Destination reached")
    S.On.Distance = 0    
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join()
    
def runToWallR():
    S = SoNarUse()
    thread_S = threading.Thread(target = CollectDistance, args = (S,))
    thread_S.start()

    try:
        S.b.wait()
    except:
        print('Error broken barrier')
        
    front = S.F.Distance
    left = S.L.Distance
    right = S.R.Distance

    while right>100:
        try:
            S.b.wait()
        except:
            print('Error broken barrier')

        front = S.F.Distance
        left = S.L.Distance
        right = S.R.Distance
        
        if front>40:
            if left<30:
                if left < 5:
                    D2U.robot_rightforward(50)
                    
                else:
                    D2U.robot_rightforward(30)
                    
            elif right<30 or left>40:
                if left > 50:
                    D2U.robot_leftforward(20)
                else:
                    D2U.robot_leftforward(30)
            else:
                D2U.robot_forward()
                #print('robot_forward')
        elif left > 100:
            D2U.turn_left()
        #print('turn_left')
        else:
            D2U.robot_stop()
        #print('robot_stop')
             
    print("Wall reached")
    S.On.Distance = 0    
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join()

def runToWallL():
    S = SoNarUse()
    thread_S = threading.Thread(target = CollectDistance, args = (S,))
    thread_S.start()

    try:
        S.b.wait()
    except:
        print('Error broken barrier')
        
    front = S.F.Distance
    left = S.L.Distance
    right = S.R.Distance

    while left>100:
        try:
            S.b.wait()
        except:
            print('Error broken barrier')

        front = S.F.Distance
        left = S.L.Distance
        right = S.R.Distance
        
        if front>40:
            if right<30:
                if right < 5:
                    D2U.robot_leftforward(50)
                    
                else:
                    D2U.robot_leftforward(30)
                    
            elif left<30 or right>40:
                if left > 50:
                    D2U.robot_rightforward(20)
                else:
                    D2U.robot_rightforward(30)
            else:
                D2U.robot_forward()
                #print('robot_forward')
        elif left > 100:
            D2U.turn_left()
        #print('turn_left')
        else:
            D2U.robot_stop()
        #print('robot_stop')
             
    print("Wall reached")
    S.On.Distance = 0    
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join()
    
def crossF(source,destination):
    #cross between sides at the front
    if source == 14: #Whatever is the last door here
        #cuz if it starts from last door no turning needed
        runNoWallR()
        if destination == 1:
            runNoWallR()  #Just charge right at the door
    elif source == 1:
        runNoWallL()
        if destination == 14:
            runNoWallL()  #Just charge right at the door
    elif source >= 8:
        turn_right()
        runNowallR()
    else:
        turn_left()
        runNoWallL()

def crossB(source,destination):
    #cross between sides at the back 
    if source == 7: #Whatever is the last door here
        if destination == 8:
            runNoWallR(1)  #Just charge right at the door
        else:
            runNoWallR(0)
    elif source == 8:
        if destination == 7:
            runNoWallL(1)  
        else:
            runNoWallL(0)      
    elif source >= 8:
        turn_left()
        runNowallL()
    else:
        turn_right()
        if destination == 8:
            runNoWallR(1)  
        else:
            runNoWallR(0) 

def runNoWallR(DOOR):
    S = SoNarUse()
    thread_S = threading.Thread(target = CollectDistance, args = (S,))
    thread_S.start()
        
    while front>40:
        try:
            S.b.wait()
        except:
            print('Error broken barrier')
                              
        front = S.F.Distance
        left = S.L.Distance
        right = S.R.Distance
        
        if right>100:
            robot_forward()
            
        elif right<20:
            
            if right < 5:
                D2U.robot_leftforward(50)
                
            else:
                robot_leftforward(30)
                        
        elif left<30 or right>30:
            D2U.robot_rightforward(30)
                    
        else:
            D2U.robot_forward()

    if DOOR == 1:
        D2U.knock()
    else:
        D2U.robot_stop()
        D2U.turn_back()
    print("RunNowall reached")
    
    S.On.Distance = 0
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join()

def runNoWallL():
    S = SoNarUse()
    thread_S = threading.Thread(target = CollectDistance, args = (S,))
    thread_S.start()
        
    while front>40:
        try:
            S.b.wait()
        except:
            print('Error broken barrier')
                              
        front = S.F.Distance
        left = S.L.Distance
        right = S.R.Distance
        
        if left>100:
            robot_forward()
            
        elif left<20:
            
            if left < 5:
                D2U.robot_leftforward(50)
                
            else:
                robot_leftforward(30)
                        
        elif right<30 or left>30:
            D2U.robot_leftforward(30)
                    
        else:
            D2U.robot_forward()
            
    if DOOR == 1:
        D2U.knock()
    else:
        D2U.robot_stop()
        D2U.turn_back()
    print("RunNowall reached") 
  
    S.On.Distance = 0    
    try:
        S.b.wait()
    except:
        print('Error broken barrier')
    thread_S.join() 

    
