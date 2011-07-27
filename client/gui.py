#!/usr/bin/python
# -*- coding: utf8 -*-

# ----------- imports spécifiques à panda3d
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task.Task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *

import direct.directbase.DirectStart

from db import *

from guiBasics import *
from guiBarre import *
from guiMouseCursor import MouseCursor

# ----------- les modules courants
import sys, math, random, os.path, os, re



#-------------------------------------------------------------------------------
# Buttons
#-------------------------------------------------------------------------------
			

soundDic = {}
soundDic["rollover"] = loader.loadSfx("sounds/SOUNDS/UI/ui_rollover.wav")
soundDic["rollover"].setVolume(0.4)

soundDic["select_confirm"] = loader.loadSfx("sounds/SOUNDS/UI/ui_select_confirm.wav")
soundDic["select_confirm"].setVolume(0.4)

soundDic["hud_contract"] = loader.loadSfx("sounds/SOUNDS/UI/hud_contract.wav")
soundDic["hud_contract"].setVolume(0.8)
soundDic["hud_expand"] = loader.loadSfx("sounds/SOUNDS/UI/hud_expand.wav")
soundDic["hud_expand"].setVolume(0.8)




class MainButton(DirectButton):
	def __init__(self, x, y, name):
		DirectButton.__init__(self,
			frameSize = (-0.35,0.35,-0.07,0.07),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.8,1,0.6),
			#pressEffect = None,
			#scale = (0.4, 1, 0.1),
			#relief = None,
			relief = DGG.GROOVE,
			#relief = DGG.RIDGE,
			rolloverSound = soundDic["rollover"],
			clickSound = soundDic["select_confirm"],
			text_font = FONT3,
			#text_scale = (0.01,0.0125,1),
			text_scale = (0.06,0.08,1),
			text_fg = (0.8,0.9,1,1),
			#text_shadow = (0.25,0.25,0.25,1),
			text_bg = (0,0,0,0.0),
			text = name,
			text_align = TextNode.ACenter,
			text_pos = (0, -0.025),
			#geom = None
			text_mayChange = True,
		)
		self.initialiseoptions(MainButton)
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (0.95,0.85,0.2,1)
		self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.9,1,1)
		self["text_shadow"] = (0.0,0.5,0.95,1)


class MainMenu:
	def __init__(self):
		self.buttons = []
		step = 0.3
		start = 0.45
		b = MainButton(0, start, "NEW GAME")
		b2 = MainButton(0, start-step, "LOAD GAME")
		b3 = MainButton(0, start-2*step, "SETTINGS")
		b4 = MainButton(0, start-3*step, "QUIT")
		self.buttons.append(b)
		self.buttons.append(b2)
		self.buttons.append(b3)
		self.buttons.append(b4)
		
	def hide(self):
		for button in self.buttons:
			button.hide()
			
	def show(self):
		for button in self.buttons:
			button.show()
			
	
#-----------------------------------------------------------------------
# cargo, shop
#-----------------------------------------------------------------------
class ItemButtonBase:
	def __init__(self, x, y, id):
		self.x = x
		self.y = y
		
		self.data = id
		
		self.size = 0.075
		self.size2 = 0.25
		
		self.frame = DirectButton(
			frameSize = (-self.size,self.size,-self.size,self.size),
			frameColor=(0.6, 0.6, 0.9, 0.0),
			pos = (x, 0, y),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			rolloverSound = soundDic["rollover"],
			clickSound = soundDic["select_confirm"],
		)
		
		if self.data.imagePath.strip() != "":
			self.itemImg = makeImg(0,0,self.data.imagePath, self.size)
			self.itemImg.reparentTo(self.frame)
		else:
			self.itemImg = None
		
		self.img = makeImg(0, 0, "img/gui/square_white.png")
		self.img.reparentTo(self.frame)
		self.img.setScale(self.size,1,self.size)
		
		self.frame2 = DirectButton(
			frameSize = (-self.size2,self.size2,-self.size,self.size),
			frameColor=(0.6, 0.6, 0.9, 0.1),
			pos = (self.size+self.size2+0.01, 0, 0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			rolloverSound = soundDic["rollover"],
			clickSound = soundDic["select_confirm"],
		)
		self.frame2.reparentTo(self.frame)
		
		self.img2 = makeImg(0, 0, "img/gui/rect_white.png")
		self.img2.reparentTo(self.frame2)
		self.img2.setScale(self.size2,1,self.size)
		
		self.textItemName = makeMsgLeft(-self.size2+0.02, 0.02, self.data.name.upper())
		self.textItemName.reparentTo(self.frame2)
		
		if self.data.quant != "inf":
			self.textItemDesc = makeMsgLeft(-self.size2+0.02, -self.size+0.02, str(self.data.quant))
		else:
			self.textItemDesc = makeMsgLeft(-self.size2+0.02, -self.size+0.02, "")
			
		self.textItemDesc.reparentTo(self.frame2)
		
		self.textItemPrice = makeMsgRight(self.size2-0.02, -self.size+0.02, "$" + str(self.data.priceBuy))
		self.textItemPrice.reparentTo(self.frame2)
		
		self.selected = False
		
		self.setState(["enabled"])
		self.frame.bind(DGG.ENTER, command=self.setState, extraArgs=[["hover"]])
		self.frame.bind(DGG.EXIT, command=self.setState, extraArgs=[["enabled"]])
		#self.frame.bind(DGG.B1PRESS, command=self.toggleSelect)
		
		self.frame2.bind(DGG.ENTER, command=self.setState, extraArgs=[["hover"]])
		self.frame2.bind(DGG.EXIT, command=self.setState, extraArgs=[["enabled"]])
		#self.frame2.bind(DGG.B1PRESS, command=self.toggleSelect)
	
	'''
	def setOnClick(self, command, extraArgs):
		self.frame.bind(DGG.B1PRESS, command=command, extraArgs = [extraArgs])
		self.frame2.bind(DGG.B1PRESS, command=command, extraArgs = [extraArgs])
	'''
	
	def select(self):
		self.selected = True
		self.setState(["selectedHover"])
		self.frame.bind(DGG.ENTER, command=self.setState, extraArgs=[["selectedHover"]])
		self.frame.bind(DGG.EXIT, command=self.setState, extraArgs=[["selected"]])
		self.frame2.bind(DGG.ENTER, command=self.setState, extraArgs=[["selectedHover"]])
		self.frame2.bind(DGG.EXIT, command=self.setState, extraArgs=[["selected"]])
			
	def unselect(self):
		self.selected = False
		self.setState(["enabled"])
		self.frame.bind(DGG.ENTER, command=self.setState, extraArgs=[["hover"]])
		self.frame.bind(DGG.EXIT, command=self.setState, extraArgs=[["enabled"]])
		self.frame2.bind(DGG.ENTER, command=self.setState, extraArgs=[["hover"]])
		self.frame2.bind(DGG.EXIT, command=self.setState, extraArgs=[["enabled"]])
	
	def toggleSelect(self, sentArgs = []):
		if self.selected:
			self.unselect()
		else:
			self.select()
	
	def setState(self, extraArgs, sentArgs=[]):
		#print("Calling setState!", extraArgs, sentArgs)
		state = extraArgs[0]
		if state == "enabled":
			self.img.setColor(0.59,0.66,0.95)
			self.img2.setColor(0.59,0.66,0.95)
		if state == "hover":
			self.img.setColor(0.58,0.79,1.0)
			self.img2.setColor(0.58,0.79,1.0)
		if state == "disabled":
			self.img.setColor(0.25,0.25,0.25)
			self.img2.setColor(0.25,0.25,0.25)
		if state == "selected":
			self.img.setColor(0.9,0.85,0.35)
			self.img2.setColor(0.9,0.85,0.35)
			
		if state == "selectedHover":
			self.img.setColor(0.9,0.9,0.9)
			self.img2.setColor(0.9,0.9,0.9)
	
	def setPos(self, x, y):
		self.frame.setPos(x, 0, y)
		
	def reparentTo(self, node):
		self.frame.reparentTo(node)
		
	def hide(self):
		self.frame.hide()
		
	def show(self):
		self.frame.show()
		
	def destroy(self):
		self.frame.destroy()
		
	def update(self):
		self.textItemDesc.setText(str(self.data.quant))
		
#-----------------------------------------------------------------------
class ItemListBase:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
		self.itemButtons = []
		
		self.maxDisplayed = 5
		self.size = 0.075
		self.size2 = 0.25
		
		self.visibleFrame = DirectScrolledFrame(
			canvasSize = (0,2*(self.size2+self.size)+0.03,-2*self.size*self.maxDisplayed-0.03,0),
			frameSize = (0.0,2*(self.size2+self.size)+0.08,-2*self.size*self.maxDisplayed,0),
			frameColor=(1,1,1,0),
			pos = (x, 0, y),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			manageScrollBars = False,
			scrollBarWidth = 0.0,
		)
		
		self.frame = DirectFrame(
			#frameSize = (-0.02,0,-2*self.size*self.nbItems-0.03,0),
			frameColor=(0.7, 0.7, 0.9, 0.0),
			#pos = (0, 0, 0),
			pos = (0,0,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.frame.reparentTo(self.visibleFrame.getCanvas())
		
	def initSlider(self):
		self.slider = DirectScrollBar(
			value = 0.0,
			range = (0.0,self.nbPos),
			pageSize = 1.0,#/self.nbPos,
			scrollSize = 1.0,#/self.nbPos,
			command = self.checkSlider,
			orientation = DGG.VERTICAL,
			manageButtons = True,
			resizeThumb = True,
			frameSize = (2*(self.size2+self.size)+0.02,2*(self.size2+self.size)+self.size,-2*self.size*self.maxDisplayed,0),
			#frameTexture = "img/gui/vide.png",
			frameTexture = "img/gui/scrollbarbg.png",
			relief = DGG.FLAT,
			thumb_frameTexture = "img/gui/scrollbar.png",
			thumb_relief = DGG.FLAT,
			#verticalScroll_thumb_geom_scale = (0.07,1,0.12),
			#self.sframe['verticalScroll_scrollSize'] = 0.05,
			#self.sframe['verticalScroll_resizeThumb'] = False,
			thumb_clickSound = None,
			thumb_rolloverSound = None,
			incButton_image = (
				"img/gui/b4_1.png",
				"img/gui/b4_2.png",
				"img/gui/b4_2.png",
				"img/gui/b4_1.png"
			),
			incButton_image_scale = (self.size-0.02)/2.0,
			incButton_image_hpr = (0,0,-90),
			incButton_clickSound = soundDic["rollover"],
			incButton_rolloverSound = None,
			
			decButton_image = (
				"img/gui/b4_1.png",
				"img/gui/b4_2.png",
				"img/gui/b4_2.png",
				"img/gui/b4_1.png"
			),
			decButton_image_scale = (self.size-0.02)/2.0,
			decButton_image_hpr = (0,0,90),
			decButton_clickSound = soundDic["rollover"],
			decButton_rolloverSound = None,
		)
		
		self.slider.reparentTo(self.visibleFrame) # and not its .getCanvas : has to be visible all the time
		#self.slider.reparentTo(self.visibleFrame.getCanvas())
	def clearButtons(self):
		for b in self.itemButtons:
			b.destroy()
		
		self.itemButtons = []
	
	def update(self):
		self.clearButtons()
		self.slider.destroy()
		self.initItems()
		
	def setPos(self, x, y):
		self.visibleFrame.setPos(x,0,y)
		self.x = x
		self.y = y
		
	def checkSlider(self, extraArgs = []):
		
		self.slider["extraArgs"] = [self.slider["value"]]
		self.setListPos(int(self.slider["value"]))
		#if abs(self.slider["value"] - float(round(self.slider["value"],0))) > 1.0/1000:
		#	self.slider["value"] = float(round(self.slider["value"], 0))
		
	def setListPos(self, n):
		if n>self.nbPos-1:
			n = self.posMax
		#print "setting pos %s" % (n)
		self.frame.setPos(0,0,2*n*self.size)
		
	def select(self, extraArgs, sentArgs = []):
		name = extraArgs[0]
		#print "Select called!"
		for b in self.itemButtons:
			if b.data.name != name:
				b.unselect()
			else:
				b.select()
	
	def setOnClick(self, command, extraArgs = []):
		for item in self.itemButtons:
			item.setOnClick(command, extraArgs)
	
	def animHide(self):
		i = LerpScaleInterval(self.visibleFrame, 1.6, 0.001, 1, blendType='easeInOut')
		i.start()
		
		# color interval doesn't work
		i2 = LerpColorScaleInterval(self.visibleFrame, 1.6, (1,1,1,0), (1,1,1,1), blendType='easeInOut')
		i2.start()
		soundDic["hud_contract"].play()
		
	def animShow(self):
		i = LerpScaleInterval(self.visibleFrame, 1.6, 1, 0.001, blendType='easeInOut')
		i.start()
		
		i2 = LerpColorScaleInterval(self.visibleFrame, 1.6, (1,1,1,1), (1,1,1,0), blendType='easeInOut')
		i2.start()
		
		soundDic["hud_expand"].play()
		
	def hide(self):
		self.visibleFrame.hide()
		
		
	def show(self):
		self.visibleFrame.show()
		
	def destroy(self):
		self.visibleFrame.destroy()


#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
class CargoLootItemButton(ItemButtonBase):
	def __init__(self, x, y, id, shopgui):
		ItemButtonBase.__init__(self, x, y, id)
		self.textItemPrice.setText(str(self.data.priceSell))
		self.gui = shopgui
	
	
		
class CargoItemList(ItemListBase):
	def __init__(self, x, y, cargo, shopgui):
		ItemListBase.__init__(self, x, y)
		self.gui = shopgui
		self.cargo = cargo
		self.initItems()
	
	def select(self, extraArgs, sentArgs = []):
		name = extraArgs[0]
		#print "Select called!"
		for b in self.itemButtons:
			if b.data.name != name:
				b.unselect()
			else:
				b.select()
				id = makeLootItemData(b.data.name, b.data.quant)
				id.priceSell = b.data.priceSell
				id.priceBuy = b.data.priceBuy
				#print "Selecting cargo item to sell : %s, sell = %s, buy = %s" % (b.data.name, id.priceSell, id.priceBuy)
				self.gui.cpanel.setItem(id)
				self.gui.cpanel.setMode("sell")
				self.gui.cpanel.setSlider(b.data.quant)
				
	def initItems(self):
		self.nbItems = len(self.cargo.loot.keys())
				
		if self.nbItems<=self.maxDisplayed:
			self.nbPos = 1
		else:
			self.nbPos = self.nbItems-self.maxDisplayed+1
			
		self.posMax = self.nbPos - 1
		
		self.initSlider()
		
		
		keys = self.cargo.loot.keys()
		keys.sort()
		#print "Keys sorted : %s" % (keys)
		step = 0.0
		for i in keys:
			item = CargoLootItemButton(self.size, -step*self.size*2-self.size, self.cargo.loot[i], self.gui)
			item.reparentTo(self.frame)
			item.frame.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
			item.frame2.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
			self.itemButtons.append(item)
			step += 1.0
		

		
	
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
class ShopLootItemButton(ItemButtonBase):
	def __init__(self, x, y, id, shopgui):
		ItemButtonBase.__init__(self, x, y, id)
		self.gui = shopgui
		
class ShopItemList(ItemListBase):
	def __init__(self, x, y, shopdata, shopgui):
		ItemListBase.__init__(self, x, y)
		self.data = shopdata
		self.gui = shopgui
		self.initItems()
		
	def initItems(self):
		self.nbItems = len(self.data.loot.keys())
		for key in self.data.loot:
			if self.data.loot[key].status == "bought" and self.data.loot[key].quant == "bought":
				self.nbItems -= 1
		if self.nbItems<=self.maxDisplayed:
			self.nbPos = 1
		else:
			self.nbPos = self.nbItems-self.maxDisplayed+1
		
		
		self.posMax = self.nbPos - 1
		
		#print "%s items for 5 visible : %s positions, posMax = %s" % (nbItems, self.nbPos, self.posMax)
		self.initSlider()
		
		keys = self.data.loot.keys()
		keys.sort()
		#print "Keys sorted : %s" % (keys)
		step = 0.0
		for i in keys:
			if (self.data.loot[i].status == "sold"):
				item = ShopLootItemButton(self.size, -step*self.size*2-self.size, self.data.loot[i], self.gui)
				item.reparentTo(self.frame)
				item.frame.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
				item.frame2.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
				self.itemButtons.append(item)
				step += 1.0
			elif (self.data.loot[i].status == "bought") and (self.data.loot[i].quant != "bought"):
				item = CargoLootItemButton(self.size, -step*self.size*2-self.size, self.data.loot[i], self.gui)
				item.reparentTo(self.frame)
				item.frame.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
				item.frame2.bind(DGG.B1PRESS, command = self.select, extraArgs=[[item.data.name]])
				self.itemButtons.append(item)
				step += 1.0
		
	def select(self, extraArgs, sentArgs = []):
		name = extraArgs[0]
		#print "Select called!"
		for b in self.itemButtons:
			if b.data.name != name:
				b.unselect()
			else:
				b.select()
				price = b.data.priceBuy
				quant = int(self.gui.player.money) / int(price)
				#print "Quantity buyable : %s ($ %s / %s )" % (quant, self.gui.player.money, price)
				id = makeLootItemData(b.data.name, quant)
				id.priceSell = b.data.priceSell
				id.priceBuy = b.data.priceBuy
				
				self.gui.cpanel.setItem(id)
				self.gui.cpanel.setMode("buy")
				self.gui.cpanel.setSlider(quant)
		
class ShopCenterPanel:
	def __init__(self, shopgui):
		self.gui = shopgui
		self.frame = DirectFrame(
			frameSize = (-0.45,0.45,-0.7,0.7),
			frameColor=(0.7, 0.7, 0.9, 0.4),
			#pos = (0, 0, 0),
			pos = (0,0,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.buyButton = MainButton(0,-0.56,"BUY")
		self.buyButton.reparentTo(self.frame)
		self.buyButton.bind(DGG.B1PRESS, command = self.gui.buy)
		
		self.sellButton = MainButton(0,-0.56,"SELL")
		self.sellButton.reparentTo(self.frame)
		self.sellButton.bind(DGG.B1PRESS, command = self.gui.sell)
		
		self.slider = DirectScrollBar(
			value = 0.0,
			range = (0.0,1.0),
			pageSize = 1.0,
			scrollSize = 1.0,
			command = self.update,
			orientation = DGG.HORIZONTAL,
			manageButtons = True,
			resizeThumb = False,
			frameSize = (-0.40,0.40,0.0,0.05),
			pos = (0,1,0.45),
			#frameTexture = "img/gui/vide.png",
			frameTexture = "img/gui/scrollbarbg.png",
			relief = DGG.FLAT,
			thumb_frameTexture = "img/gui/scrollbar.png",
			thumb_relief = DGG.FLAT,
			#verticalScroll_thumb_geom_scale = (0.07,1,0.12),
			#self.sframe['verticalScroll_scrollSize'] = 0.05,
			#self.sframe['verticalScroll_resizeThumb'] = False,
			thumb_clickSound = None,
			thumb_rolloverSound = None,
			incButton_image = (
				"img/gui/b4_1.png",
				"img/gui/b4_2.png",
				"img/gui/b4_2.png",
				"img/gui/b4_1.png"
			),
			incButton_image_scale = 0.022,
			incButton_image_hpr = (0,0,180),
			incButton_clickSound = soundDic["rollover"],
			incButton_rolloverSound = None,
			
			decButton_image = (
				"img/gui/b4_1.png",
				"img/gui/b4_2.png",
				"img/gui/b4_2.png",
				"img/gui/b4_1.png"
			),
			decButton_image_scale = 0.022,
			decButton_image_hpr = (0,0,0),
			decButton_clickSound = soundDic["rollover"],
			decButton_rolloverSound = None,
		)
		self.slider.reparentTo(self.frame)
		
		self.itemButton = CargoLootItemButton(-0.26, 0.60, makeLootItemData("empty", 1), self.gui)
		self.itemButton.reparentTo(self.frame)
		
		self.quantMsg = makeMsgLeft(-0.15,0.2,"")
		self.priceMsg = makeMsgLeft(-0.15,0.12,"")
		self.quantMsg.reparentTo(self.frame)
		self.priceMsg.reparentTo(self.frame)
		
		self.quantMsg.setScale(0.04)
		self.priceMsg.setScale(0.04)
		
		self.descMsg = makeMsgLeft(-0.4, -0.05, "")
		self.descMsg.reparentTo(self.frame)
		
		self.setMode("sell")
		
		self.empty = makeLootItemData("empty", 1)
		
	def destroy(self):
		self.frame.destroy()
		
	def hide(self):
		#self.itemButton.data.name = "empty"
		#self.setItem(makeLootItemData("empty", 1))
		self.setItem(self.empty)
		self.frame.hide()
		#print "hiding center panel"
		
	def show(self):
		self.frame.show()
		
	def setItem(self, lootitemdata):
		self.itemButton.destroy()
		self.itemButton = CargoLootItemButton(-0.26, 0.60, lootitemdata, self.gui)
		self.setSlider(self.itemButton.data.quant)
		self.itemButton.reparentTo(self.frame)
		
	def setMode(self, mode="buy"):
		if mode == "buy":
			self.mode = "buy"
			self.sellButton.hide()
		else:
			self.mode = "sell"
			self.buyButton.hide()
		
	def setSlider(self, n):
		if n == 1:
			self.slider["range"] = (0.0, 1.0)
		else:
			self.slider["range"] = (1.0, float(n))
		self.slider["value"] = 1.0
		self.descMsg.setText("")
		
	def getQuant(self):
		self.itemButton.data.quant = int(round(self.slider["value"], 0))
		return self.itemButton.data.quant
		#return int(self.slider["value"])
		
	def update(self):
		#print "updating shop center panel"
		
		#if self.itemButton.data.name == "empty":
			#print "shop center panel skipping update : no item selected"
			#self.hide()
		#	return
		
		#self.show()
		
		
		
		self.itemButton.data.quant = int(round(self.slider["value"], 0))
		self.itemButton.update()
		
		msg = "Quantity : " + str(self.itemButton.data.quant)
		self.quantMsg.setText(msg)
		if self.mode == "sell":
			pricesell = int(self.itemButton.data.priceSell)
			self.itemButton.textItemPrice.setText(str(self.itemButton.data.priceSell))
			
			price = "Total : $ " + str(pricesell * int(self.itemButton.data.quant))
			self.buyButton.hide()
			self.sellButton.show()
		else:
			pricebuy = int(self.itemButton.data.priceBuy)
			self.itemButton.textItemPrice.setText(str(self.itemButton.data.priceBuy))
			
			price = "Total : $ " + str(pricebuy * int(self.itemButton.data.quant))
			#print ("pricebuy : %s * quant : %s => total : %s" % (pricebuy, self.itemButton.data.quant, price))
			self.sellButton.hide()
			self.buyButton.show()
			
		self.priceMsg.setText(price)
		
		room = self.gui.player.ship.cargo.getRoomLeft()
		quant = self.getQuant()
		name = self.itemButton.data.name
		
		if room < quant and self.mode == "buy":
			msg = "You don't have enough room for " + str(quant) + " units of " + str(name) + "."
			#print msg
			self.descMsg.setText(msg)
		else:
			self.descMsg.setText("")
			
class ShopGui:
	def __init__(self, player):
		self.player = player
		
		self.cargoList = CargoItemList(-1.22,0.25, self.player.ship.cargo, self)
		self.shopList = ShopItemList(0.50,0.25,player.currentBase.shop, self)
		self.cpanel = ShopCenterPanel(self)
		
		self.playerMoneyMsg = makeMsgLeft(-1.05, 0.28)
		self.playerMoneyMsg.setScale(0.065)
		
		self.cargoBar = CargoBarre(-1.1, -0.60, (0.8,0.8,1,1),70)
		
		self.update()
		
		#self.cargoList.setOnClick(self.onCargoSelect, [])
		
	def update(self):
		self.player.currentBase.shop.setCargoPrices(self.player.ship.cargo)
		
		self.cargoList.update()
		self.shopList.update()
		self.cpanel.update()
		room = int(self.player.ship.cargo.room - self.player.ship.cargo.getRoomLeft())
		self.cargoBar.set(room)
		
		msg = "$ " + str(self.player.money)
		self.playerMoneyMsg.setText(msg)

	def buy(self, extraArgs = [], sentArgs = []):
		name = self.cpanel.itemButton.data.name
		if name == "empty":
			#print "Nothing to buy"
			return
		quant = self.cpanel.getQuant()
		if quant == 0 or quant == "empty":
			#print "Nothing to buy"
			return
		price = self.cpanel.itemButton.data.priceBuy
		total = quant * price
		name = self.cpanel.itemButton.data.name
		
		if quant <= self.player.ship.cargo.getRoomLeft():
			self.player.ship.cargo.add(name, quant)
			self.player.pay(total)
			#print "Player just bought %s %s" % (quant, name)
		else:
			msg = "Player doesn't have enough room for " + str(quant) + " " + str(name)
			#print msg
			#self.cpanel.descMsg.setText(msg)
		
		self.update()
		
	def sell(self, extraArgs = [], sentArgs = []):
		name = self.cpanel.itemButton.data.name
		if name == "empty":
			#print "Nothing to sell"
			return
		quant = self.cpanel.getQuant()
		if quant == 0 or quant == "empty":
			#print "Nothing to sell"
			return
		price = self.cpanel.itemButton.data.priceSell
		total = quant * price
		name = self.cpanel.itemButton.data.name
		self.player.ship.cargo.remove(name, quant)
		self.player.getMoney(total)
		#print "Player got $ %s from selling %s %s" % (total, quant, name)
		#self.cpanel.hide()
		self.cpanel.setItem(self.cpanel.empty)
		self.update()
		
	def hide(self):
		self.cargoList.hide()
		self.shopList.hide()
		self.cpanel.hide()
		self.cargoBar.hide()
		self.playerMoneyMsg.hide()
		
	def show(self):
		self.cargoList.show()
		self.shopList.show()
		self.cpanel.show()
		self.cargoBar.show()
		self.playerMoneyMsg.show()
		
	def destroy(self):
		self.cargoList.destroy()
		self.shopList.destroy()
		self.cpanel.destroy()
		self.cargoBar.destroy()
		self.playerMoneyMsg.destroy()
#-------------------------------------------------------------------------------
# TopButtons
#-------------------------------------------------------------------------------
class TopButton(DirectButton):
	def __init__(self, x, y, name):
		scale = 0.05
		imgPath = "img/gui/topbuttons/" + str(name) + ".png"
		
		
		
		DirectButton.__init__(self,
			frameSize = (-scale,scale,-scale,scale),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.8,1,0.6),
			#pressEffect = None,
			#scale = (0.4, 1, 0.1),
			relief = None,
			#relief = DGG.GROOVE,
			#relief = DGG.RIDGE,
			rolloverSound = soundDic["rollover"],
			clickSound = soundDic["select_confirm"],
		)
		
		self.initialiseoptions(TopButton)
		
		self.img = makeImg(0,0,imgPath,scale)
		self.img.setColor(0.7,0.7,0.9,1)
		self.img.reparentTo(self)
		#self["image"].setTransparency(True),
		self.img.setColor(0.8,0.8,0.8,1.0)
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def onHover(self, extraArgs=[], sentArgs=[]):
		self.img.setColor(0.95,0.95,1.0,1.0)
		
	def onOut(self, extraArgs=[], sentArgs=[]):
		#self["text_fg"] = (0.8,0.9,1,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		#self["image_color"] = (0.7,0.7,0.9,1)
		self.img.setColor(0.8,0.8,0.8,1.0)
		
		
class SpaceTopButtonBar:
	def __init__(self):
		self.buttonFreefly = TopButton(-0.4,0.9,"spaceShip")
		self.buttonReach = TopButton(-0.2,0.9,"spaceReach")
		self.buttonDock = TopButton(0.0,0.9,"spaceDock")
		self.buttonFollow = TopButton(0.2,0.9, "spaceFollow",)
	def hide(self):
		self.buttonFreefly.hide()
		self.buttonReach.hide()
		self.buttonDock.hide()
		self.buttonFollow.hide()
	def show(self):
		self.buttonFreefly.show()
		self.buttonReach.show()
		self.buttonDock.show()
		self.buttonFollow.show()
		
	def destroy(self):
		self.buttonFreefly.destroy()
		self.buttonReach.destroy()
		self.buttonDock.destroy()
		self.buttonFollow.destroy()
		
class GroundTopButtonBar:
	def __init__(self):
		self.buttonBaseport = TopButton(-0.4,0.9,"dock")
		self.buttonBar = TopButton(-0.2,0.9,"bar")
		self.buttonLoot = TopButton(0.0,0.9,"shop")
		self.buttonEquip = TopButton(0.2,0.9,"equip")
		self.buttonShip = TopButton(0.4,0.9,"ship")
		
	def hide(self):
		self.buttonBaseport.hide()
		self.buttonBar.hide()
		self.buttonLoot.hide()
		self.buttonEquip.hide()
		self.buttonShip.hide()
		
	def show(self):
		self.buttonBaseport.show()
		self.buttonBar.show()
		self.buttonLoot.show()
		self.buttonEquip.show()
		self.buttonShip.show()
		
	def destroy(self):
		self.buttonBaseport.destroy()
		self.buttonBar.destroy()
		self.buttonLoot.destroy()
		self.buttonEquip.destroy()
		self.buttonShip.destroy()

class SpaceLabel(DirectButton):
	def __init__(self, x, y, genre, name):
		self.x = x
		self.y = y
		DirectButton.__init__(self,
			frameSize = (-0.2,0.2,-0.03,0.03),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.8,1,0.1),
			#pressEffect = None,
			#scale = (0.4, 1, 0.1),
			#relief = None,
			#relief = DGG.GROOVE,
			#relief = None,
			relief = DGG.FLAT,
			#relief = DGG.RIDGE,
			rolloverSound = soundDic["rollover"],
			clickSound = soundDic["select_confirm"],
			text_font = labelFont,
			#text_scale = (1.01,1.5,1),
			text_scale = (0.0045,0.005,1),
			text_fg = (0.8,0.9,1,1),
			#text_shadow = (0.25,0.25,0.25,1),
			text_bg = (0,0,0,0.0),
			text = name,
			text_align = TextNode.ALeft,
			text_pos = (-0.125, -0.016),
			#geom = None
			text_mayChange = True,
		)
		self.initialiseoptions(SpaceLabel)
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
		path = "img/gui/label" + genre.title() + ".png"
		self.img = makeImg(self.x-0.16, self.y, path, 0.025)
		
		self.distText = makeMsgLeft(self.x + 0.11, self.y - 0.016, "100")
		self.distText["font"] = labelFont
		self.distText["scale"] = (0.0045,0.005,1)
		self.distText["fg"] = (0.8,0.9,1,1)
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (0.95,0.85,0.2,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		self["frameColor"]=(0.4,0.85,1,0.2)
		self.distText["fg"] = (0.8,0.9,1,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.9,1,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		self["frameColor"]=(0.2,0.8,1,0.1)
		self.distText["fg"] = (0.8,0.9,1,1)
		
	def destroy(self):
		self.img.destroy()
		DirectButton.destroy(self)
	def show(self):
		self.img.show()
		DirectButton.show(self)
	def hide(self):
		self.img.hide()
		DirectButton.hide(self)
		
class SpaceGui:
	def __init__(self, playerdata):
		self.pdata = playerdata
		
		self.topbar = SpaceTopButtonBar()
		
		yellow = (0.65234375, 0.6484375, 0.3359375)
		blue = (0.25390625, 0.2734375, 0.7421875)
		red = (0.546875, 0.125, 0.17578125)
		self.laserHP = SpaceBarre(2,yellow)
		self.shieldHP = SpaceBarre(1,blue)
		self.coqueHP = SpaceBarre(0,red)
		
		self.speedMsg = OnscreenText(pos=(-0.98, -0.755), fg = (1,1,1,1), scale = 0.05, align=TextNode.ACenter, mayChange = 1)
		self.speedMsg["font"] = FONT
		self.speedMsg["scale"] = (0.04,0.05,1.0)
		
		self.speedImg = makeImg(-0.98, -0.74, "img/gui/speed.png", (0.11,1.0,0.07))
		
		self.label1 = SpaceLabel(-0.8,0.7,"loot", "item 1")
		
		self.hide()
		
	def setSpeed(self, speed):
		self.speedMsg.setText(str(speed))
		
	def show(self):
		self.topbar.show()
		self.laserHP.show()
		self.shieldHP.show()
		self.coqueHP.show()
		self.speedMsg.show()
		self.speedImg.show()
		self.label1.show()
		
	def hide(self):
		self.topbar.hide()
		self.laserHP.hide()
		self.shieldHP.hide()
		self.coqueHP.hide()
		self.speedMsg.hide()
		self.speedImg.hide()
		self.label1.hide()
		
	def destroy(self):
		self.topbar.destroy()
		self.laserHP.destroy()
		self.shieldHP.destroy()
		self.coqueHP.destroy()
		self.speedMsg.destroy()
		self.speedImg.destroy()
		self.label1.destroy()
		
class GroundGui:
	def __init__(self, playerdata):
		self.playerData = playerdata
		
		self.topbar = GroundTopButtonBar()
		
		self.shopGui = ShopGui(self.playerData)
		
		self.hide()
		
	def show(self):
		self.topbar.show()
		self.shopGui.show()
		
	def hide(self):
		self.topbar.hide()
		self.shopGui.hide()
	
	def destroy(self):
		self.topbar.destroy()
		self.shopGui.destroy()
		
		
