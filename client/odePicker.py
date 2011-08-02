#!/usr/bin/python
# -*- coding: utf8 -*-
from pandac.PandaModules import *
from odeBasics import *

class OdePicker:
	def __init__(self, wm):
		self.wm = wm
		
		self.crosshairRay = OdeRayGeom(self.wm.space, 1) # has to be longer than base.camLens.getFar()
		#self.crosshairRay = OdeRayGeom(self.space, infini)
		self.crosshairRay.setCollideBits(odeBitMask["crosshair"])
		self.crosshairRay.setCategoryBits(odeBitMask["crosshair"])
		self.crosshairRayId = self.crosshairRay.getId()
		
		self.crosshairSphere = OdeSphereGeom(self.wm.space, 500)
		self.crosshairSphere.setCollideBits(odeBitMask["crosshair"])
		self.crosshairSphere.setCategoryBits(odeBitMask["crosshair"])
		self.crosshairSphereId = self.crosshairSphere.getId()
		
		self.crosshairModel = NodePath("crossHairModel")
		#self.crosshairModel = loader.loadModel("smiley.egg")
		self.crosshairModel.reparentTo(render)
		#self.crosshairModel.setScale(10)
		
		self.targetGeomId = None
		self.targetModel = None
		
	def update(self, mpos):
		#pass
		self.setCrosshair(mpos)
		self.checkPickRay()
		
	def setCrosshair(self, mpos):
		self.crosshairSphere.setPosition(base.camera.getPos(render))
		nearPoint = Point3()
		farPoint = Point3()
		base.camLens.extrude(mpos, nearPoint, farPoint)
		#nearP = Vec3(render.getRelativePoint(camera, nearPoint))
		#farP = Vec3(render.getRelativePoint(camera, farPoint))
		nearP = Vec3(render.getRelativePoint(base.cam, nearPoint))
		farP = Vec3(render.getRelativePoint(base.cam, farPoint))
		
		direction = nearP-farP
		#direction.normalize()
		length = direction.length()
		direction.normalize()
		#self.crosshairRay.set(farP,direction)
		self.crosshairRay.set(farP,direction)
		self.crosshairRay.setLength(length)
		
	def checkPickRay(self):
		targetFound = False
		
		for ship in self.wm.shipList:
			geom = ship.geom
			entry = OdeUtil.collide(geom, self.crosshairRay)
			#print "Nombre de contacts : %s" % (entry.getNumContacts())
			if entry.getContactPoints():
				pos = entry.getContactPoints()[0]
				self.crosshairModel.setPos(pos)
				self.wm.gm.crosshair.setMode(0)
				#print "Setting a ship target"
				self.targetGeomId = geom.getId()
				targetFound = True
		
			
		for loot in self.wm.lootList:
			geom = loot.geom
			entry = OdeUtil.collide(geom, self.crosshairRay)
			if entry.getContactPoints():
				pos = entry.getContactPoints()[0]
				self.crosshairModel.setPos(pos)
				self.wm.gm.crosshair.setMode(0)
				self.targetGeomId= geom.getId()
				#print "Setting a loot target"
				targetFound = True
		
		for sbase in self.wm.baseList:
			geom = sbase.geom
			entry = OdeUtil.collide(geom, self.crosshairRay)
			if entry.getContactPoints():
				pos = entry.getContactPoints()[0]
				self.crosshairModel.setPos(pos)
				self.wm.gm.crosshair.setMode(0)
				self.targetGeomId= geom.getId()
				#print "Setting a base target"
				targetFound = True
						
		if not targetFound:
			#print "target not found"
			self.targetGeomId = None
			self.wm.gm.crosshair.setMode(1)
			#print "Just lost target..."
			entry = OdeUtil.collide(self.crosshairRay, self.crosshairSphere)
			if entry.getContactPoints():
				pos = entry.getContactPoints()[0]
				self.crosshairModel.setPos(pos)
			
	
