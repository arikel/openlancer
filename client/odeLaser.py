#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from direct.directbase import DirectStart

from direct.showbase import Audio3DManager
#from audio3DManager import Audio3DManager

from odeBasics import *
from db import *

audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
#audio3d = Audio3DManager(base.sfxManagerList[0], camera)
audio3d.setDistanceFactor(4.0)
audio3d.setListenerVelocityAuto()
#-----------------------------------------------------------------------
# Load all laser models
#-----------------------------------------------------------------------
laserModels = {}
laserNameList = ["ray1", "ray2", "ray3"]

for name in laserNameList:
	m = loader.loadModel("models/guns/" + name)
	m.setShaderOff(True)
	m.setBin("fixed",0)
	m.setLightOff(True)
	m.setScale(1, 10, 1)
	m.setTwoSided(True)
	#m.setTexture(ts, tex)
	m.show(BitMask32.bit(0))
	m.show(BitMask32.bit(1))
	laserModels[name] = m

laserSounds = {}
soundList = ["laser_mono", "slimeball_mono"]
for name in soundList:
	laserSounds[name] = audio3d.loadSfx("sounds/lasers/" + name + ".ogg")
	#laserSounds[name].setVolume(0.4)

exploSound1 = audio3d.loadSfx("sounds/space/explosion01.ogg")
#print pdir(exploSound1)
exploSound1.setVolume(1.0)
exploSound1.set3dMinDistance(100.0)
exploSound1.set3dMaxDistance(50000.0)

'''
def timer(task):
	laserModel.setShaderInput("time", task.time)
	return task.cont
	
taskMgr.add(timer, "shader")
'''

class Laser:
	#def __init__(self, wm, originPos, targetPos, speed, shipSpeed, lifeTime, ray = 0.5, bitMask = odeBitMask["npcLaser"]):
	def __init__(self, wm, originPos, targetPos, shipSpeed, gunData):
		self.genre = "laser"
		self.wm = wm
		self.gunData = gunData
		
		self.pos = Point3(originPos)
		self.targetPos = Point3(targetPos)
		
		self.direction = targetPos - originPos
		self.direction.normalize()
		
		#self.speed = speed
		self.shipSpeed = shipSpeed
		self.lifeTime = self.gunData.lifeTime
		
		#self.ray = ray
		self.geom = OdeSphereGeom(self.wm.space, self.gunData.ray)
		self.geom.setCollideBits(odeBitMask["npc"])
		self.geom.setCategoryBits(odeBitMask["npc"])
		self.geom.setPosition(self.pos)
		
		self.model = NodePath("laser")
		self.model.reparentTo(render)
		self.model.setPos(self.geom.getPosition())
		self.model.lookAt(self.targetPos)
		
		if self.gunData.model in laserModels:
			laserModels[self.gunData.model].show(BitMask32.bit(1))
			laserModels[self.gunData.model].instanceTo(self.model)
			
		self.model.hide(BitMask32.bit(0))
		self.model.show(BitMask32.bit(1))
		self.model.setShaderOff(True)
		self.model.setLightOff(True)
		
		if self.gunData.sound in laserSounds:
			#self.sound = laserSounds[self.gunData.sound]
			path = "sounds/lasers/" + self.gunData.sound + ".ogg"
			self.sound = audio3d.loadSfx(path)
			audio3d.attachSoundToObject(self.sound, self.model)
			#audio3d.setSoundMaxDistance(self.sound, 150)
			#audio3d.setSoundMinDistance(self.sound, 10)
			self.sound.set3dMinDistance(1.0)
			self.sound.set3dMaxDistance(1000.0)
			self.sound.play()
			
		self.body = OdeBody(self.wm.world)
		self.mass = OdeMass()
		self.mass.setSphereTotal(0.1, self.gunData.ray)
		self.body.setMass(self.mass)
		self.body.setPosition(self.pos)
		self.body.setQuaternion(self.model.getQuat(render))
		
		self.geom.setBody(self.body)
		self.body.setLinearVel(self.direction*self.gunData.speed+self.shipSpeed)#*self.speed)
		
		self.alive = True
		
	def getId(self):
		return self.geom.getId()
		
	def update(self, dt):
		self.lifeTime -= dt
		if self.lifeTime <= 0:
			self.destroy()
		else:
			self.model.setPos(self.geom.getPosition())
			'''
			self.model.setPosQuat(
				render,
				self.geom.getPosition(),
				Quat(self.geom.getQuaternion()))
			'''
			
	def destroy(self):
		audio3d.detachSound(self.sound)
		self.geom.destroy()
		self.body.destroy()
		self.model.remove()
		self.alive = False
		
	def hide(self):
		self.model.hide()
		
	def show(self):
		self.model.show()
