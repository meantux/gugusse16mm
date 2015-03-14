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

stream=[]


sample={
    "holeHeight" : 168,
    "holeWidth"  : 234,
    "imageHeight":1948,
    "imageWidth" :1949,
    "frameHeight": 968,
    "frameWidth" :1312,
    "frameYoffset":  80,
    "frameXoffset":  18
}

def square(x):
    return x*x

def edgeOf(line, direction):
    checkwidth=int(len(line)/6)
    lowest=(0,0.0)
    highest=(0,0.0)
    #trace=[]
    for idx in range(checkwidth, len(line)-checkwidth):
        delta=0
        for i in range(1, checkwidth):
            diff=(square(line[idx-i]) - square(line[idx+i]))
            delta+=diff
        #trace.append((idx,delta))
        if(delta<lowest[1]):
            lowest=(idx, delta)
        if(delta>highest[1]):
            highest=(idx, delta)
    #print (str(trace))
    if direction == "darkToLight":
        return lowest[0]
    if direction == "lightToDark":
        return highest[0]

def holePosition(im):
    width=im.size[0]
    height=im.size[1]
    
    # Let's figure out the top and bottom of the upper hole
    line=[]
    for y in range(0,int(height/2)):
        total=0
        for i in im.getpixel((width/10, y)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(2.0 * (sample['holeHeight'] * height / sample['imageHeight']))]
    for idx in range (0,int(height/2)):
        if line[idx] < floor:
            line[idx]=floor
    topHole=edgeOf(line, "darkToLight")

    line=[]
    for y in range(int(height/2), height):
        total=0
        for i in im.getpixel((width/10, y)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(1.5 * (sample['holeHeight'] * height / sample['imageHeight']))]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    bottomHole=int(height/2)+edgeOf(line, "darkToLight")

    line=[]
    y=topHole+int((bottomHole-topHole)/(2*sample['frameHeight']/sample['holeHeight']))
    print("Checking right edge at y="+str(y))
    for x in range(0,int(width/4)):
        total=0
        for i in im.getpixel((x, y)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(1.5 * (sample['holeWidth'] * width / sample['imageWidth']))]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    holeRightEdge=edgeOf(line, "lightToDark")

    line=[]
    y=bottomHole+int((bottomHole-topHole)/(2*sample['frameHeight']/sample['holeHeight']))
    #print("Checking right edge at y="+str(y))
    for x in range(0,int(width/4)):
        total=0
        for i in im.getpixel((x, y)):
            total+=i
        line.append(total)
    # The floor value will be used to prevent brand markings between holes to
    # interfere with the (fragile) logic of edge detection
    floor=sorted(line, reverse=True)[int(1.5 * (sample['holeWidth'] * width / sample['imageWidth']))]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    holeRightEdgeLower=edgeOf(line, "lightToDark")


    print ("topHole="+str(topHole)+", bottomHole="+str(bottomHole)+", holeRightEdge="+str(holeRightEdge))
#    for i in range(-10,10):
#        im.putpixel((int(width/10)+i, topHole),(255,0,0))
#        im.putpixel((int(width/10)+i, bottomHole),(255,0,0))
#        im.putpixel((holeRightEdge,10+topHole+i ),(255,0,0))
    return (topHole, bottomHole, holeRightEdge, holeRightEdgeLower)
        

positions={}
numOfImages=0
totalTopHole=0
totalBottomHole=0
totalHoleRightEdge=0
totalHoleRightEdgeLower=0
for pidx in range(1,len(sys.argv)):    
    try:
        im=Image.open(sys.argv[pidx])
        results=holePosition(im)
        positions[sys.argv[pidx]]=results
        numOfImages+=1
        totalTopHole+=results[0]
        totalBottomHole+=results[1]
        totalHoleRightEdge+=results[2]
        totalHoleRightEdgeLower+=results[3]
    except:
        pass
avgTopHole=int(totalTopHole/numOfImages)
avgBottomHole=int(totalBottomHole/numOfImages)
avgHoleRightEdge=int(totalHoleRightEdge/numOfImages)
avgHoleRightEdgeLower=int(totalHoleRightEdgeLower/numOfImages)


avgDeltaHole=avgBottomHole-avgTopHole
avgDeltaEdge=int((avgHoleRightEdge+avgHoleRightEdgeLower)/2)

sizeYOut=avgDeltaHole + (avgDeltaHole % 2)
sizeXOut=int(avgDeltaHole * 2 / 3) * 2
scaledXOffset=int(sample['frameXoffset']*sizeXOut/sample['frameWidth'])
scaledYOffset=int(sample['frameYoffset']*sizeYOut/sample['frameHeight'])

for pic in positions:
    im=Image.open(pic)
    results=positions[pic]
    topHole=results[0]
    bottomHole=results[1]
    holeRightEdge=results[2]
    holeRightEdgeLower=results[3]
    if abs(topHole-avgTopHole) < abs(bottomHole-avgBottomHole):
        bottomHole=topHole+avgDeltaHole
    else:
        topHole=bottomHole-avgDeltaHole
    if abs(holeRightEdge-avgHoleRightEdge) < abs(holeRightEdgeLower-avgHoleRightEdgeLower):
        holeRightEdgeLower=avgHoleRightEdgeLower + holeRightEdge-avgHoleRightEdge
    else:
        holeRightEdge=avgHoleRightEdge+holeRightEdgeLower-avgHoleRightEdgeLower
    x1=holeRightEdge+scaledXOffset
    y1=topHole+scaledYOffset
    x2=x1+sizeXOut
    y2=y1+sizeYOut
    print("Cropping "+pic+" with values: "+str((x1,y1,x2,y2))+ " and saving in subdirectory cropped/")
    im.crop((x1,y1,x2,y2)).save("cropped/"+pic)
    
