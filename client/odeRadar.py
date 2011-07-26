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
		self.targetImg = makeImg(0,0,"img/generic/select5.png", 1)
		self.targetImg.setScale(0.1)
		self.targetText = makeMsg(0,0)
		self.targetText["scale"] = 0.04
		self.targetText["font"] = FONT3
		self.targetNP = None
		
		self.interval = LerpScaleInterval(self.targetImg, 0.25, 0.15, 0)
		self.sound = soundDic["hud_expand"]
		
		self.clearRadar()
		
	def setTargetNP(self, np):
		self.targetNP = np
		self.interval.start()
		self.sound.play()
		
	def update(self):
		if self.targetNP != None:
			self.targetImg.show()
			self.targetText.show()
			self.setRadar()
		else:
			self.clearRadar()
			self.targetImg.hide()
			self.targetText.hide()
			
	def clearRadar(self):
		self.targetImg.hide()
		self.targetText.hide()
	
	def hide(self):
		self.clearRadar()
	
	def show(self):
		self.targetImg.show()
		self.targetText.show()
	
	def setRadar(self):
		
		self.targetImg.show()
		self.targetText.show()
		
		pos = self.targetNP.getPos(render)
		
		p3 = base.cam.getRelativePoint(render, Point3(pos))
		p2 = Point2()
		
		dist = (self.wm.ship.model.getPos() - pos).length()
		dist = formatDist(dist)
		# offset for msgTarget, according to where the target is
		msgTargetDx = 0
		msgTargetDy = -0.16
		
		if base.camLens.project(p3, p2):
			r2d = Point3(p2[0], 0, p2[1])
			a2d = aspect2d.getRelativePoint(render2d, r2d) 
			self.targetImg.setScale(0.15)
			self.targetImg.setPos(a2d)
			self.targetText.setPos(a2d[0]-0.015,a2d[2]+0.07)
			self.targetText.setText(dist)
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
				
			self.targetImg.setPos(DX, 0, DY)
			self.targetImg.setScale(0.1)
			self.targetText.setText(dist)
			self.targetText.setPos(DX-0.015, DY+0.07)
			

