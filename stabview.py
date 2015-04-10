#!/usr/bin/python
import pygame
import Tkinter
import tkFileDialog
import os, sys

from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'

class PyManMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    def __init__(self, width=1280,height=720):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        """Set the window Size"""
        self.width = width
        self.height = height
        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("La Gugusse 16mm - Picture stabilization")
        self.font = pygame.font.Font(None, 36)
        text=self.font.render("Hello There", 1, (80, 80, 80))
        textpos=text.get_rect()
	background = pygame.Surface(self.screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))
	textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text, textpos)
        self.screen.blit(background, (0, 0))
        pygame.display.flip()
    def MainLoop(self):
        """This is the Main Loop of the Game"""
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
 

tkroot=Tkinter.Tk()
tkroot.withdraw()

currdir=os.getcwd()
#fromdir=tkFileDialog.askdirectory(parent=tkroot, initialdir=currdir, title='Please select the directory of the original pictures')
#todir=tkFileDialog.askdirectory(parent=tkroot, initialdir=currdir, title='Now please select another directory for output')

#if fromdir == todir:
#    print "The input and output directories must not be the same (operation cancelled)"
#    sys.exit(0)

MainWindow = PyManMain()
MainWindow.MainLoop()

