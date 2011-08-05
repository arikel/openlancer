#!/usr/bin/python
# -*- coding: utf8 -*-

import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.interval.IntervalGlobal import *

#import psyco
#psyco.full()

import sys
from random import random, seed
from math import *


	
def randVec():
	tmpVec = Vec3(random()-.5,random()-.5,random()-.5)
	#tmpVec.normalize()
	return tmpVec

class AriParticle:
	# particle used for stardust cloud around camera, to simulate
	# movement in space
	def __init__(self, originPos, ray, move = False):
		self.originPos = originPos # Vec3
		self.ray = ray # float
		self.diam = 2*self.ray
		self.move = move
		self.x = (2*random()-1)*self.ray
		self.y = (2*random()-1)*self.ray
		self.z = (2*random()-1)*self.ray
		
		#self.pos = Vec3(self.originPos)+randVec()*self.ray*random()/2
		self.pos = Vec3(self.x, self.y, self.z)
		
		self.frame = 1
		
		#self.size = random()*0.2 + 0.02
		self.size = random()*0.2 + 1.2
		self.color = Vec4(random()/2.0 + 0.5,random()/4.0 + 0.75,random()/4.0 + 0.75,1)
		
		self.moveVec = randVec() * 0.01 # + Vec3(0,0,0.02)
		
	def setOriginPos(self, originPos):
		self.originPos = originPos
		dx = self.x - originPos[0]
		dy = self.y - originPos[1]
		dz = self.z - originPos[2]
		
		if dx>self.ray:
			self.x = self.x - self.diam
			#print "particle out, X axis +"
		elif dx < -self.ray:
			self.x = self.x + self.diam
			#print "particle out, X axis -"
		if dy>self.ray:
			self.y = self.y - self.diam
			#print "particle out, Y axis +"
		elif dy < -self.ray:
			self.y = self.y + self.diam
			#print "particle out, Y axis -"
			
		if dz>self.ray:
			self.z = self.z - self.diam
			#print "particle out, Z axis +"
		elif dz < -self.ray:
			self.z = self.z + self.diam
			#print "particle out, Z axis -"
		
		if self.move:
			self.x += self.moveVec[0]
			self.y += self.moveVec[1]
			self.z += self.moveVec[2]
		self.pos = Vec3(self.x, self.y, self.z)
		
			
		
				
class ParticleEngine:
	# particle engine used for stardust cloud around camera, to simulate
	# movement in space
	def __init__(self, model, nb=600, ray=20.0, move = False):
		self.np = model
		self.pos = self.np.getPos()
		
		self.ray = ray
		#self.pos = Vec3(pos) # a Vec3
		self.move = move
		maxParticles = 5000 # max number of particle (1000) triangles we will display
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setPlateSize(1)
		#self.generator.setClip(0,0,1,1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		self.generatorNode.setTwoSided(True)
		self.generatorNode.setTexture(loader.loadTexture("img/particles/stardust.png"))
		#self.generatorNode.setTexture(loader.loadTexture("img/particles/spark.png"))
		self.generatorNode.setBin("fixed",0)
		self.generatorNode.setLightOff(True)
		self.generatorNode.setShaderOff(True)
		
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000*self.ray))
		self.generatorNode.node().setFinal(True)
		seed()
		self.particles = []
		minDist = 10000
		maxDist = -1
		totalDist = 0
		
		for i in range(nb):
			p = AriParticle(self.pos, self.ray, self.move)
			self.particles.append(p)
			dist = Vec3(self.pos - p.pos).length()
			if dist < minDist:
				minDist = dist
			if dist > maxDist:
				maxDist = dist
			totalDist += dist
		moyDist = totalDist/nb
		#print "ParticleEngine generated, minDist = %s, maxDist = %s, averageDist = %s" % (minDist, maxDist, moyDist)
		
		'''
		# create 100 random lines
		lines = []
		for i in range(100):
			l = [randVec()*100,randVec()*100,187,.1,Vec4(random(),random(),random(),1)]
			lines.append(l)
		'''
		
		self.speed = 0.0
		
		self.start()
		
	def setPos(self, pos):
		self.pos = pos
		
	def start(self):
		if (not(taskMgr.hasTaskNamed("drawStarDust"))):
			taskMgr.add(self.drawTask, "drawStarDust")
		self.generatorNode.reparentTo(render)
		
	def stop(self):
		if (taskMgr.hasTaskNamed("drawStarDust")):
			taskMgr.remove("drawStarDust")
		self.generatorNode.detachNode()
		
		
	def drawTask(self, task):
		""" this is called every frame to regen the mesh """
		#t = globalClock.getFrameTime()
		self.pos = self.np.getPos()
		self.generator.begin(base.cam,render)
		#for pos,frame,size,color in self.particles:
		for p in self.particles:
			p.setOriginPos(self.pos)
			#print "Position origine : %s" % (self.pos)
			#self.generator.billboard(p.pos,p.frame,p.size,p.color)
			direction = render.getRelativeVector(self.np, (0,self.speed/10.0,0))
			alpha = min(self.speed/100.0, 1)
			#direction = Vec3(direction)
			self.generator.segment(p.pos,p.pos+direction,1,0.5,Vec4(1,1,1,alpha))
		
		'''
		for start,stop,frame,size,color in lines:
			generator.segment(start,stop,frame,size*sin(t*2)+2,color)
		'''
		self.generator.end()
		return Task.cont
		
	def draw(self, speed):
		self.pos = self.np.getPos()
		self.generator.begin(base.cam,render)
		for p in self.particles:
			p.setOriginPos(self.pos)
			#direction = render.getRelativeVector(self.np, (0,speed/5.0,0))
			#direction = Vec3(0,speed,0)
			#self.generator.segment(p.pos,p.pos+direction,1,0.5,Vec4(1,1,1,1))
			self.generator.billboard(p.pos,1,p.size,p.color)
		self.generator.end()
		
		
	def destroy(self):
		self.stop()
		self.particles = []
		self.generatorNode.removeNode()







class WarpParticle:
	# particle used for warp sphere
	def __init__(self, parentNp, ray=2, out = False):
		self.out = out
		self.parentNp = parentNp
		#self.np = np # nodepath
		self.ray = ray # float
		
		tmpVec = randVec()
		self.np = self.parentNp.attachNewNode("np")
		
		if self.out:
			#self.pos = self.originPos + tmpVec*self.ray/tmpVec.length()
			
			self.np.setPos(tmpVec*self.ray/tmpVec.length())
			#print self.pos
		else:
			self.np.setPos(tmpVec*self.ray)
		
		self.frame = 1
		
		self.size = random()*0.2 + 0.08
		self.color = Vec4(random()/2.0 + 0.5,random()/4.0 + 0.75,random()/4.0 + 0.75,1)
		
	def setPos(self, pos):
		self.np.setPos(pos)
		
	def getPos(self):
		return Vec3(self.np.getPos(render))
		
		
class WarpParticleEngine:
	def __init__(self, pos, nb=100, ray=2.0, rot = 0):
		
		self.ray = ray
		self.rot = rot
		self.pos = Vec3(pos) # a Vec3
		self.np = render.attachNewNode("warp")
		self.np.setPos(pos)
		
		maxParticles = 5000 # max number of particle (1000) triangles we will display
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setPlateSize(1)
		#self.generator.setClip(0,0,1,1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		self.generatorNode.setTwoSided(True)
		self.generatorNode.setTexture(loader.loadTexture("img/particles/stardust.png"))
		self.generatorNode.setBin("fixed",0)
		
		self.generatorNode.setLightOff(True)
		self.generatorNode.setShaderOff(True)
		
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000*self.ray))
		self.generatorNode.node().setFinal(True)
		
		self.particles = []
		minDist = 10000
		maxDist = -1
		totalDist = 0
		
		for i in range(nb):
			p = WarpParticle(self.np, self.ray, out = True)
			self.particles.append(p)
			p = WarpParticle(self.np, self.ray)
			self.particles.append(p)
			
		self.startDraw()
		
	def setPos(self, pos):
		self.pos = pos
		
	def startDraw(self):
		#if (not(taskMgr.hasTaskNamed("drawWarp"))):
		self.generatorNode.reparentTo(render)
		taskMgr.add(self.drawTask, "drawWarp")
		
			
	def stopDraw(self):
		if (taskMgr.hasTaskNamed("drawWarp")):
			taskMgr.remove("drawWarp")
		self.np.detachNode()
		self.generatorNode.detachNode()
		
	def drawTask(self, task):
		""" this is called every frame to regen the mesh """
		#dt = globalClock.getFrameTime()
		dt = globalClock.getDt()
		self.np.setH(self.np.getH()+self.rot*dt)
		self.generator.begin(base.cam,render)
		#for pos,frame,size,color in self.particles:
		for p in self.particles:
			#p.setPos(self.pos)
			#print "Position origine : %s" % (self.pos)
			
			self.generator.billboard(p.getPos(),p.frame,p.size,p.color)
			#print "drawing particle in : %s" % (p.pos)
		#self.generator.segment(Vec3(0,0,10),Vec3(self.pos),1,sin(t*20)*0.2+0.5,Vec4(0,0,1,1))
		
		'''
		for start,stop,frame,size,color in lines:
			generator.segment(start,stop,frame,size*sin(t*2)+2,color)
		'''
		self.generator.end()
		return Task.cont
		
	def destroy(self):
		self.stopDraw()
		self.particles = []







class RingParticle:
	# particle used for warp sphere
	def __init__(self, parentNp, ray=2):
		self.parentNp = parentNp
		#self.np = np # nodepath
		self.ray = ray # float
		
		tmpVec = randVec()
		tmpVec[1] = 0
		self.np = self.parentNp.attachNewNode("np")
		
			
		self.np.setPos(tmpVec*self.ray/tmpVec.length())
			#print self.pos
		
		self.frame = 1
		
		self.size = random()*0.2 + 0.08
		self.color = Vec4(random()/2.0 + 0.5,random()/4.0 + 0.75,random()/4.0 + 0.75,1)
		
	def setPos(self, pos):
		self.np.setPos(pos)
		
	def getPos(self):
		return Vec3(self.np.getPos(render))
		
		
class RingParticleEngine:
	def __init__(self, pos, nb=100, ray=2.0, rot = 0, dec=0):
		self.dec = dec
		self.ray = ray
		self.rot = rot
		self.pos = Vec3(pos) # a Vec3
		self.np = render.attachNewNode("warp")
		self.np.setPos(pos)
		
		maxParticles = 5000 # max number of particle (1000) triangles we will display
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setPlateSize(1)
		#self.generator.setClip(0,0,1,1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		self.generatorNode.setTwoSided(True)
		self.generatorNode.setTexture(loader.loadTexture("img/particles/stardust.png"))
		self.generatorNode.setBin("fixed",0)
		
		self.generatorNode.setLightOff(True)
		self.generatorNode.setShaderOff(True)
		
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000*self.ray))
		self.generatorNode.node().setFinal(True)
		
		self.particles = []
		minDist = 10000
		maxDist = -1
		totalDist = 0
		
		for i in range(nb):
			p = RingParticle(self.np, self.ray)
			self.particles.append(p)
			
		self.startDraw()
		
	def setPos(self, pos):
		self.pos = pos
		
	def startDraw(self):
		#if (not(taskMgr.hasTaskNamed("drawWarp"))):
		self.generatorNode.reparentTo(render)
		taskMgr.add(self.drawTask, "drawWarp")
		
			
	def stopDraw(self):
		if (taskMgr.hasTaskNamed("drawWarp")):
			taskMgr.remove("drawWarp")
		self.np.detachNode()
		self.generatorNode.detachNode()
		
	def drawTask(self, task):
		""" this is called every frame to regen the mesh """
		ft = globalClock.getFrameTime()
		
		dt = globalClock.getDt()
		self.np.setR(self.np.getR()+self.rot*dt)
		self.generator.begin(base.cam,render)
		#for pos,frame,size,color in self.particles:
		for p in self.particles:
			#p.setPos(self.pos)
			#print "Position origine : %s" % (self.pos)
			fac = (sin(5*(ft+self.dec))+1.1)*2
			p.np.setP(self.np, p.np.getP()+self.rot*dt*2*random())
			self.generator.billboard(p.getPos(),p.frame,p.size*fac,p.color)
			#print "drawing particle in : %s" % (p.pos)
		#self.generator.segment(Vec3(0,0,10),Vec3(self.pos),1,sin(t*20)*0.2+0.5,Vec4(0,0,1,1))
		
		'''
		for start,stop,frame,size,color in lines:
			generator.segment(start,stop,frame,size*sin(t*2)+2,color)
		'''
		self.generator.end()
		return Task.cont
		
	def destroy(self):
		self.stopDraw()
		self.particles = []


class Trail():
	def __init__(self,parent,hi,len,col,step):
		self.parent=parent
		#trail len
		self.nr=len+1   
		self.col=col
		self.step=step
		self.do=globalClock.getFrameTime()
	   
		#attrib
		self.tfade=True
		self.afade=True
		self.tex=True

		#vert data
		self.vdata = GeomVertexData('name',GeomVertexFormat.getV3c4t2(),Geom.UHDynamic)
	   
		#writers
		self.vertex = GeomVertexWriter(self.vdata, 'vertex')	   
		self.color = GeomVertexWriter(self.vdata, 'color')
		self.texcoord=GeomVertexWriter(self.vdata,'texcoord')
	   
		#trail height step
		self.dim=1.0/(self.nr<<1)
		
		for i in range(self.nr<<1):
			#alpha=1.0/(i+1)				   
			alpha=1
			#self.color.addData4f(col[0],col[1],col[2],alpha)		   
			#self.color.addData4f(col[0],col[1],col[2],alpha)
			self.color.addData4f(1,1,1,alpha)
			self.color.addData4f(1,1,1,alpha)
			self.texcoord.addData2f(i*self.dim*2,1)		   
			self.texcoord.addData2f(i*self.dim*2,0)		   
 
		#create prim
		prim = GeomTristrips(Geom.UHDynamic)
		for i in range(self.nr<<1):
			prim.addVertex(i)
		prim.closePrimitive()

		#geom
		self.geom=Geom(self.vdata)
		self.geom.addPrimitive(prim)
		self.geom.doublesideInPlace()	   
				 
		self.node=GeomNode('gnode')
		self.node.addGeom(self.geom)
		self.node.setBounds(OmniBoundingVolume())
		self.node.setFinal(True)
	   
		self.nodep = render.attachNewNode(self.node)	   
		self.nodep.setTransparency(TransparencyAttrib.MDual)
		#self.nodep.setColor(1,0,0)
		#self.nodep.setTexture(texture)
		#pos root
		self.root=self.parent.attachNewNode('root')
			   
		#p dif is height
		self.p1=self.root.attachNewNode('p1')
		self.p1.setZ(hi*0.5)
	   
		self.p2=self.root.attachNewNode('p2')
		self.p2.setZ(-hi*0.5)
	   
		   
		#trail poses
		self.trpos=[]
		pos=[self.p1.getPos(),self.p2.getPos()]
	   
		for i in range(self.nr):
			self.trpos.append((pos))
		
		self.color = GeomVertexWriter(self.vdata, 'color')
		col=self.col
		for i in range(self.nr<<1):
			if self.afade:					
				alpha=1.0/(i+1)				 
			else:
				alpha=1
			   
				#tr.color.addData4f(col[0],col[1],col[2],alpha)		   
				#tr.color.addData4f(col[0],col[1],col[2],alpha)
			self.color.addData4f(1,1,1,alpha)
			self.color.addData4f(1,1,1,alpha)
				
		taskMgr.add(self.run, "trailerPE task")
		
	def run(self, task):
		'''
		if globalClock.getFrameTime()-self.do>self.step:
			self.do=globalClock.getFrameTime()
				   
			self.trpos.pop()
	   
			self.trpos.insert(0,[self.p1.getPos(render),self.p2.getPos(render)])
		else:
			self.trpos[0]=[self.p1.getPos(render),self.p2.getPos(render)]
		'''
		
		#self.trpos.pop()
		#self.trpos.insert(0,[self.p1.getPos(render),self.p2.getPos(render)])
		
		#self.trpos[0]=[self.p1.getPos(render),self.p2.getPos(render)]
		
		pos = GeomVertexWriter(self.vdata, 'vertex')
		for i in range(self.nr):
		   
			npos=self.root.getPos(render)
			xr,yr,zr=self.root.getPos()
			x1,y1,z1=self.trpos[i][0]
			x2,y2,z2=self.trpos[i][1]
			xx=x1-x2
			yy=y1-y2
			zz=z1-z2

			xdim=self.dim*i*xx
			ydim=self.dim*i*yy
			zdim=self.dim*i*zz
		   
			if not self.tfade:
				xdim=0
				ydim=0
				zdim=0
		   
			pos.setData3f(x1-xdim,y1-ydim,z1-zdim)
			pos.setData3f(x2+xdim,y2+ydim,z2+zdim)
		return Task.cont

class AriTrail:
	def __init__(self, np, nb = 20, delay = 0.03):
		if nb < 3:
			nb = 3
		self.parentNp = np
		self.nb = nb
		self.delay = delay
		self.pos = []
		self.do=globalClock.getFrameTime()
		#self.np = render.attachNewNode("trail")
		#self.np.setPos(pos)
		
		maxParticles = 500
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setClip(0,0,1,1)
		#self.generator.setPlateSize(1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		self.generatorNode.setTwoSided(True)
		self.generatorNode.setTexture(loader.loadTexture("img/particles/white.png"))
		#self.generatorNode.setTexture(loader.loadTexture("img/particles/white2.png"))
		self.generatorNode.setBin("fixed",0)
		self.generatorNode.setLightOff(True)
		self.generatorNode.setShaderOff(True)
		
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000000000000000000000000))
		self.generatorNode.node().setFinal(True)
		
		for n in range(self.nb):
			self.pos.append(Vec3(self.parentNp.getPos(render)))
			

		
		#self.start()
		self.stop()
		

		
	def start(self):
		#if (not(taskMgr.hasTaskNamed("drawWarp"))):
		self.generatorNode.reparentTo(render)
		taskMgr.add(self.drawTask, "drawTrail")
		
			
	def stop(self):
		if (taskMgr.hasTaskNamed("drawTrail")):
			taskMgr.remove("drawTrail")
		#self.np.detachNode()
		#self.generator.begin(base.cam,render)
		#self.generator.end()
		self.generatorNode.detachNode()
		
	def drawTask(self, task):
		dt = globalClock.getFrameTime()
		#dt = globalClock.getDt()
		if dt-self.do>self.delay:
			self.do = dt
			newPos = Vec3(self.parentNp.getPos(render))
			self.pos.pop()
			self.pos.insert(0, newPos)
		
		#print "NewPos : %s" % (newPos)
		#self.np.setH(self.np.getH()+self.rot*dt)
		self.generator.begin(base.cam,render)
		#for pos,frame,size,color in self.particles:
		nbPos = len(self.pos)-1
		for n in range(nbPos):
			fac = (nbPos-float(n))/nbPos
			#fac = (nbPos-n)/nbPos
			self.generator.linkSegment(self.pos[n],1,fac*0.20,Vec4(1,1,1,fac*1.0))
		self.generator.linkSegmentEnd(1,Vec4(1,1,1,0))
		self.generator.end()
		
		'''
		for start,stop,frame,size,color in lines:
			generator.segment(start,stop,frame,size*sin(t*2)+2,color)
		'''
		
		return Task.cont
		
	def destroy(self):
		self.stopDraw()
		self.particles = []
		self.generatorNode.removeNode()
		

class AriTrail2:
	def __init__(self, np, nb = 20, delay = 0.03):
		if nb < 3:
			nb = 3
		self.parentNp = np
		#self.np = render.attachNewNode("np")
		self.nb = nb
		self.delay = delay
		self.pos = []
		self.do=globalClock.getFrameTime()
		maxParticles = 500
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setPlateSize(1)
		#self.generator.setClip(0,0,1,1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		self.generatorNode.setTwoSided(True)
		self.generatorNode.setTexture(loader.loadTexture("img/particles/white_a.png"))
		self.generatorNode.setBin("fixed",0)
		self.generatorNode.setLightOff(True)
		
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000))
		self.generatorNode.node().setFinal(True)
		
		for n in range(self.nb):
			self.pos.append(Vec3(self.parentNp.getPos(render)))
				
		self.startDraw()
		

		
	def startDraw(self):
		#if (not(taskMgr.hasTaskNamed("drawTrail"))):
		self.generatorNode.reparentTo(render)
		taskMgr.add(self.drawTask, "drawTrail")
		
			
	def stopDraw(self):
		if (taskMgr.hasTaskNamed("drawTrail")):
			taskMgr.remove("drawTrail")
		self.generatorNode.detachNode()
		
	def drawTask(self, task):
		dt = globalClock.getFrameTime()
		#dt = globalClock.getDt()
		if dt-self.do>self.delay:
			self.do = dt
			newPos = Vec3(self.parentNp.getPos())
			self.pos.pop()
			self.pos.insert(0, newPos)
		#self.np.setPos(self.parentNp.getPos())
		#print "HPR = ", self.generatorNode.getHpr()
		self.generator.begin(base.cam,render)
		nbPos = len(self.pos)-1
		for n in range(nbPos):
			fac = (nbPos-float(n))/nbPos
			self.generator.linkSegment(self.pos[n],1,fac*0.5,Vec4(1,1,1,fac*0.8))
		self.generator.linkSegmentEnd(1,Vec4(1,1,1,0))
		self.generator.end()
		return Task.cont
		
	def destroy(self):
		self.stopDraw()
		self.particles = []
