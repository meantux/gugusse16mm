#!/usr/bin/python

# import the pygame module, so you can use it
import pygame, pygbutton
import Tkinter, tkFileDialog, os, sys

screen=None
buttons=[]
tkroot=Tkinter.Tk()
tkroot.withdraw()
currdir=os.getcwd()
fromdir=None
todir=None

def addButton(caption, func):    
    print "Adding button "+caption
    newbutton=pygbutton.PygButton((10,30 + 40 * len(buttons), 200,30), caption)
    buttons.append((newbutton, func))
    
def selInDir():
    fromdir=tkFileDialog.askdirectory(parent=tkroot, initialdir=currdir, title='Please select the directory of the original pictures')

def selOutDir():
    todir=tkFileDialog.askdirectory(parent=tkroot, initialdir=currdir, title='Please select a directory for output')

def selImage():
    print "selImage"

def setHoleCoord():
    print "setHoleCoord"

def setFrameCoord():
    print "setFrameCoord"

def setAudioCoord():
    print "setAudioCoord"

def changeAudioMode():
    print "ChangeAudioMode"

def render():
    print "RENDER"


# define a main function
def main():
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("La Gugusse 16mm - Stabilization")
    
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((1280,720))

    addButton('Set In Directory', selInDir)
    addButton('Set Out Directory', selOutDir)
    addButton('Choose Ref. Pix', selImage)
    addButton('Set Hole Coord.', setHoleCoord)
    addButton('Set Frame Coord.', setFrameCoord)
    addButton('Set Audio Coord.', setAudioCoord)
    addButton('Audio Mode', changeAudioMode)
    addButton('RENDER', render)
    for but in buttons:
        but[0].draw(screen)
    pygame.display.flip()
    
    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            for but in buttons:
                if 'click' in but[0].handleEvent(event):
                    but[1]()
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
    
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
