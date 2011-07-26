#!/usr/bin/python
# -*- coding: utf8 -*-

from guiBasics import makeImg


class CargoBarre:
	def __init__(self, x, y, color=(1.0,0.3,0.1,1), maxVal=0):
		self.color = color
		self.x = x
		self.y = y
		self.maxVal = float(maxVal)
		self.scale = 0.008
		self.step = 0.022
		self.images = []
		
		for i in range(16):
			img = makeImg(self.x+self.step*i, self.y, "img/gui/white.png", self.scale)
			img.setColor(self.color[0], self.color[1], self.color[2])
			self.images.append(img)
		
		
	def scaleImage(self, n, scale):
		self.images[n].setScale(scale*self.scale, 0, self.scale)
		self.images[n].setPos(self.x+self.step*n - self.scale*(1-scale), 0, self.y)
	
	def set(self, val):
		self.show()
		
		if val>self.maxVal:val = self.maxVal
		entiers = int(val*16/self.maxVal)
		decim = val*16/self.maxVal - entiers
		
		for i in range(entiers):
			self.scaleImage(i, 1)
			
		if entiers <= 15:
			self.scaleImage(entiers, decim)
			entiers += 1
			while entiers <=15:
				self.images[entiers].hide()
				entiers += 1
				
	def hide(self):
		for img in self.images:img.hide()
		
	def show(self):
		for img in self.images:img.show()
	
	def destroy(self):
		for img in self.images:img.destroy()
	
class SpaceBarre:
	def __init__(self, pos = 0, color=(1.0,0.3,0.1,1), maxVal=0):
		#self.W = base.win.getXSize()
		#self.H = base.win.getYSize()
		self.H = 600.0
		self.color = color
		self.x = -160.0/self.H
		self.maxVal = 0
		
		if pos == 0:
			self.y = -1+30.0/self.H
		elif pos == 1:
			self.y = -1+50.0/self.H
		else:
			self.y = -1+70.0/self.H
		
		self.images = []
		
		for i in range(16):
			img = makeImg(self.x+20.0/self.H*i, self.y, "img/gui/white.png", 8.0/self.H)
			img.setColor(self.color[0], self.color[1], self.color[2])
			self.images.append(img)
			
	def setVal(self, val):
		if val > self.maxVal: val = self.maxVal
		if val < 0: val = 0
		
	def setMaxVal(self, val):
		self.maxVal = val
		
	def scaleImage(self, n, scale):
		self.images[n].setScale(8.0*scale/self.H, 0, 8.0/self.H)
		self.images[n].setPos(self.x+20.0/self.H*n - 8.0*(1-scale)/self.H, 0, self.y)
		
	def hide(self):
		for img in self.images:
			img.hide()
			
	def show(self):
		for img in self.images:
			img.show()
		
	def destroy(self):
		for img in self.images:
			img.destroy()
#-------------------------------------------------------------------------------
# Barre
#-------------------------------------------------------------------------------
class Barre:
	"""
	(x=0, y=0, n=0, nmax=30, color="red", sens="H", hmax = 0.21)
	"""
	def __init__(self, x=0, y=0, n=0, nmax=30, color="red", sens="H", hmax = 0.21):
		"""
		(x=0, y=0, n=0, nmax=30, color="red", sens="H", hmax = 0.21)
		Une classe pour les barres des hp/ep/mp et celles des food/water.
		
		"""
		self.x = x
		self.y = y
		self.ypos = 0
		self.scale = (0.1, 1, 0.1)
		
		self.n = n
		self.nmax = nmax
		self.hmax = hmax
		
		self.h = 0
		
		self.path =  "img/gui/" + color + ".png"
		
		self.sens = sens
		if self.sens == "H": # barre horizontale
			self.scale = (1.0/10, 1, 1.0/60)
		if self.sens == "V": # barre verticale
			self.scale = (1.0/60, 1, 1.0/10)
		self.img = None
		
	def clear(self):
		try:
			self.img.destroy()
		except:
			pass
			
	def set(self):
		if self.sens == "V":
			self.h = self.n * self.hmax / self.nmax
			self.ypos = self.h / 2 + self.y
			self.scale = (1.0/100, 1, self.h/2)
		if self.sens == "H":
			self.h = self.n * self.hmax / self.nmax
			self.ypos = self.h / 2 + self.x
			self.scale = (self.h/2, 1, 1.0/100)	
			
			#print "x=%s, y=%s, ypos=%s, n=%s, nmax=%s, h=%s, hmax=%s, scale=%s" % (self.x, self.y, self.ypos, self.n, self.nmax, self.h, self.hmax, str(self.scale))
		
	def show(self, n=None, nmax=None):
		if nmax!=None:
			self.nmax = nmax
		if n!=None:
			self.n = n
		if self.n > self.nmax:
			self.n = self.nmax
			
		self.set()
		self.clear()
		if(self.sens == "V"):
			self.img = makeImg(self.x, self.ypos, self.path, self.scale)
			
		if(self.sens == "H"):
			self.img = makeImg(self.ypos, self.y, self.path, self.scale)
		self.img.setColor(1,1,1,0.8)


