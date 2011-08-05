#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os, random


from pandac.PandaModules import *

'''
loadPrcFileData("setup", """sync-video 0
#win-size 1280 1024
win-size 1024 768
#win-size 1024 960
#win-size 800 600
yield-timeslice 0 
client-sleep 0 
multi-sleep 0
basic-shaders-only #f
fullscreen #f
#audio-library-name null
""")
'''

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.directbase import DirectStart
from direct.showbase import Audio3DManager
from direct.filter.FilterManager import FilterManager

from skyBox import SkyBox
from particleEngine import AriTrail, ParticleEngine
from lightManager import LightManager
from gui import *

from odeBasics import *
from odeLaser import *
from odeShip import *
from odeBase import *
from odePicker import *
from odeRadar import *



spaceBgMusic = {}
#spaceBgMusic["hesperida_space"] = loader.loadSfx("sounds/musics/cold_silence.ogg")
spaceBgMusic["hesperida_space"] = loader.loadSfx("sounds/musics/giii_8inst_1.ogg")
spaceBgMusic["hesperida_space"].setLoop(True)
spaceBgMusic["hesperida_space"].setVolume(0.4)

class SpaceCamManager:
	def __init__(self, wm):
		self.wm = wm
		self.mode = "manual"
		self.baseNode = NodePath("camCenter")
		self.baseNode.reparentTo(self.wm.ship.model)
		
		self.targetNode = NodePath("camTarget")
		self.targetNode.reparentTo(self.baseNode)
		
		self.camCube = Cube(self.wm, 0.1)
		self.camCube.model.detachNode()
		self.camCube.geom.setCollideBits(BitMask32(0b00))
		self.camCube.geom.setCategoryBits(BitMask32(0b00))
		self.camCube.body.setPosition(self.wm.ship.model.getPos()+(Point3(0,-20, 3)))
		
		self.basePoint = Point3(0,-20, 3)
		self.decal = Vec3(5.5,0,0.5)

		self.update()
		
	def update(self, dx=0, dy=0):
		if self.mode == "manual":
			#target = render.getRelativePoint(self.ship.model, Point3(0+dx*4,-10,3+dy*1.5))
			#self.decal = Vec3(dx*5.5,0,dy*0.5)
			self.targetNode.setPos(0,300,0)
			self.baseNode.setHpr(0,0,0)
			self.baseNode.setPos(dx*5, -20, 2+dy*0.5)
			
			#target = render.getRelativePoint(self.wm.ship.model, self.basePoint + self.decal)
			target = self.baseNode.getPos(render)
			
			dist = (target - base.camera.getPos()).length()
			#self.camCube.body.addForce((target - self.camCube.body.getPosition())*dist*12.55)
			self.camCube.body.addForce((target - self.camCube.body.getPosition())*dist)
			base.camera.setPos(self.camCube.body.getPosition())
			#base.camera.lookAt(render.getRelativePoint(self.wm.ship.model, Point3(0,1000,0)))
			base.camera.lookAt(self.targetNode)
			base.camera.setR(self.wm.ship.model.getR())
			if self.camCube.body.getLinearVel().length()>500.0:
				self.camCube.body.setLinearVel(0,0,0)
			self.camCube.body.setLinearVel(self.camCube.body.getLinearVel()*0.95)
			
			
			#base.camera.setQuat(render, Quat(self.camCube.body.getQuaternion()))
			
			
		elif self.mode == "auto":
			self.targetNode.setPos(0.0,300,0.0)
			self.baseNode.setHpr(0.0,0.0,0.0)
			self.baseNode.setPos(0, -16, 5)
			
			#target = render.getRelativePoint(self.wm.ship.model, self.basePoint)
			target = self.baseNode.getPos(render)
			
			dist = (target - base.camera.getPos()).length()
			self.camCube.body.addForce((target - self.camCube.body.getPosition())*dist*12.5)
			base.camera.setPos(self.camCube.body.getPosition())
			base.camera.setR(self.wm.ship.model.getR())
			#base.camera.lookAt(render.getRelativePoint(self.wm.ship.model, Point3(0,1000,0)))
			base.camera.lookAt(self.targetNode)
			self.camCube.body.setLinearVel(self.camCube.body.getLinearVel()*0.94)
		
		elif self.mode == "turret":
			self.baseNode.setPos(0,0,0)
			self.targetNode.setPos(0,-40,0)
			self.baseNode.setH(self.baseNode.getH()- dx)
			self.baseNode.setP(self.baseNode.getP()+ dy)
			#print "turret : %s %s " % (dx, dy)
			if self.baseNode.getP()>90:
				self.baseNode.setP(90)
			elif self.baseNode.getP()<-90:
				self.baseNode.setP(-90)
			
			self.baseNode.setR(0)
			self.targetNode.setR(0)
			
			base.camera.setPos(self.targetNode.getPos(render))
			base.camera.setHpr(self.targetNode.getHpr(render))
			#base.camera.lookAt(self.baseNode)
			self.camCube.setPos(self.baseNode.getPos(render))
		
class SpaceOdeWorldManager(DirectObject):
	def __init__(self, gamemanager):
		# GameManager, from game.py
		self.gm = gamemanager
		
		# ODE base setup
		self.world = makeWorld()
		self.space = OdeSimpleSpace()
		self.space.setAutoCollideWorld(self.world)
		self.space.setCollisionEvent("ode-collision")
		self.accept("ode-collision", self.onCollision)
		self.contactGroup = OdeJointGroup()
		self.space.setAutoCollideJointGroup(self.contactGroup)
		
		#---------------------------------------------------------------
		# space objects lists and dics
		#---------------------------------------------------------------
		self.shipList = []
		self.shipDic = {}
		
		self.laserList = []
		self.laserDic = {}
		
		self.lootList = []
		self.lootDic = {}
		
		self.baseList = []
		self.baseDic = {}
		
		
		#---------------------------------------------------------------
		self.dtCumul = 0.0
		self.stepSize = 1.0 / 75.0
		
		#---------------------------------------------------------------
		# crosshair stuff, to aim guns and click on 3D objects with the mouse.
		# This same crosshair is used when on the ground for GUI too, for now.
		#---------------------------------------------------------------
		
		self.gm.crosshair.setMode(1)
		self.currentTargetDest = None
		self.currentTargetNP = None
		
		self.picker = OdePicker(self)
		
		
		#---------------------------------------------------------------
		# input handling
		self.keyMap = {}
		self.acceptAll()
		#---------------------------------------------------------------
		# some loot
		for i in range(10):
			cube = Cube(self, 5)
			#cube = Sphere(self, 5)
			cube.setPos((i*0.02,i*0.02,5.5*i+2.51))
			name = "Cube " + str(i)
			cube.name = name
			self.lootList.append(cube)
			self.lootDic[cube.geom.getId()] = cube
			
		#---------------------------------------------------------------
		# player ship
		self.ship = Ship(self, self.gm.playerData.ship)
		self.ship.setPos((0,-20,12.51))
		
		#---------------------------------------------------------------
		# bases
		self.addBase("hesperida")
		
		

		#---------------------------------------------------------------
		# camera
		self.mode = "manual"
		self.camHandler = SpaceCamManager(self)
		self.camHandler.update()
		
		#---------------------------------------------------------------
		# radar
		self.radar = OdeRadar(self)
		
		#---------------------------------------------------------------
		# light
		self.light = LightManager()
		self.light.lightCenter.reparentTo(self.ship.model)
		
		#---------------------------------------------------------------
		# stardust cloud surrounding the player ship
		#self.PE = ParticleEngine(self.ship.model.getPos(), nb=100, ray=100, move = True)
		self.PE = ParticleEngine(self.ship.model, nb=50, ray=100, move = True)
		self.PE.stop()
		
		#---------------------------------------------------------------
		# trail of the player ship, TODO : move that to the OdeShip class and update ShipData to handle it
		self.trailPE = AriTrail(self.ship.model,20,0.0)
		#self.trailPE2 = AriTrail(self.gun2,10,0.0)
		
		#skyName = "skyBox06"
		skyName = "purple0"
		self.sky = SkyBox()
		self.sky.load(skyName)
		self.sky.set(skyName)
		self.currentSkyName = skyName
		self.sky.stop()
		#self.sky.currentModel.hide(BitMask32.bit(1))
		
		
		#-------------------------------------------------------------------
		# GUI
		#-------------------------------------------------------------------
		self.gui = SpaceGui(self.gm.playerData)
		
		#self.msgSpeed = OnscreenText(pos=(-0.98, -0.755), fg = (1,1,1,1), scale = 0.05, align=TextNode.ALeft, mayChange = 1)
		#self.msgSpeed["font"] = FONT
		#self.msgSpeed["scale"] = (0.04,0.05,1.0)
		
		# BG music
		self.bgMusic = spaceBgMusic["hesperida_space"]
		
		
		self.NPCTimer = 0.0
		
		#self.accept("t", self.step)
		#self.start()
		self.task = None
		
		self.stop()
		
	def acceptAll(self):
		self.accept("ode-collision", self.onCollision)
		
		for key in ("a", "z", "e", "q", "s", "d", "w", "c", "r",
		"arrow_up", "arrow_down", "mouse1", "mouse3"
		):
			self.keyMap[key] = 0
			self.accept(key, self.setKey, [key, 1])
			keyup = key + "-up"
			self.accept(keyup, self.setKey, [key, 0])
		
		self.accept("space", self.toggleMode)
		self.accept("mouse1", self.selectClick)
		self.accept("p", self.spawnShip)
		
	def start(self):
		#print "Starting the space world."
		self.acceptAll()
		self.task = taskMgr.doMethodLater(1.5, self.worldTask, "spaceWorldTask")
		self.sky.set(self.currentSkyName)
		self.PE.start()
		self.showAll()
		self.radar.hide()
		self.bgMusic.play()
		#print "Le root de audio3d c'est %s" % (audio3d.root)
		taskMgr.doMethodLater(1.5, self.start3DAudio, "start3DAudio")
		
	def start3DAudio(self, task):
		#audio3d.attachListener(camera)
		audio3d.__init__(base.sfxManagerList[0], camera)
		#taskMgr.add(audio3d.update, "Audio3DManager-updateTask", 51)
		#print "restarted 3D audio!"
		return Task.done
		
	def stop(self):
		#print "Stopping the space world."
		
		#audio3d.detachSound()
		'''
		for sound in laserSounds:
			audio3d.detachSound(laserSounds[sound])
		audio3d.detachListener()
		'''
		audio3d.disable()
		#print "disabled 3D audio!"
		
		if self.task:
			#print "really stopped the world"
			taskMgr.remove(self.task)
			self.sky.stop()
			self.PE.stop()
			self.task = None
		#else:
			#print "Found no world running to stop though..."

		self.hideAll()
		self.ignoreAll()
		self.gm.crosshair.setMode(1)
		self.bgMusic.stop()
		
	def hideAll(self):
		for id in self.shipDic.keys():
			self.shipDic[id].hide()
		for id in self.lootDic.keys():
			self.lootDic[id].hide()
		for id in self.laserDic.keys():
			self.laserDic[id].hide()
		for id in self.baseDic.keys():
			self.baseDic[id].hide()
			
		self.ship.model.hide()
		self.radar.hide()
		#self.msgSpeed.hide()
		self.PE.stop()
		self.trailPE.stop()
		self.gui.hide()
		
	def showAll(self):
		for id in self.shipDic.keys():
			self.shipDic[id].show()
		for id in self.lootDic.keys():
			self.lootDic[id].show()
		for id in self.laserDic.keys():
			self.laserDic[id].show()
		for id in self.baseDic.keys():
			self.baseDic[id].show()
			
		self.ship.model.show()
		self.radar.show()
		#self.msgSpeed.show()
		self.PE.start()
		self.trailPE.start()
		self.gui.show()
		
	def destroy(self):
		self.stop()
		
		self.sky.clear()
		
		for id in self.shipDic.keys():
			self.destroyShip(id)
		
		for id in self.lootDic.keys():
			#print "Destroying ", self.lootDic[id].name
			self.destroyLoot(id)
		
		for id in self.laserDic.keys():
			self.destroyLaser(id)
		
		for id in self.baseDic.keys():
			self.destroyBase(id)
		
		self.gui.destroy()
		self.radar.destroy()
		self.ship.destroy()
		
	def setKey(self, k, v):
		self.keyMap[k] = v
	
	def onCollision(self, entry):
		geom1 = entry.getGeom1()
		geom2 = entry.getGeom2()
		body1 = entry.getBody1()
		body2 = entry.getBody2()
		
		# Must have hit someone
		#print "World, ", geom1, geom2, body1, body2
		id1 = geom1.getId()
		id2 = geom2.getId()
		
		contactPoint = entry.getContactPoints()[0]
		
		if ((id1 in self.lootDic) and (id2 in self.laserDic)):
			#print "Collision cube / laser!!! l'oeuf tombe sur la pierre!"
			#exploSound1 = audio3d.loadSfx("sounds/space/explosion01.ogg")
			audio3d.attachSoundToObject(exploSound1, self.lootDic[id1].model)
			exploSound1.play()
			self.destroyLaser(id2)
		
		elif ((id2 in self.lootDic) and (id1 in self.laserDic)):
			#print "Collision laser / cube!!! This is gonna hurt!"
			#exploSound1 = audio3d.loadSfx("sounds/space/explosion01.ogg")
			audio3d.attachSoundToObject(exploSound1, self.lootDic[id2].model)
			exploSound1.play()
			self.destroyLaser(id1)
			
		if ((id1 in self.shipDic) and (id2 in self.laserDic)):
			#print "Collision ship / laser!"
			#exploSound1 = audio3d.loadSfx("sounds/space/explosion01.ogg")
			audio3d.attachSoundToObject(exploSound1, self.shipDic[id1].model)
			exploSound1.play()
			coqueDmg = self.laserDic[id2].gunData.coqueDmg
			shieldDmg = self.laserDic[id2].gunData.shieldDmg
			self.shipDic[id1].data.remShieldHP(shieldDmg)
			if self.shipDic[id1].data.shieldHP <= 0.0:
				self.shipDic[id1].data.remCoqueHP(coqueDmg)
			self.destroyLaser(id2)
		
		elif ((id2 in self.shipDic) and (id1 in self.laserDic)):
			#print "Collision laser / ship!"
			#exploSound1 = audio3d.loadSfx("sounds/space/explosion01.ogg")
			audio3d.attachSoundToObject(exploSound1, self.shipDic[id2].model)
			exploSound1.play()
			coqueDmg = self.laserDic[id1].gunData.coqueDmg
			shieldDmg = self.laserDic[id1].gunData.shieldDmg
			self.shipDic[id2].data.remShieldHP(shieldDmg)
			if self.shipDic[id2].data.shieldHP <= 0.0:
				self.shipDic[id2].data.remCoqueHP(coqueDmg)
			self.destroyLaser(id1)
			
		
	
	def selectClick(self):
		if self.picker.targetGeomId != None:
			#print "Selecting geom"
			if self.picker.targetGeomId in self.shipDic:
				self.radar.setTarget(
					self.picker.targetGeomId,
					self.shipDic[self.picker.targetGeomId].model,
					self.shipDic[self.picker.targetGeomId].name,
					"ship")
					
			elif self.picker.targetGeomId in self.lootDic:
				self.radar.setTarget(
					self.picker.targetGeomId,
					self.lootDic[self.picker.targetGeomId].model,
					self.lootDic[self.picker.targetGeomId].name,
					"loot")
					
			elif self.picker.targetGeomId in self.baseDic:
				self.radar.setTarget(
					self.picker.targetGeomId,
					self.baseDic[self.picker.targetGeomId].model,
					self.baseDic[self.picker.targetGeomId].name,
					"base")
				
		self.shoot()
		
	def shoot(self, dt=1.0/75.0):
		targetPos = self.picker.crosshairModel.getPos(render)
		for loot in self.lootList:
			direction = targetPos - loot.model.getPos()
			loot.body.addForce(direction)
		for ship in self.shipList:
			ship.steerToPoint(targetPos, dt)
			ship.shootLasers(targetPos)
			
	def shoot2(self):
		targetPos = self.picker.crosshairModel.getPos(render)
		for loot in self.lootList:
			direction = -targetPos + loot.model.getPos()
			loot.body.addForce(direction*10)
	
	#-------------------------------------------------------------------
	# base handling
	#-------------------------------------------------------------------
	def addBase(self, name):
		if name in spaceBaseDb:
			spacebase = OdeBase(self, name)
			spacebaseId = spacebase.getId()
			self.baseList.append(spacebase)
			self.baseDic[spacebaseId] = spacebase
		
	def destroyBase(self, id):
		self.baseDic[id].destroy()
		self.baseList.remove(self.baseDic[id])
		del self.baseDic[id]
		
	#-------------------------------------------------------------------
	# laser handling
	#-------------------------------------------------------------------
	def shootLaser(self, originPos, targetPos, shipSpeed, gunData):
		#laser = Laser(self, originPos, targetPos, speed, shipSpeed, lifeTime)
		laser = Laser(self, originPos, targetPos, shipSpeed, gunData)
		laser.model.show(BitMask32.bit(1))
		self.laserList.append(laser)
		self.laserDic[laser.getId()] = laser
		#laserSounds["slimeball"].play() # deprecated, laser now plays its own sound on init
		
	def updateLasers(self, dt):
		for laser in self.laserList:
			laser.update(dt)
			if not laser.alive:
				self.laserList.remove(laser)
				del self.laserDic[laser.getId()]
				del laser
				
	def destroyLaser(self, id):
		self.laserDic[id].destroy()
		self.laserList.remove(self.laserDic[id])
		del self.laserDic[id]
	
	#-------------------------------------------------------------------
	# loot handling
	#-------------------------------------------------------------------
	def updateLoot(self, dt):
		for loot in self.lootList:
			loot.update(dt)
	
	def destroyLoot(self, geomId):
		self.lootList.remove(self.lootDic[geomId])
		self.lootDic[geomId].destroy()
		del self.lootDic[geomId]
	#-------------------------------------------------------------------
	# ship handling
	#-------------------------------------------------------------------
	def spawnShip(self):
		NPCShip = Ship(self, shipDb["npc"].makeCopy())
		NPCShip.geom.setCollideBits(odeBitMask["npc"])
		NPCShip.geom.setCategoryBits(odeBitMask["npc"])
		
		#shipModels["sabreNew"].instanceTo(NPCShip.model)
		NPCShip.setPos((-8,15,45))
		#NPCShip.data.setGun(0, gunDb["laser1"])
		#NPCShip.data.setGun(1, gunDb["laser3"])
		#NPCShip.initGuns() # already called in Ship.__init__, but called again here to update the equipped guns
		
		
		self.shipList.append(NPCShip)
		self.shipDic[NPCShip.getId()] = NPCShip
		#print "Adding ship, we now have %s ships in space" % (len(self.shipList))
		
	def updateShips(self, dt):
		for ship in self.shipList:
			ship.update(dt)
	
	def destroyShip(self, geomId):
		self.shipDic[geomId].destroy()
		self.shipList.remove(self.shipDic[geomId])
		#self.shipDic[geomId].destroy()
		del self.shipDic[geomId]
		#print "Destroyed ship, we now have %s ships in space" % (len(self.shipList))
		
	def setMode(self, mode):
		self.mode = str(mode)
		self.camHandler.mode = self.mode
		#if self.mode == "manual" or self.mode == "auto":
		#	self.camCube.body.setPosition(self.wm.ship.model.getPos()+(Point3(0,-20, 3)))
			
		
	def toggleMode(self):
		if self.mode == "auto":
			self.mode = "manual"
		elif self.mode == "manual":
			self.mode = "turret"
		else:
			self.mode = "auto"
			
		self.camHandler.mode = self.mode
		
	
		
	'''
	# this function is used if space.collide is used instead of autoCollide
	def handleCollisions(self, arg, geom1, geom2):
		entry = OdeUtil.collide(geom1, geom2)
		if entry.isEmpty():
			return
	'''
	
	#-------------------------------------------------------------------
	# World Task!
	#-------------------------------------------------------------------	
	def worldTask(self, task):
		
		dt = globalClock.getDt()
		
		self.NPCTimer += dt
		
		
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			dx = mpos.getX()
			dy = mpos.getY()
		else:
			mpos = None
			dx = 0
			dy = 0
		
		if mpos:
			self.picker.update(mpos)
		self.radar.update()
		
		#self.refireTimer += dt
			
		self.shipSpeed = self.ship.body.getLinearVel()
		self.currentSpeed = self.shipSpeed.length()
		self.PE.speed = self.currentSpeed
		#self.PE.draw(self.currentSpeed)
		
		
		dx = min(dx, 1.0)
		dx = max(dx, -1.0)
		
		dy = min(dy, 1.0)
		dy = max(dy, -1.0)
		
		if self.mode == "manual":
			self.ship.steer(dx, dy, dt*100)
		elif self.mode == "auto":
			self.ship.steer(0, 0, dt*100)
			#self.ship.setAngMotor3(-self.ship.model.getR()/20)
			self.ship.autoCorrectHpr()
		else:
			self.ship.setAngMotor1(0)
			self.ship.setAngMotor2(0)
			self.ship.setAngMotor3(0)
			
		# speed control
		if self.keyMap["z"]:
			self.ship.accelerate(dt)
			#self.ship.setLinMotor(self.ship.pushSpeed)
		elif self.keyMap["s"]:
			self.ship.decelerate(dt)
			#self.ship.setLinMotor(-self.ship.pushSpeed)
		else:
			self.ship.rest()
			
		# roll
		if self.keyMap["d"]:
			#self.ship.setAngMotor3(self.ship.steerRSpeed)
			self.ship.roll(self.ship.steerRMaxSpeed, dt*100)
		elif self.keyMap["q"]:
			self.ship.roll(self.ship.steerRMaxSpeed, -dt*100)
			#self.ship.setAngMotor3(-self.ship.steerRSpeed)
			#self.stopAngMotor3()
		else:
			if self.mode == "manual":
				self.ship.setAngMotor3(0)
			
		if self.keyMap["mouse3"]:
			self.ship.shootLasers(self.picker.crosshairModel.getPos())
		
		if self.keyMap["mouse1"]:
			self.shoot(dt)
		
		
		
		#self.space.collide("", self.handleCollisions)
		self.space.autoCollide()
		
		'''
		self.dtCumul += dt
		while self.dtCumul > self.stepSize:
			# Remove a stepSize from the accumulator until
			# the accumulated time is less than the stepsize
			self.dtCumul -= self.stepSize
			# Step the simulation
			self.world.quickStep(self.stepSize)
		'''
		self.world.quickStep(dt)
		
		self.contactGroup.empty()
		
		self.updateLoot(dt)
		self.updateLasers(dt)
		self.updateShips(dt)
		
		self.ship.update(dt)
		
		self.gui.laserHP.setVal(self.ship.data.gunHP)
		self.gui.shieldHP.setVal(self.ship.data.shieldHP)
		self.gui.coqueHP.setVal(self.ship.data.coqueHP)
		
		#---------------------------------------------------------------
		# speed message
		l = round(self.currentSpeed, 2)
		self.gui.setSpeed(l)
		
		#---------------------------------------------------------------
		# cam handling
		self.camHandler.update(dx, dy)
		
		return task.cont

"""

wm = SpaceOdeWorldManager()
wm.spawnShip()

exiter = DirectObject()
exiter.accept("escape", sys.exit)


base.setFrameRateMeter(True)
base.setBackgroundColor(0,0,0)

base.disableMouse()



bgMusic1 = loader.loadSfx("sounds/MUSIC/music_br_space.wav")
bgMusic1.setLoop(True)
bgMusic1.setVolume(0.6)
bgMusic1.play()


L = LightManager()
L.lightCenter.reparentTo(wm.ship.model)
#L.setPos(Vec3(0,-40,-10))

render.setShaderAuto()
#render.setShaderOff()

render.setAntialias(AntialiasAttrib.MMultisample)

base.setFrameRateMeter(True)
base.camLens.setNearFar(1,100000)
base.camLens.setFov(60)



barreLaser = SpaceBarre(2,(0.94,0.87,0.1))
barreShield = SpaceBarre(1,(0.3,0.45,0.9))
barreCoque = SpaceBarre(0,(1.0,0.3,0.1))

"""


"""
def makeFilterBuffer(srcbuffer, name, sort, prog):
	blurBuffer=base.win.makeTextureBuffer(name, 512, 512)
	
	blurBuffer.setSort(sort)
	blurBuffer.setClearColor(Vec4(0,0,0,1))
	blurCamera=base.makeCamera2d(blurBuffer)
	#blurCamera.node().setCameraMask(BitMask32.bit(1))
	blurScene=NodePath("new Scene")
	blurCamera.node().setScene(blurScene)
	shader = loader.loadShader(prog)
	card = srcbuffer.getTextureCard()
	card.reparentTo(blurScene)
	card.setShader(shader)
	return blurBuffer


'''
tempnode = NodePath(PandaNode("temp node"))
tempnode.setShader(loader.loadShader("shaders/lightingGen.sha"))
base.cam.node().setInitialState(tempnode.getState())
'''

base.cam.node().setCameraMask(BitMask32.bit(0))
#render.show(BitMask32.bit(0))
#render.hide(BitMask32.bit(1))


viewTex = Texture('ViewTex')
glowBuffer = base.win.makeTextureBuffer('glowBuffer', 512, 512, viewTex, True)
#glowBuffer=base.win.makeTextureBuffer("glowBuffer", 512, 512)
glowBuffer.setClearColor(Vec4(0.0,0.0,0.0,1))
glowBuffer.setClearColorActive(True)
#glowBuffer.setClearColor(base.win.getClearColor()) 
glowBuffer.setSort(-3)

glowCamera=base.makeCamera(glowBuffer, lens=base.cam.node().getLens())
glowCamera.node().setCameraMask(BitMask32.bit(1))

tempnode = NodePath(PandaNode("temp node"))
tempnode.setShader(loader.loadShader("shaders/glowShader.sha"))
#tempnode.setShader(loader.loadShader("shaders/lightingGen.sha"))
glowCamera.node().setInitialState(tempnode.getState())
glowCamera.node().setScene(render)
wm.ship.model.show(BitMask32.bit(0))
wm.ship.model.hide(BitMask32.bit(1))

blurXBuffer=makeFilterBuffer(glowBuffer,  "Blur X", -2, "shaders/XBlurShader.sha")
blurYBuffer=makeFilterBuffer(blurXBuffer, "Blur Y", -1, "shaders/YBlurShader.sha")

laserCard = blurYBuffer.getTextureCard()
laserCard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
#laserCard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.OIncomingColorSaturate))
laserCard.reparentTo(render2d)
'''
base.bufferViewer.setPosition("llcorner")
base.bufferViewer.setLayout("hline")
base.bufferViewer.setCardSize(0.652,0)

base.bufferViewer.toggleEnable()
'''
"""

'''
manager = FilterManager(base.win, base.cam)
tex = Texture()
quad = manager.renderSceneInto(colortex=tex)
quad.setShader(Shader.load("shaders/post.sha"))
quad.setShaderInput("tex", tex)
'''

#run()
