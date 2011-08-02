#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

class LightManager:
	def __init__(self):
		self.lightCenter = render.attachNewNode(PandaNode("center"))
		#self.lightCenter.setHpr(45,0,0)
		#self.lightCenter.lookAt(10,10,10)
		# Create Ambient Light
		self.ambientLight = AmbientLight('ambientLight')
		self.ambientLight.setColor(Vec4(0.2,0.2,0.2, 1))
		self.alight = self.lightCenter.attachNewNode(self.ambientLight)
		render.setLight(self.alight)

		# point light
		self.pointlight = PointLight("Light")
		self.light = self.lightCenter.attachNewNode(self.pointlight)
		#modelLight = loader.loadModel("misc/Pointlight.egg.pz")
		#modelLight.reparentTo(light)
		self.pointlight.setColor(Vec4(0.2,0.2,0.2,1))
		#self.light.setPos(0,15,10)
		render.setLight(self.light)
		
		# Spotlight
		self.spot = Spotlight("spot")
		self.spot.getLens().setNearFar(1,1000)
		self.spot.getLens().setFov(120)
		self.spot.setColor(Vec4(1,1,1,1))
		#self.spotlight = render.attachNewNode(self.spot)
		self.spotlight = self.lightCenter.attachNewNode(self.spot)
		
		#self.spotlight.setPos(self.light.getPos())
		#self.spotlight.setHpr(-45,0,0)
		self.spotlight.node().setShadowCaster(False)
		self.spotlight.lookAt(0,10,0)
		render.setLight(self.spotlight)
		
		
		'''
		# directional light
		self.dlight1 = DirectionalLight("dlight")
		self.dlight1.setColor(Vec4(0.5,0.5,0.5,1))
		self.dlight = self.lightCenter.attachNewNode(self.dlight1)
		self.dlight.lookAt(render, 0,0,0)
		#self.dlight.node().setShadowCaster(True)
		self.dlight.node().getLens().setFov(40)
		self.dlight.node().getLens().setNearFar(1, 200)
		self.dlight.node().setScene(render)
		self.dlight.node().getLens().setFilmSize(800,600)
		render.setLight(self.dlight)
		'''
		
		self.setPos((0,-20,2))
		
	def setPos(self, pos):
		self.lightCenter.setPos(pos)
		#self.light.setPos(pos)
		#self.spotlight.setPos(self.light.getPos())
		#self.spotlight.lookAt(render, 0,0,0)
		
	def reparentTo(self, parent):
		self.lightCenter.reparentTo(parent)
