from firebase import firebase
import json

fb = firebase.FirebaseApplication('https://d2u2-68242.firebaseio.com/',None)

def readData():
    curQ = fb.get('/Queue/Current',None)
    inQ = fb.get('/Queue/InQueue',None)
    print(curQ)
    return int(curQ),int(inQ)

def updateQueue(curQ,inQ):
    updated = False
    if(curQ < inQ):
        newQ = str(int(curQ) +1 )
        fb.put('/Queue','Current',newQ)
        print("New Task detected \nCurrentQ updated with newQ = ",newQ)
        updated = True
    elif(curQ == inQ):
        print("All task has been completed")
    else:
        print("Fatal error with queue tracking System please recheck Database")
    return updated

def getTaskDetail(taskQ):
    data = {}
    allData = fb.get('UsageLog',None,params={"orderByChild":"QueueNumber"})
    for i in allData:
        if int(allData.get(i).get('QueueNumber')) == taskQ:
                data =  allData.get(i)
                #print(data)
    return data

def getScrDest(data):
    source = data.get('Source')
    destination = data.get('Destination')
    return source,destination
    
def markTaskDone(curQ):
    ref = 'UsageLog/'+key
    fb.put(ref,'Status',"Done")

#SAMPLE CALL ORDER
    
#[curQ,inQ] = readData()    
'''
if(updateQueue(curQ,inQ) == True):
    [source,destination] = getScrDest(getTaskDetail(curQ))
'''

#This was used to test
#[source,destination] = getScrDest(getTaskDetail(curQ))    
#print("Source: ",source,"\n","Destination: ",destination)
#data = getTaskDetail(curQ) 
#newTask(data,inQ)
#[data,key] = getTaskDetail(2)
#print(data,key)
#markTaskDone(key)

