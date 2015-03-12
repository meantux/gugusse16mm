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

sample={
    "holeHeight" : 198,
    "holeWidth"  : 290,
    "imageHeight":2400,
    "imageWidth":2400,
    "frameHeight":1202,
    "frameWidth" :1602
}



def edgeOf(line, direction):
    checkwidth=int(len(line)/6)
    lowest=(0,0.0)
    highest=(0,0.0)
    #trace=[]
    for idx in range(checkwidth, len(line)-checkwidth):
        delta=0
        for i in range(1, checkwidth):
            diff=line[idx-i] - line[idx+i]
            delta= delta + (diff * abs(diff))
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
    floor=sorted(line, reverse=True)[int(1.05 * (sample['holeHeight'] * height / sample['imageHeight']))]
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
    floor=sorted(line, reverse=True)[int(1.05 * (sample['holeHeight'] * height / sample['imageHeight']))]
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
    floor=sorted(line, reverse=True)[int(1.05 * (sample['holeWidth'] * width / sample['imageWidth']))]
    for idx in range (0,len(line)):
        if line[idx] < floor:
            line[idx]=floor
    holeRightEdge=edgeOf(line, "lightToDark")


    print (sys.argv[1]+": topHole="+str(topHole)+", bottomHole="+str(bottomHole)+", holeRightEdge="+str(holeRightEdge))


        


im=Image.open(sys.argv[1])
holePosition(im)

