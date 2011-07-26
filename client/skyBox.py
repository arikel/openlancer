#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.directbase import DirectStart

class SkyBox:
	def __init__(self):
		self.models = {}
		self.currentModel = None
		
	def load(self, name):
		path = "models/skies/" + str(name)
		model = loader.loadModel(path)
		model.setScale(512)
		model.setBin('background', 1)
		model.setDepthWrite(0)
		model.setLightOff()
		model.setShaderOff()
		self.models[name] = model
		
	def unload(self, name):
		if name in self.models:
			self.models[name].detachNode()
			del self.models[name]
			
	def start(self):
		if not (taskMgr.hasTaskNamed("skyTask")):
			taskMgr.add(self.task, "skyTask")
		
				
	def stop(self):
		if (taskMgr.hasTaskNamed("skyTask")):
			#print("Stopping skyTask")
			taskMgr.remove("skyTask")
		if self.currentModel:
				self.currentModel.detachNode()
		
	def task(self, task):
		self.currentModel.setPos(base.camera.getPos(render))
		return Task.cont
			
	def set(self, name):
		if name in self.models:
			if self.currentModel:
				self.currentModel.detachNode()
			self.currentModel = self.models[name]
			self.currentModel.reparentTo(render)
			self.start()
			return True
		else:
			print("Error : skybox %s not found." % (name))
			return False
			
			
	def clear(self, extraArgs=[]):
		self.currentModel.detachNode()
		self.stop()


