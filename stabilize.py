#!/usr/bin/python3
#
#
# Image Stabilization software for "La Gugusse 16mm"
#
# This software expects the following from the images before processing:
#
# A- The images should be already cropped for a 1:1 ratio
# B- The holes should be on the left and the soundtrack (if any) on the right
# C- the width of the image should be filled by the whole width of the film (not
#    just the image)
# D- The complete width of the film should be visible (image + holes + soundtrack if any)
# E- the holes should be visible and if anything is saturated on the image
#    then it should be the holes themselves, no surface of film should be saturated. In
#    other words: this will only work if the holes are lighter than any surface
#    of the film.
# F- There should be 2 holes on the left
# G- The images should already be leveled as this stabilization doesn't do any
#    rotation.
# 
#
# Author: Denis-Carl Robidoux, proud creator of La Gugusse 16mm
# 
#
########################################################################

# requires pillow library
from PIL import Image
import sys
import os
import wave



reference={
    #       width, height, xoffset, yoffset
    "hole": (10,10,10,10),
    "frame": (1624, 1200, 62, 36),
    #       width, height, xoffset, yoffset, numOfChannels
    "audio": (374, 1228, 1740, 24, 1),
}

def square(x):
    return x*x*x


class Channel:
    data=None
    def __init__(self, name):
        self.data=open(name+".txt", "w")        
    def readFrame(self, img):
        for y in range(0,img.size[1]):
            line=[]
            for x in range(0, img.size[0]):
                line.append(sum(img.getpixel((x,y))))
            threshold=int((min(line)+max(line))/2)
            value=0
            for i in line:
                if i > threshold:
                    value+=1
            self.data.write(str(value)+"\n")
    def close(self):
        self.data.close()
            

       

    

    

def edgeOf(line, direction, checkwidth):
    lowest=None
    highest=None
    #trace=[]
    for idx in range(checkwidth, len(line)-checkwidth):
        delta=0
        for i in range(1, checkwidth):
            diff=(square(line[idx-i]) - square(line[idx+i]))
            delta+=diff
        #trace.append((idx,delta))
        if lowest == None or (delta<lowest[1]):
            lowest=(idx, delta)
        if highest == None or (delta>highest[1]):
            highest=(idx, delta)
    #print (str(trace))
    if direction == "darkToLight":
        return lowest[0]
    if direction == "lightToDark":
        return highest[0]

def holeVerticalOffset(im, hoffs=0):
    width=im.size[0]
    height=im.size[1]
    
    # Let's figure out the top of the hole
    line=[]
    sampleBottom=min(height, reference['hole'][3] + 2 * reference['hole'][1])
    sampleTop=max(0, reference['hole'][3] - reference['hole'][1])
    midX=reference['hole'][2] + int(reference['hole'][0] / 2) + hoffs
    for y in range(sampleTop, sampleBottom):
        total=0
        for i in im.getpixel((midX, y)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(1.5 * reference['hole'][1])]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    topHole=edgeOf(line, "darkToLight",int(50*reference['hole'][1]/100))+sampleTop
    return topHole - reference['hole'][3]
def holeHorizontalOffset(im, voffs=0):
    width=im.size[0]
    height=im.size[1]
    
    # Let's figure out the top of the hole
    line=[]
    sampleRight=min(width, reference['hole'][2] + 2 * reference['hole'][0])
    sampleLeft=max(0, reference['hole'][2] - reference['hole'][0])
    midY=reference['hole'][3] + int(reference['hole'][1] / 2) + voffs
    for x in range(sampleLeft, sampleRight):
        total=0
        for i in im.getpixel((x, midY)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(1.25 * reference['hole'][0])]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    rightHole=edgeOf(line, "lightToDark",int(reference['hole'][0]/2))+sampleLeft
    return rightHole - (reference['hole'][2]+reference['hole'][0])
        

positions={}
numOfImages=0
totalTopHole=0
totalBottomHole=0
totalHoleRightEdge=0
totalHoleRightEdgeLower=0
pidx=1
extractAudio=True
mono=False
stabilizeX=True
stabilizeY=True


left=Channel("left")
right=Channel("right")
voffs=0
hoffs=0

while pidx < len(sys.argv):    
    if sys.argv[pidx] == '-nosound':
        extractAudio=False
    elif sys.argv[pidx] == '-noXoffset':
        stabilizeX=False
    elif sys.argv[pidx] == '-noYoffset':
        stabilizeY=False        
    elif sys.argv[pidx] == '-mono':
        mono=True
    else:
        try:
            im=Image.open(sys.argv[pidx])
            if stabilizeY:
                voffs=holeVerticalOffset(im)
            if stabilizeX:
                hoffs=holeHorizontalOffset(im, voffs)
            x1=reference['frame'][2]+hoffs
            x2=x1+reference['frame'][0]
            y1=reference['frame'][3]+voffs
            y2=y1+reference['frame'][1]
            print ("Stabilizing "+sys.argv[pidx]+", X="+str(hoffs)+", Y="+str(voffs))
            im.crop((x1,y1,x2,y2)).save("cropped/"+sys.argv[pidx])
            if extractAudio:
                x1=reference['audio'][2]+hoffs
                x3=x1+reference['audio'][0]
                y1=reference['audio'][3]+hoffs
                y3=y1+reference['audio'][1]                    
                if mono:
                    left.readFrame(im.crop((x1,y1,x3,y3)))
                else:
                    x2=int((x1+x3)/2)
                    left.readFrame(im.crop((x1,y1,x2,y3)))
                    right.readFrame(im.crop((x2,y1,x3,y3)))
                    
                
        except:
            print("EXCEPTION: Skipped "+ sys.argv[pidx])
            pass
    pidx+=1




#if extractAudio:
#    soundStartOffset=int(sample['Tracks_start']*sizeYOut/sample['frameHeight'])
#    soundMidOffset=int(sample['Tracks_mid']*sizeYOut/sample['frameHeight'])
#    soundEndOffset=int(sample['Tracks_end']*sizeYOut/sample['frameHeight'])
#    left=Channel()
#    if not mono:
#        right=Channel()

#for pic in sorted(positions):
#    im=Image.open(pic)
#    results=positions[pic]
#    topHole=results[0]
#    bottomHole=results[1]
#    holeRightEdge=results[2]
#    holeRightEdgeLower=results[3]
#    if abs(topHole-avgTopHole) < abs(bottomHole-avgBottomHole):
#        bottomHole=topHole+avgDeltaHole
#    else:
#        topHole=bottomHole-avgDeltaHole
#    if abs(holeRightEdge-avgHoleRightEdge) < abs(holeRightEdgeLower-avgHoleRightEdgeLower):
#        holeRightEdgeLower=avgHoleRightEdgeLower + holeRightEdge-avgHoleRightEdge
#    else:
#        holeRightEdge=avgHoleRightEdge+holeRightEdgeLower-avgHoleRightEdgeLower
#    x1=holeRightEdge+scaledXOffset
#    y1=topHole+scaledYOffset
#    x2=x1+sizeXOut
#    y2=y1+sizeYOut
#    print("Cropping "+pic+" with values: "+str((x1,y1,x2,y2))+ " and saving in subdirectory cropped/")
#    im.crop((x1,y1,x2,y2)).save("cropped/"+pic)
#    #im.crop((x3,y1,x4,y2)).save("sound/"+pic)
#    if extractAudio:
#        x3=holeRightEdge+soundStartOffset
#        x4=holeRightEdge+soundMidOffset
#        x5=holeRightEdge+soundEndOffset
#        if mono:
#            left.readFrame(im.crop((x3,y1,x5,y2)))
#            #im.crop((x3,y1,x5,y2)).save("sound0/"+pic)
#        else:
#            left.readFrame(im.crop((x3,y1,x4,y2)))
#            #im.crop((x3-20,y1,x4,y2)).save("sound1/"+pic)
#            right.readFrame(im.crop((x4,y1,x5,y2)))
#            #im.crop((x4,y1,x5,y2)).save("sound2/"+pic)
            

    
    
left.close()
right.close()
