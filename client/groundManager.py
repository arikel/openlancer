#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os, random


from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.directbase import DirectStart
from direct.filter.FilterManager import FilterManager

from skyBox import SkyBox
from particleEngine import AriTrail, ParticleEngine
from lightManager import LightManager
from gui import *

groundBgMusic = {}
groundBgMusic["hesperida_shop"] = loader.loadSfx("sounds/musics/b423b42.ogg")
groundBgMusic["hesperida_shop"].setVolume(1.99)

class GroundManager:
	def __init__(self, gm):
		self.gm = gm # GameManager, from game.py
		self.playerData = self.gm.playerData
		self.gui = GroundGui(self.playerData)
		
		skyName = "hipshot1"
		self.sky = SkyBox()
		self.sky.load(skyName)
		#self.sky.set(skyName)
		self.currentSkyName = skyName
		#self.sky.clear()
		
		self.bgMusic = groundBgMusic["hesperida_shop"]
		self.bgMusic.setVolume(0.3)
		self.bgMusic.setLoop(True)
		
	def start(self):
		self.bgMusic.setVolume(0.3)
		self.bgMusic.play()
		self.show()
	
	def stop(self):
		#self.bgMusic.stop()
		taskMgr.add(self.fadeMusicTask, "fadeMusicTask")
		self.sky.clear()
		self.hide()
	
	def show(self):
		self.gui.show()
		self.sky.set(self.currentSkyName)
		
	def hide(self):
		self.gui.hide()
		
	def destroy(self):
		self.stop()
		self.gui.destroy()
		
	def fadeMusicTask(self, task):
		dt = globalClock.getDt()
		vol = self.bgMusic.getVolume()
		self.bgMusic.setVolume(vol - dt/2.0)
		if vol <= 0.02:
			self.bgMusic.stop()
			#print "Stopping music, sinve vol at %s" % (vol)
			return Task.done
		#print "Fading out music, volume at %s" % (vol)
		return Task.cont
		
		
