#d_motion_matrix = [[0,0,0,0,0,0,0,0,0,0],
#                   [0,0,0,0,0,0,0,0,0,0],
#                   [0,0,0,0,0,0,0,0,0,0]] # currently 3 values kept for 10 frames
d_motion_matrix = [[0,0],
                   [0,0],
                   [0,0]] # currently 3 values kept for 2 frames
R = len(d_motion_matrix)
C = len(d_motion_matrix[0])

def get_max_motion(new_c,threshold):
    global d_motion_matrix, R, C
    # new_c is a single column of new data
    # a is the 2D array which holds a shifting window of difference values
    # if total motion is above threshold we have significant motion
    # otherwise no motion
    
    # this loop moves the data down by a single column
    for i in range(1,C):
        for r in range(R):
            d_motion_matrix[r][C-i] = d_motion_matrix[r][C-i-1]
    # this loop fills the first column with the new data
    for i in range(R):
        d_motion_matrix[i][0] = new_c[i]
    # max_motion_row will the row number which has the maximum motion
    max_motion_row = -1
    max_motion_value = -1
    for i in range(R):
        ith_motion_value = sum(d_motion_matrix[i][:])
        if (ith_motion_value > threshold) and (ith_motion_value > max_motion_value):
            max_motion_row = i
            max_motion_value = ith_motion_value
    # print matrix a row by row to see how it changes
    # this code maybe removed later
    # for i in range(R):
    #    print d_motion_matrix[i]
    # finally return the row where maximum motion was detected
    # -1 is returned if no motion is detected that is above threshold
    return max_motion_row

import csv
import re
from math import fabs
from pykinect import nui
from pykinect.nui import JointId
LEFT_ARM = (JointId.ShoulderCenter, 
            JointId.ShoulderLeft, 
            JointId.ElbowLeft, 
            JointId.WristLeft, 
            JointId.HandLeft)
RIGHT_ARM = (JointId.ShoulderCenter, 
             JointId.ShoulderRight, 
             JointId.ElbowRight, 
             JointId.WristRight, 
             JointId.HandRight)
LEFT_LEG = (JointId.HipCenter, 
            JointId.HipLeft, 
            JointId.KneeLeft, 
            JointId.AnkleLeft, 
            JointId.FootLeft)
RIGHT_LEG = (JointId.HipCenter, 
             JointId.HipRight, 
             JointId.KneeRight, 
             JointId.AnkleRight, 
             JointId.FootRight)
SPINE = (JointId.HipCenter, 
         JointId.Spine, 
         JointId.ShoulderCenter, 
         JointId.Head)

prev_vals = [0,0,0]
curr_vals = [0,0,0]
Delay = {'HALF':15,'ONE':30,'ONE_AND_HALF':45,'TWO':60,'THREE':90,'TEN':300}
frameCounter = 0
frameToSample = Delay['THREE']
setNumber = 1
frameNumber = 1
initial = 1
numOfSets = input("Enter number of gestures: ")
subjectName = raw_input("Enter subject name: ")
distance = raw_input("Enter distance from Kinect: ")
gestureID = raw_input("Enter gestureID: ")

fileString = "C:\\tmp\\" + subjectName + "_" + distance + "_" + gestureID + ".csv"
outfile = open( fileString, "wb")
writer = csv.writer(outfile, delimiter=',')
gesturesBuffer = [] #holds sequence of gestures
frameBuffer = []


with nui.Runtime() as kinect:
    
    kinect.skeleton_engine.enabled = True
    
    while (setNumber <= numOfSets):

        frame = kinect.skeleton_engine.get_next_frame()
        
        for skeleton in frame.SkeletonData:
            
            if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
                #prev_vals = curr_vals
                
                if (frameCounter == frameToSample):
                    
                    if initial == 1:
                        initial = 0
                        print "\a" #beep
                    
                    if frameNumber <= Delay['TWO']:
                        #write data to list here.
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.Head].x, skeleton.SkeletonPositions[JointId.Head].y, skeleton.SkeletonPositions[JointId.Head].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.HandRight].x, skeleton.SkeletonPositions[JointId.HandRight].y, skeleton.SkeletonPositions[JointId.HandRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.HandLeft].x, skeleton.SkeletonPositions[JointId.HandLeft].y, skeleton.SkeletonPositions[JointId.HandLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.WristRight].x, skeleton.SkeletonPositions[JointId.WristRight].y, skeleton.SkeletonPositions[JointId.WristRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.WristLeft].x, skeleton.SkeletonPositions[JointId.WristLeft].y, skeleton.SkeletonPositions[JointId.WristLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.ElbowRight].x, skeleton.SkeletonPositions[JointId.ElbowRight].y, skeleton.SkeletonPositions[JointId.ElbowRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.ElbowLeft].x, skeleton.SkeletonPositions[JointId.ElbowLeft].y, skeleton.SkeletonPositions[JointId.ElbowLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.ShoulderRight].x, skeleton.SkeletonPositions[JointId.ShoulderRight].y, skeleton.SkeletonPositions[JointId.ShoulderRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.ShoulderCenter].x, skeleton.SkeletonPositions[JointId.ShoulderCenter].y, skeleton.SkeletonPositions[JointId.ShoulderCenter].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.ShoulderLeft].x, skeleton.SkeletonPositions[JointId.ShoulderLeft].y, skeleton.SkeletonPositions[JointId.ShoulderLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.HipRight].x, skeleton.SkeletonPositions[JointId.HipRight].y, skeleton.SkeletonPositions[JointId.HipRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.HipCenter].x, skeleton.SkeletonPositions[JointId.HipCenter].y, skeleton.SkeletonPositions[JointId.HipCenter].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.HipLeft].x, skeleton.SkeletonPositions[JointId.HipLeft].y, skeleton.SkeletonPositions[JointId.HipLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.KneeRight].x, skeleton.SkeletonPositions[JointId.KneeRight].y, skeleton.SkeletonPositions[JointId.KneeRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.KneeLeft].x, skeleton.SkeletonPositions[JointId.KneeLeft].y, skeleton.SkeletonPositions[JointId.KneeLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.AnkleRight].x, skeleton.SkeletonPositions[JointId.AnkleRight].y, skeleton.SkeletonPositions[JointId.AnkleRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.AnkleLeft].x, skeleton.SkeletonPositions[JointId.AnkleLeft].y, skeleton.SkeletonPositions[JointId.AnkleLeft].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.FootRight].x, skeleton.SkeletonPositions[JointId.FootRight].y, skeleton.SkeletonPositions[JointId.FootRight].z]
                        frameBuffer = frameBuffer + [skeleton.SkeletonPositions[JointId.FootLeft].x, skeleton.SkeletonPositions[JointId.FootLeft].y, skeleton.SkeletonPositions[JointId.FootLeft].z]
                                                                    
                        #increment frame to sample
                        frameToSample += 1
                        frameNumber += 1

                    else: # set captured
                        print "\a" #beep
                        print "\a"

                        frameToSample += Delay['THREE']
                        frameNumber = 1
                        setNumber += 1
                        initial = 1
                        gesturesBuffer.append(frameBuffer)  
                        frameBuffer = []
                            
        frameCounter = frameCounter + 1       
                
        #curr_vals = [skeleton.SkeletonPositions[JointId.Head].x, skeleton.SkeletonPositions[JointId.Head].y, skeleton.SkeletonPositions[JointId.Head].z]
        #print curr_vals
               # d_vals = [fabs(curr_vals[0]-prev_vals[0]),fabs(curr_vals[1]-prev_vals[1]),fabs(curr_vals[2]-prev_vals[2])]
                #id = get_max_motion(d_vals,0.01)
                #print d_vals
                #print skeleton.SkeletonPositions[JointId.Head].z
                #if id > 0:
                    #print "\a"
                #else:
                    #print "NO MOTION DETECTED"
                    #pass


# loop through gesturesBuffer
print "\a"
print "\a"
print "\a"

for frameSet in gesturesBuffer:
    writer.writerow(frameSet)

outfile.close()
                
