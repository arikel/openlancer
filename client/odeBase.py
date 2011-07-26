#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os, random


from pandac.PandaModules import *

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.directbase import DirectStart
from direct.filter.FilterManager import FilterManager
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *

from skyBox import SkyBox
from particleEngine import AriTrail, ParticleEngine
from lightManager import LightManager
from gui import *

#from db import *

from odeBasics import *
from odeLaser import *
from odeShip import *
from odePicker import *
from odeRadar import *

def makePlanet(name, scale = 1.0):
	path = "img/textures/planets/" + str(name) + ".jpg"
	tex = loader.loadTexture(path)
	model = loader.loadModel("models/planets/genericplanet")
	model.setTexture(tex, 1)
	model.setScale(scale)
	return model

class OdeBase:
	def __init__(self, wm, name=""):
		self.wm = wm
		self.scale = 1.0
		
		if name in spaceBaseDb:
			self.data = spaceBaseDb[name]
		else:
			self.data = None
			print "Warning : base name not found."
			return
		
		self.modelList = []
		self.geomList = []
		self.geomIdList = []
		
		
		self.model = Actor.Actor("models/bases/landgate")
		self.model.loadAnims({"open":"models/bases/landgate-anim1"})
		self.model.loadAnims({"close":"models/bases/landgate-anim2"})
		
		self.model.reparentTo(render)
		
		i1 = self.model.actorInterval("open", 1)
		i2 = self.model.actorInterval("close", 1)
		
		self.seq = Sequence()
		self.seq.append(i1)
		self.seq.append(i2)
		self.seq.loop()
		
		self.geom = OdeBoxGeom(self.wm.space, self.scale)
		self.geom.setCollideBits(odeBitMask["npc"])
		self.geom.setCategoryBits(odeBitMask["npc"])
		
		self.planet = makePlanet("mars", 2.0)
		self.planet.reparentTo(render)
		
		self.shipList = [] # list of ships waiting to dock, in or out
		
	def getId(self):
		return self.geom.getId()
		
	def show(self):
		self.model.show()
		self.planet.show()
		
	def hide(self):
		self.model.hide()
		self.planet.hide()	
	
	def destroy(self):
		self.model.cleanup()
		self.model.removeNode()
		self.planet.removeNode()
		self.geom.destroy()
