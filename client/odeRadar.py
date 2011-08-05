#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os, random


from pandac.PandaModules import *

from direct.gui.OnscreenText import OnscreenText

from gui import *

from odeBasics import *
from odeLaser import *
from odeShip import *
from odePicker import *

class OdeRadar:
	def __init__(self, wm):
		self.wm = wm # worldManager, to get the player ship position, to compute the distance to target
		
		self.frame = DirectFrame(
			frameSize = (-0.25,0.25,-0.25,0.25),
			frameColor=(0.2, 0.6, 0.5, 0.0),
			pos = (0,0,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			sortOrder = -10
		)
		
		self.targetImg = makeImg(0,0,"img/generic/select5.png", 1)
		self.targetImg.setScale(0.1)
		self.targetImg.reparentTo(self.frame)
		
		self.distanceLabel = makeMsgCenter(0,-0.035)
		self.distanceLabel["scale"] = 0.035
		self.distanceLabel["font"] = FONT3
		self.distanceLabel.setPos(0,0.10)
		self.distanceLabel.reparentTo(self.frame)
		
		self.nameLabel = makeMsgCenter(0,0.02)
		self.nameLabel["scale"] = 0.035
		self.nameLabel["font"] = FONT3
		self.nameLabel.setPos(0,0.14)
		self.nameLabel.reparentTo(self.frame)
		self.nameLabel.setText("There will be name of loot.")
		
		self.bar1 = LifeBarre(1.0, "blue")
		self.bar1.reparentTo(self.frame)
		self.bar1.setPos(-0.1, -0.12)
		
		self.bar2 = LifeBarre(1.0, "red")
		self.bar2.reparentTo(self.frame)
		self.bar2.setPos(-0.1, -0.15)
		
		self.targetNP = None
		
		self.interval = LerpScaleInterval(self.targetImg, 0.25, 0.15, 0)
		self.sound = soundDic["radarSelect"]
		
		self.clearRadar()
		
	def setTargetNP(self, np):
		self.targetNP = np
		self.interval.start()
		self.sound.play()
		
	def setTargetGeomId(self, id):
		self.targetId = id
		
	def setTarget(self, id, np, name = "", genre=""):
		self.setTargetGeomId(id)
		self.setTargetNP(np)
		self.nameLabel.setText(str(name))
		self.targetGenre = str(genre)
		if self.targetGenre == "ship":
			self.bar1.setMaxVal(self.wm.shipDic[id].data.shieldHPMax)
			self.bar1.setVal(self.wm.shipDic[id].data.shieldHP)
			self.bar2.setMaxVal(self.wm.shipDic[id].data.coqueHPMax)
			self.bar2.setVal(self.wm.shipDic[id].data.coqueHP)
			
			#print "Locking target : HP = %s / %s" % (self.wm.shipDic[id].data.shieldHP,self.wm.shipDic[id].data.shieldHPMax)
	def update(self):
		if self.targetNP != None:
			self.show()
			self.setRadar()
		else:
			self.clearRadar()
			
	def clearRadar(self):
		self.hide()
	
	def hide(self):
		self.frame.hide()
	
	def show(self):
		self.frame.show()
	
	def destroy(self):
		self.frame.destroy()
	
	def clearTarget(self):
		self.targetNP = None
		self.targetId = None
		
		
	def setRadar(self):
		
		pos = self.targetNP.getPos(render)
		
		p3 = base.cam.getRelativePoint(render, Point3(pos))
		p2 = Point2()
		
		dist = (self.wm.ship.model.getPos() - pos).length()
		dist = formatDist(dist)
		
		if base.camLens.project(p3, p2):
			r2d = Point3(p2[0], 0, p2[1])
			a2d = aspect2d.getRelativePoint(render2d, r2d) 
			self.targetImg.setScale(0.15)
			self.distanceLabel.setText(dist)
			self.frame.setPos(a2d)
			self.distanceLabel.setPos(0,0.10)
			self.nameLabel.setPos(0,0.14)
			
				
		else:
			relPos = self.targetNP.getPos(base.camera)
			DX = relPos.getX()
			DY = relPos.getZ()
			fac = max(abs(DX), abs(DY))
			
			
			if abs(DX)==fac:
				DY = DY / fac
				DX = DX / fac*1.25
			else:
				DX = DX / fac*1.25
				DY = DY / fac*0.95
				if DY == 0.95:
					self.distanceLabel.setPos(0,-0.14)
					self.nameLabel.setPos(0,-0.10)
				else:
					self.distanceLabel.setPos(0,0.10)
					self.nameLabel.setPos(0,0.14)
			
			self.targetImg.setScale(0.1)
			
			self.distanceLabel.setText(dist)
			self.frame.setPos(DX,0,DY)
		if self.targetGenre == "ship":
			self.bar1.setVal(self.wm.shipDic[self.targetId].data.shieldHP)
			self.bar2.setVal(self.wm.shipDic[self.targetId].data.coqueHP)
		elif self.targetGenre == "loot":
			self.bar1.setVal(0)
			#self.bar2.setVal(self.wm.lootDic[self.targetId].data.coqueHP)
			self.bar2.setVal(self.bar2.maxVal)
			
