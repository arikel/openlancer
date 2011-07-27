#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

from odeBasics import *
from odeLaser import *

from db import *


class GunSlot:
	def __init__(self, gunData = None):
		self.pos = Point3(0,0,0) # relative position on the ship
		self.rotation = 0 # rotation % R, tilting
		self.classe = 1 # only guns with classe <= that can be equipped
		self.active = False # does it fire for now?
		
		# does it have a gun equipped?
		if gunData != None:
			self.setGunData(gunData)
		else:
			self.gunData = None
		
	def setGunData(self, gundata):
		self.gunData = gundata
		self.active = True
		self.refireTimer = 0.0
		
	def setPos(self, pos):
		self.pos = pos
	
	def setActive(self, active = True):
		self.active = active
	
	def enable(self):
		self.active = True
		
	def disable(self):
		self.active = False
	
	def unequip(self):
		self.gunData = None
		self.disable()
		
	def toggle(self):
		self.active = not self.active

class Ship(Body):
	def __init__(self, worldmanager, data = None):
		Body.__init__(self, worldmanager)
		if data != None:
			self.data = data
			self.name = self.data.name
		else:
			print "Error : Data for %s ship not found, aborting ship init."
			return None
		
		self.initModel()
		self.initOde()
		self.initGuns()
		
		self.hasPilot = False
		
	def destroy(self):
		#self.model.detachNode()
		#self.model.removeNode()
		self.model.remove()
		self.geomVisual.remove()
		self.body.destroy()
		self.geom.destroy()
		
	def initModel(self):
		#print "Ship init : model..."
		#self.model = NodePath("Ship")
		path = "models/ships/" + self.data.model
		#print "loading model %s" % (path)
		self.model = loader.loadModel(path)
		
		#self.model.setTexture(ts, tex)
		#self.model.setRenderModeWireframe()
		self.model.reparentTo(render)
		self.model.setScale(self.scale)
		
	def update(self, dt):
		self.updatePos()
		self.updateLasers(dt)
		self.reduceAngVel()
		self.reduceLinVel()
		self.geomVisual.setPos(0,self.getLinSpeed()*dt*10, 0)
		#self.geomVisual.setPos(self.body.getLinearVel())
	#---------------------------------------------------------------
	# guns
	#---------------------------------------------------------------
	def initGuns(self):
		self.gunSlots = []
		
		for gunSlot in self.data.gunSlots:
			point = gunSlot[0]
			classe = gunSlot[1]
			data = gunSlot[2]
			active = gunSlot[3]
			#print "(Ship) adding a gunSlot to ship %s, data = %s" % (self.name, data)
			slot = GunSlot()
			slot.setGunData(data)
			slot.setActive(active)
			slot.setPos(point)
			self.gunSlots.append(slot)
			

		
	def shootLasers(self, targetPos):
		for slot in self.gunSlots:
			if slot.active:
				if slot.refireTimer >= slot.gunData.refire:
					# time to shoot this one
					slot.refireTimer = 0.0
					self.wm.shootLaser(
						render.getRelativePoint(self.model, slot.pos),
						targetPos,
						self.body.getLinearVel(),
						slot.gunData
						)
				
					
	def updateLasers(self, dt):
		for slot in self.gunSlots:
			if slot.active:
				slot.refireTimer += dt
				#print "refire time updated : timer at %s" % (slot.gun.refireTimer)
				
	
	#---------------------------------------------------------------
	# model, ode body, and ode geom setup
	#---------------------------------------------------------------
	def initOde(self):
		#print "Ship init : ODE..."
		self.body = OdeBody(self.world)
		
		self.mass = OdeMass()
		self.mass.setSphereTotal(1, self.scale)
		#self.mass.setBoxTotal(1, self.scale)
		self.body.setMass(self.mass)
		self.body.setPosition(self.model.getPos(render))
		self.body.setQuaternion(self.model.getQuat(render))
		
		#self.trimeshData = OdeTriMeshData( self.model, True )
		#self.geom = OdeTriMeshGeom( self.space, self.trimeshData )
		#self.geom = OdeSphereGeom(self.space, self.scale/2.0)
		self.geom = OdeBoxGeom(self.space, self.scale*2)
		self.geom.setCollideBits(BitMask32(0b0001))
		self.geom.setCategoryBits(BitMask32(0b0001))
		self.geom.setBody(self.body)
		
		self.geomVisual = loader.loadModel("models/generic/box")
		#self.geomVisual = loader.loadModel("models/generic/ball")
		self.geomVisual.reparentTo(self.model)
		self.geomVisual.setScale(self.scale*2)
		
		self.id = self.geom.getId()
		
		self.linVelVisc = 0.99
		self.angVelVisc = 0.99
		
		self.initPushEngine()
		self.initSteerEngine()
		
	#---------------------------------------------------------------
	# engine setup
	#---------------------------------------------------------------
	def initPushEngine(self):
		self.pushForce = self.data.pushForce
		self.pushSideForce = self.data.pushSideForce
		self.pushSideForceFactor = self.data.pushSideForceFactor
		self.pushSpeed = 0.0
		self.pushMaxSpeed = self.data.pushMaxSpeed
		
		# linear motor : forward
		self.lMotor = OdeLMotorJoint(self.world)
		self.lMotor.attachBody(self.body, 0)
		self.lMotor.setNumAxes(1)
		self.lMotor.setAxis(0, 1, 0, 1, 0)
		self.lMotor.setParam(2, 0) # Vel
		self.lMotor.setParam(3, self.pushForce) # FMax
		self.lMotor.setParam(4, 1) # fudge, between 0 and 1 (default)
		self.lMotor.setParam(5, 0) # 0 : no bouncy, 1 : max bouncy
		
		# linear motor : side pushing
		self.lMotor2 = OdeLMotorJoint(self.world)
		self.lMotor2.attachBody(self.body, 0)
		self.lMotor2.setNumAxes(1)
		self.lMotor2.setAxis(0, 1, 1, 0, 0)
		self.lMotor2.setParam(2, 0) # Vel
		self.lMotor2.setParam(3, self.pushSideForce) # FMax
		self.lMotor2.setParam(4, 1) # fudge, between 0 and 1 (default)
		self.lMotor2.setParam(5, 0)
		
	def initSteerEngine(self):
		
		self.steerHForce = self.data.steerHForce
		self.steerHSpeed = 0.0
		self.steerHMaxSpeed = self.data.steerHMaxSpeed
		
		self.steerPForce = self.data.steerPForce
		self.steerPSpeed = 0.0
		self.steerPMaxSpeed = self.data.steerPMaxSpeed
		
		self.steerRForce = self.data.steerRForce
		self.steerRSpeed = 0.0
		self.steerRMaxSpeed = self.data.steerRMaxSpeed
		
		# angular motor 1 : H
		self.aMotor1 = OdeAMotorJoint(self.world)
		self.aMotor1.attachBody(self.body, 0)
		self.aMotor1.setMode(0)
		self.aMotor1.setNumAxes(1)
		self.aMotor1.setAxis(0, 1, 0, 0, 1)
		self.aMotor1.setParamVel(0, 0)
		self.aMotor1.setParamFMax(0, self.steerHForce)

		
		# angular motor 2 : P
		self.aMotor2 = OdeAMotorJoint(self.world)
		self.aMotor2.attachBody(self.body, 0)
		self.aMotor2.setMode(0)
		self.aMotor2.setNumAxes(1)
		self.aMotor2.setAxis(0, 1, 1, 0, 0)
		self.aMotor2.setParamVel(0, 0)
		self.aMotor2.setParamFMax(0, self.steerPForce)
		
		# angular motor 3 : R
		self.aMotor3 = OdeAMotorJoint(self.world)
		self.aMotor3.attachBody(self.body, 0)
		self.aMotor3.setMode(0)
		self.aMotor3.setNumAxes(1)
		self.aMotor3.setAxis(0, 1, 0, 1, 0)
		self.aMotor3.setParamVel(0, 0)
		self.aMotor3.setParamFMax(0, self.steerRForce)
		
	def setLinMotor(self, speed = 5):
		self.lMotor.setParam(2, speed)
	
	def setLinMotor2(self, speed = 5):
		self.lMotor2.setParam(2, speed)

	def setAngMotor1(self, angle=1):
		if angle > self.steerHMaxSpeed:
			angle = self.steerHMaxSpeed
		elif angle < - self.steerHMaxSpeed:
			angle = - self.steerHMaxSpeed
		self.aMotor1.setParamVel(1, angle)

	def setAngMotor2(self, angle=1):
		if angle > self.steerPMaxSpeed:
			angle = self.steerPMaxSpeed
		elif angle < - self.steerPMaxSpeed:
			angle = - self.steerPMaxSpeed
		self.aMotor2.setParamVel(1, angle)
		

	def setAngMotor3(self, angle=1):
		if angle > self.steerRMaxSpeed:
			angle = self.steerRMaxSpeed
		elif angle < - self.steerRMaxSpeed:
			angle = - self.steerRMaxSpeed
		self.aMotor3.setParamVel(1, angle)
	
	def getLinSpeed(self):
		return self.body.getLinearVel().length()
	
	def setSpeed(self, speed):
		self.pushSpeed = speed
		if self.pushSpeed > self.pushMaxSpeed:
			self.pushSpeed = self.pushMaxSpeed
		#elif self.pushSpeed < 0: #-self.pushMaxSpeed/10:
		#	self.pushSpeed = 0 #-self.pushMaxSpeed/10
		elif self.pushSpeed < -self.pushMaxSpeed/10:
			self.pushSpeed = -self.pushMaxSpeed/10
		
		self.setLinMotor(self.pushSpeed)
	
	def accelerate(self, dt):
		self.setSpeed(self.pushSpeed + dt*100)
	
	def decelerate(self, dt):
		self.setSpeed(self.pushSpeed - dt*200)
		
	def brake(self, dt):
		self.setSpeed(self.pushSpeed - dt*300)
			
	def rest(self):
		if self.pushSpeed < 0:
			self.pushSpeed = 0
		self.setLinMotor(self.pushSpeed)
		
	def stop(self):
		self.pushSpeed = 0
		self.setLinMotor(0)
		self.setLinMotor2(0)
		self.setAngMotor1(0)
		self.setAngMotor2(0)
		self.setAngMotor3(0)
		
	def steer(self, dx, dy, dt):
		self.setAngMotor1(dx*dt*-self.steerHMaxSpeed)
		self.setAngMotor2(dy*dt*self.steerPMaxSpeed)
		#self.setAngMotor3(dz*self.steerRMaxSpeed)
		#self.setAngMotor3(-self.model.getR()/20)
		
	def autoCorrectHpr(self):
		self.setAngMotor3(-self.model.getR()/20)
		self.setAngMotor2(-self.model.getP()/20)
		
	def roll(self, dz, dt):
		self.setAngMotor3(self.steerRMaxSpeed*dt*dz)
	
	
	def steerToPoint(self, targetPoint, dt=0.01):
		
		self.model.lookAt(targetPoint)
		targetHpr = self.model.getHpr()
		self.updatePos()
		
		hprMove = targetHpr - self.model.getHpr()
		#print "hprMove : %s" % (hprMove)	
		
		dist = (self.model.getPos()-targetPoint).length()
		dist2 = render.getRelativePoint(self.model, targetPoint).length()
		
		dx = -hprMove.getX()
		dy = hprMove.getY()
		dz = hprMove.getZ()
		
		if dx<-180: dx += 360
		if dx> 180:	dx -= 360
		if dy<-180: dy += 360
		if dy> 180:	dy -= 360
		
		#if abs(dx)<1.6 and abs(dy)<1.6:
		self.setAngMotor3(-self.model.getR()/20)
		
		
		if (-1 < dx < 1) and (-1 <dy < 1) :
		#(self.model.getPos()-targetPoint).length()
		#if (self.model.getPos()-targetPoint).length()<10:
			#print "target locked!"
			if dist> 80:
				#print "Accelerating towards target!"
				#self.setLinMotor(self.pushMaxSpeed)
				self.accelerate(dt)
				#print "pushing fast to target!"
				#self.steer(dx/180, dy/180, dt*100)
			elif dist > 10:
				self.setLinMotor(self.pushMaxSpeed*dist/80)
				#self.steer(dx/180, dy/180, dt*100)
				self.accelerate(dt/5.0)
				#print "target close, slowing down!"
			else:
				self.stop()
				#print "target reached i guess..."
		else:
			#self.brake(dt)
			self.setLinMotor(0)
			self.steer(dx/180, dy/180, dt*100)
			#print "ok where is it...(dx = %s, dy = %s)" % (dy, dy)
				#self.stop()

	def steerToTargetNP(self, np, dt=1.0/75.0):
		targetPoint = np.getPos(render)
		self.steerToPoint(targetPoint, dt)
		
	def steerAwayFromTargetNP(self, np, dt = 1.0/75.0):
		targetPoint = self.model.getPos(render) + self.model.getPos(render) - np.getPos(render)
		targetPoint = Vec3(targetPoint)
		targetPoint.normalize()
		targetPoint = 500*targetPoint()
		self.steerToPoint(targetPoint, dt)
		
		
class PilotAI:
	def __init__(self, ship):
		self.ship = ship
		
		self.targetPoint = None
		self.targetNode = None
		self.targetGeom = None
		
		self.mode = "idle"
		self.timer = 0.0
		
	def setMode(self, mode):
		self.mode = mode
		
		
