#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os

from pandac.PandaModules import *
loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
#win-size 800 600
#win-size 1024 768
#win-size 1280 960
#win-size 1280 1024
win-fixed-size 1
#yield-timeslice 0 
#client-sleep 0 
#multi-sleep 0
basic-shaders-only #f
fullscreen #f
#audio-library-name null
""")

from direct.fsm.FSM import FSM
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from direct.gui.DirectGui import * # DGG, DirectButton
from direct.showbase.Transitions import Transitions

from odeSpace import *
from groundManager import *
from gui import *
from db import *

class GameManager(FSM):
	
	def __init__(self, filename):
		FSM.__init__(self, 'Game')
		
		self.savedGame = PlayerFileParser("save.xml")
		self.playerData = self.savedGame.playerData
		self.playerData.setShip(shipDb[self.playerData.ship.name])
		
		self.crosshair = MouseCursor()
		self.crosshair.setMode(1)
		
		self.mainMenu = MainMenu()
		self.mainMenu.hide()
		self.mainMenu.buttons[0]["command"] = self.request
		self.mainMenu.buttons[0]["extraArgs"] = ["Space"]
		
		self.mainMenu.buttons[1]["command"] = self.request
		self.mainMenu.buttons[1]["extraArgs"] = ["Ground"]
		
		self.mainMenu.buttons[3]["command"] = self.quit
		self.mainMenu.buttons[3]["extraArgs"] = [0]
		
		
		#self.groundGui = GroundGui(self.playerData)
		#self.groundWorldManager = GroundManager(self)
		
		#self.spaceWorldManager = SpaceOdeWorldManager(self)
		
		self.prevState = None
		
		self.trans = Transitions(loader)
		
		self.request("IntroMainMenu")
		#self.request("Space")
	
	def quit(self, extraArgs=[]):
		audio3d.detachListener()
		sys.exit()
		
	def getEscape(self):
		if self.state == "Space":
			if self.spaceWorldManager.camHandler.mode == "turret":
				self.spaceWorldManager.setMode("manual")
			else:
				self.prevState = "Space"
				self.request("IntroMainMenu")
			
		elif self.state == "Ground":
			self.prevState = "Ground"
			self.request("IntroMainMenu")
		elif self.state == "IntroMainMenu":
			if self.prevState is not None:
				self.request(self.prevState)
		
	def saveGame(self):
		self.savedGame.save()
	
	def enterIntroMainMenu(self):
		#print "we entered intro main menu"
		self.mainMenu.show()
		self.trans.fadeIn()
		
	def exitIntroMainMenu(self):
		#print("we exited intro main menu")
		self.trans.fadeOut()
		self.mainMenu.hide()
		
	def enterSpace(self):
		#print "we entered space"
		'''
		audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
		audio3d.setDistanceFactor(100)
		audio3d.setListenerVelocityAuto()
		#audio3d.attachListener(camera)
		'''
		self.trans.fadeIn()
		self.spaceWorldManager = SpaceOdeWorldManager(self)
		self.spaceWorldManager.start()
		
		
	def exitSpace(self):
		#print("we exited space")
		self.trans.fadeOut()
		self.spaceWorldManager.destroy()
		del self.spaceWorldManager
		
	def enterGround(self):
		#print "we entered ground"
		self.trans.fadeIn()
		self.groundWorldManager = GroundManager(self)
		self.groundWorldManager.start()
		
		
	def exitGround(self):
		#print("we exited ground")
		self.trans.fadeOut()
		self.groundWorldManager.destroy()
		del self.groundWorldManager


g = GameManager("save2.txt")

props = WindowProperties()
props.setCursorHidden(True) 
base.win.requestProperties(props)

base.disableMouse()

base.setFrameRateMeter(True)
base.setBackgroundColor(0,0,0)
base.accept("escape", g.getEscape, [])
base.camLens.setNearFar(1,100000)
base.camLens.setFov(80)

render.setAntialias(AntialiasAttrib.MMultisample)


run()


