#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os, random


from pandac.PandaModules import *


from db import *

def SameVec(pt1, pt2):
	return (pt1 - pt2).length() < 1E-5 

def formatDist(dist):
	if dist < 1000:
		dist = str(int(dist))# + " M"
	else:
		dist = str(int(dist / 100.0) / 10.0) + " K"
	return dist
	
def ReduceContactGroup(contactGroup):
	tlist = [ contactGroup[i] for i in xrange(contactGroup.getNumContacts()) ]
	i = 0
	while i < len(tlist):
		j = i + 1
		while j < len(tlist):
			if (SameVec(tlist[i].getPos(), tlist[j].getPos())):
				tlist.pop(j)
			else:
				j += 1
		i += 1
	return tlist
	
def makeWorld():
	world = OdeWorld()
	world.setGravity(0, 0, 0)#-9.81
	world.initSurfaceTable(1)
	world.setCfm(0.00001)
	world.setErp(0.6)
	#world.setAutoDisableFlag(1)
	#world.setAutoDisableAngularThreshold(0.3)
	#world.setAutoDisableLinearThreshold(0.3)#0.1
	#world.setAutoDisableSteps(30)
	#world.setAutoDisableTime(0.0)
	
	#world.setSurfaceEntry(surfaceID1, surfaceID2, mu, bounce, bounce_vel, soft_erp, soft_cfm, slip, dampen)
	world.setSurfaceEntry(0, 0, 20, 0.5, 9.1, 0.9, 0.00001, 0.9, 0.002)
	return world

odeBitMask = {}
odeBitMask["playerShip"] =  BitMask32(0b000001)
odeBitMask["playerLaser"] = BitMask32(0b000100)

odeBitMask["npc"] =         BitMask32(0b000101)
odeBitMask["npcLaser"] =    BitMask32(0b001000)

odeBitMask["particle"] =    BitMask32(0b000000)
odeBitMask["crosshair"] =   BitMask32(0b000000) # used for picker : crosshairRay and crosshairSphere with OdeUtil.collide() only


'''
class Floor:
	def __init__(self, space, height):
		scale = 15000
		self.geom = OdePlaneGeom(space, 0,0,1,height)
		self.geom.setCollideBits(BitMask32(0b0001))
		self.geom.setCategoryBits(BitMask32(0b0001))
		cm = CardMaker("floor")
		cm.setFrame(-scale, scale, -scale, scale)
		cm.setHasNormals(True)
		cm.setUvRange(0,scale/100)
		
		self.floorModel = render.attachNewNode(cm.generate())
		self.floorModel.setPos(0, 0, height)
		self.floorModel.lookAt(0, 0, -1)
		self.floorModel.setColor(1,1,1,0.5)
		tex = loader.loadTexture("models/-0Sand.JPG")
		self.floorModel.setTexture(tex, 1)
'''
		
class Body(object):
	def __init__(self, worldmanager, scale=1):
		self.wm = worldmanager
		self.world = self.wm.world
		self.space = self.wm.space
		self.scale = scale
		
		self.linVelVisc = 0.99
		self.angVelVisc = 0.99
		
		self.name = "body"
		self.genre = "body"
	def setPos(self, pos):
		self.body.setPosition(pos)
		self.updatePos()

	def updatePos(self):
		self.model.setPosQuat(render, self.body.getPosition(), Quat(self.body.getQuaternion()))
		
	def reduceAngVel(self):
		self.body.setAngularVel(self.body.getAngularVel()*self.linVelVisc)
		
	def reduceLinVel(self):
		self.body.setLinearVel(self.body.getLinearVel()*self.angVelVisc)
	
	def getId(self):
		return self.geom.getId()
	
	def update(self, dt):
		self.updatePos()
		self.reduceAngVel()
		self.reduceLinVel()
	
	def destroy(self):
		self.model.remove()
		self.body.destroy()
		self.geom.destroy()
		
	def hide(self):
		self.model.hide()
		
	def show(self):
		self.model.show()
		
class Cube(Body):
	def __init__(self, worldmanager, scale=1):
		Body.__init__(self, worldmanager, scale)
		self.model = loader.loadModel("models/generic/box.egg")
		self.model.reparentTo(render)
		random.seed()
		self.model.setColor(random.random(), random.random(), random.random(), 1)
		self.model.setScale(self.scale)
		self.model.setPos(0,0,self.scale/2+1)
		self.body = OdeBody(self.world)
		self.mass = OdeMass()
		self.mass.setBoxTotal(1, self.scale)
		self.body.setMass(self.mass)
		self.updatePos()

		self.geom = OdeBoxGeom(self.space, self.scale)
		self.geom.setCollideBits(odeBitMask["npc"])
		self.geom.setCategoryBits(odeBitMask["npc"])
		self.geom.setBody(self.body)
		
		self.linVelVisc = 0.99
		self.angVelVisc = 0.99

		self.genre = "cube"
		

class Sphere(Body):
	def __init__(self, worldmanager, scale):
		Body.__init__(self, worldmanager, scale)

		self.model = loader.loadModel("models/generic/ball.egg")
		#self.model = NodePath("Sphere")
		self.model.reparentTo(render)
		self.model.setScale(self.scale)
		self.body = OdeBody(self.world)
		self.mass = OdeMass()
		self.mass.setSphereTotal(1, self.scale)
		self.body.setMass(self.mass)
		self.body.setPosition(self.model.getPos(render))
		self.body.setQuaternion(self.model.getQuat(render))

		self.geom = OdeSphereGeom(self.space, self.scale)
		self.geom.setCollideBits(odeBitMask["npc"])
		self.geom.setCategoryBits(odeBitMask["npc"])
		self.geom.setBody(self.body)

		self.genre = "sphere"
