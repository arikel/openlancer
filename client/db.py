#!/usr/bin/python
# -*- coding: utf8 -*-

from xml.dom import minidom, Node

from pandac.PandaModules import *

#-----------------------------------------------------------------------
# XML handy stuff
#-----------------------------------------------------------------------

def getChildNodes(node, name):
	children = []
	for child in node.childNodes:
		if (child.nodeType == Node.ELEMENT_NODE and child.nodeName == name):
			children.append(child)
	return children

class FileParserBase:
	def getNode(self, dom, name):
		for node in getChildNodes(dom, name):
			return node
		return None
		
	def getNodes(self, dom, name):
		return getChildNodes(dom, name)
		
	def getSimpleData(self, dom, name):
		node = dom.getElementsByTagName(name)[0]
		res = str(node.childNodes[0].data)#.lower()
		res = res.strip()
		return res
	
	def getSimpleInt(self, dom, name):
		return int(self.getSimpleData(dom, name))
		
	def getSimpleFloat(self, dom, name):
		return float(self.getSimpleData(dom, name))
		
		
#-----------------------------------------------------------------------
# Item DB - itemDb.xml
#-----------------------------------------------------------------------
		
class LootItemData:
	def __init__(self, name, imagePath, desc, longDesc, priceSell, priceBuy, quant):
		self.name = name
		self.imagePath = imagePath
		if name == "empty":
			self.imagePath = ""
		self.desc = desc
		self.longDesc = longDesc
		self.priceSell = int(priceSell) # what the players gets if he sells the item, per unit
		self.priceBuy = int(priceBuy) # how much it costs to the player to buy one of those
		self.quant = quant # can be an int, or "inf" (sold by base), or "bought" (bought on base)
		if self.quant == "inf":
			self.status = "sold"
		elif self.quant == "bought":
			self.status = "bought"
		else:
			self.status = None
			self.quant = int(self.quant)


class ItemFileParser(FileParserBase):
	def __init__(self):
		f = open("itemDb.xml")
		self.xmlData = f.read()
		f.close()
		self.dom = minidom.parseString(self.xmlData)
		self.dom = self.getNode(self.dom, "items")
		
		self.itemDb = {} # name : ShipData
		
		self.itemNodes = self.getNodes(self.dom, "item")
		
		for item in self.itemNodes:
			name = self.getSimpleData(item, "name")
			imagePath = self.getSimpleData(item, "image")
			imagePath = "img/items/" + imagePath + ".png"
			
			desc = self.getSimpleData(item, "desc")
			longDesc = self.getSimpleData(item, "longDesc")
			priceSell = self.getSimpleData(item, "priceSell")
			priceBuy = self.getSimpleData(item, "priceBuy")
			quant = "inf"
			
			itemData = LootItemData(name, imagePath, desc, longDesc, priceSell, priceBuy, quant)
			
			self.itemDb[name] = itemData

itemDb = ItemFileParser().itemDb


def makeLootItemData(name, quant):
	""" returns an average LootItemData """
	
	if name in itemDb:
		id = LootItemData(
			name,
			itemDb[name].imagePath,
			itemDb[name].desc,
			itemDb[name].longDesc,
			itemDb[name].priceSell,
			itemDb[name].priceBuy,
			quant
		)
		return id
	print "Error : unable to create %s %s" % (quant, name)
	return None


#-----------------------------------------------------------------------
# CargoData
#-----------------------------------------------------------------------
class CargoData:
	def __init__(self, room):
		self.room = room # max number of lootItems carried
		self.loot = {} # name, LootItemData
		
	def add(self, name, quant):
		roomLeft = self.getRoomLeft()
		quant = int(str(quant))
		if quant<=roomLeft:
			#print "Cargo big enough, adding %s %s" % (quant, name)
			if name in self.loot:
				self.loot[name].quant += quant
			else:
				id = makeLootItemData(name, quant)
				if id != None:
					self.loot[name]=id
		else:
			print "cargo add error, not enough room for %s %s, room left = %s" % (quant, name, roomLeft)
			
	def remove(self, name, quant):
		if name in self.loot:
			if self.loot[name].quant >= quant:
				self.loot[name].quant -= quant
				if self.loot[name].quant == 0 and self.loot[name].status != "bought":
					del self.loot[name]
	
	def setPrice(self, name, sell, buy):
		if name in self.loot:
			self.loot[name].priceSell = sell
			self.loot[name].priceBuy = buy
			
	def getRoomLeft(self):
		roomLeft = self.room
		for i in self.loot:
			roomLeft -= self.loot[i].quant
		return roomLeft


#-----------------------------------------------------------------------
# Gun DB - gunDb.xml
#-----------------------------------------------------------------------

class GunData:
	def __init__(self, name):
		self.name = name
		self.classe = 1
		self.energyCost = 10
		self.shieldDmg = 10
		self.coqueDmg = 10
		self.lifeTime = 2.0
		self.speed = 300.0
		self.ray = 0.5
		self.refire = 0.2
		self.sound = "laser"
		self.model = "ray1"
		
		self.imagePath = ""
		self.desc = ""
		self.longDesc = ""
		self.priceSell = 1000 # what the players gets if he sells the item, per unit
		self.priceBuy = 1500 # how much it costs to the player to buy one of those

class GunFileParser(FileParserBase):
	def __init__(self):
		f = open("gunDb.xml")
		self.xmlData = f.read()
		f.close()
		self.dom = minidom.parseString(self.xmlData)
		self.dom = self.getNode(self.dom, "guns")
		
		self.gunDb = {} # name : gunData
		
		self.gunNodes = self.getNodes(self.dom, "gun")
		
		for gun in self.gunNodes:
			name = self.getSimpleData(gun, "name")
			gunData = GunData(name)
			
			imagePath = self.getSimpleData(gun, "image")
			gunData.imagePath = "img/items/" + imagePath + ".png"
			gunData.classe = self.getSimpleData(gun, "classe")
			gunData.energyCost = self.getSimpleFloat(gun, "energyCost")
			gunData.shieldDmg = self.getSimpleFloat(gun, "shieldDmg")
			gunData.coqueDmg = self.getSimpleFloat(gun, "coqueDmg")
			gunData.lifeTime = self.getSimpleFloat(gun, "lifeTime")
			gunData.speed = self.getSimpleFloat(gun, "speed")
			gunData.ray = self.getSimpleFloat(gun, "ray")
			gunData.refire = self.getSimpleFloat(gun, "refire")
			gunData.sound = self.getSimpleData(gun, "sound")
			gunData.model = self.getSimpleData(gun, "model")
			gunData.desc = self.getSimpleData(gun, "desc")
			gunData.longDesc = self.getSimpleData(gun, "longDesc")
			gunData.priceSell = self.getSimpleInt(gun, "priceSell")
			gunData.priceBuy = self.getSimpleInt(gun, "priceBuy")
			
			self.gunDb[name] = gunData

gunDb = GunFileParser().gunDb

#-----------------------------------------------------------------------
# Ship DB - shipDb.xml
#-----------------------------------------------------------------------
class ShipData:
	def __init__(self, name):
		self.name = name
		self.gunSlots = [] # list of [point, classe, gunData, active]
		self.storedGuns = [] # list of unequipped guns : [name]
		
	def makeCopy(self):
		newdata = ShipData(self.name)
		newdata.model = self.model
		
		newdata.gunSlots.extend(self.gunSlots)
		newdata.storedGuns.extend(self.storedGuns)
		
		newdata.initHP(
			self.coqueHPMax,
			self.shieldHPMax,
			self.gunHPMax,
			self.gunRecoverSpeed,
			self.shieldRecoverSpeed)
			
		newdata.setPushEngine(
			self.pushForce,
			self.pushMaxSpeed,
			self.pushSideForce,
			self.pushSideForceFactor)
			
		newdata.setSteerEngine(
			self.steerHForce, self.steerHMaxSpeed,
			self.steerPForce, self.steerPMaxSpeed,
			self.steerRForce, self.steerRMaxSpeed)
			
		newdata.setCargo(self.cargo.room)
			
		return newdata
		
	def initHP(self, coque, shield, gun, grs, srs):
		self.coqueHPMax = float(coque)
		self.shieldHPMax = float(shield)
		self.gunHPMax = float(gun)
		
		self.coqueHP = float(self.coqueHPMax)
		self.shieldHP = float(self.shieldHPMax)
		self.gunHP = float(self.gunHPMax)
		
		self.gunRecoverSpeed = float(grs)
		self.shieldRecoverSpeed = float(srs)
		
	def addCoqueHP(self, n):
		self.coqueHP += float(n)
		if self.coqueHP > self.coqueHPMax:
			self.coqueHP = self.coqueHPMax
			
	def remCoqueHP(self, n):
		self.coqueHP -= float(n)
		if self.coqueHP < 0.0:
			self.coqueHP = 0.0
	
	def addShieldHP(self, n):
		self.shieldHP += float(n)
		if self.shieldHP > self.shieldHPMax:
			self.shieldHP = self.shieldHPMax
			
	def remShieldHP(self, n):
		self.shieldHP -= float(n)
		if self.shieldHP < 0.0:
			self.shieldHP = 0.0
	
	def addGunHP(self, n):
		self.gunHP += float(n)
		if self.gunHP > self.gunHPMax:
			self.gunHP = self.gunHPMax
			
	def remGunHP(self, n):
		self.gunHP -= float(n)
		if self.gunHP < 0.0:
			self.gunHP = 0.0
	
	def setPushEngine(self, force, speed, sideForce, sideForceFactor):
		self.pushForce = float(force)
		self.pushMaxSpeed = float(speed)
		self.pushSideForce = float(sideForce)
		self.pushSideForceFactor = float(sideForceFactor)
		
	def setSteerEngine(self, hForce, hSpeed, pForce, pSpeed, rForce, rSpeed):
		# steer
		self.steerHForce = float(hForce)
		self.steerHMaxSpeed = float(hSpeed)
		
		self.steerPForce = float(pForce)
		self.steerPMaxSpeed = float(pSpeed)
		
		# roll
		self.steerRForce = float(rForce)
		self.steerRMaxSpeed = float(rSpeed)
	
	def addGunSlot(self, point, classe, gunData = None, active = False):
		self.gunSlots.append([point, classe, gunData, active]) # Point3, max classe of the gun (1 - 10), gunData if a gun is equipped
		#print "(ShipData) Added gun slot to ship data : %s" % (gunData) 
		
	def setGun(self, slotNumber, gunData, active=True):
		if gunData is not None:
			pass
			#print "(ShipData) Gun %s set on slot %s" % (gunData.name, slotNumber)
		else:
			active = False
		self.gunSlots[slotNumber][2] = gunData
		self.gunSlots[slotNumber][3] = active
		
	def removeGun(self, slotNumber):
		self.setGun(slotNumber, None)
	
	def clearGuns(self):
		for i in range(len(self.gunSlots)):
			self.removeGun(i)
	
	def hasGun(self, slotNumber):
		if self.gunSlots[slotNumber][2] != None:
			return True
		return False
	
	def setCargo(self, n):
		self.cargo = CargoData(n)
	
	
		
		
class ShipFileParser(FileParserBase):
	def __init__(self):
		f = open("shipDb.xml")
		self.xmlData = f.read()
		f.close()
		self.dom = minidom.parseString(self.xmlData)
		self.dom = self.getNode(self.dom, "ships")
		
		self.shipDb = {} # name : ShipData
		
		self.shipNodes = self.getNodes(self.dom, "ship")
		
		for ship in self.shipNodes:
			name = self.getSimpleData(ship, "name")
			shipData = ShipData(name)
			
			model = self.getSimpleData(ship, "model")
			shipData.model = model
			
			HP = self.getNode(ship, "HP")
			HPcoque = HP.getAttribute("coque")
			HPshield = HP.getAttribute("shield")
			HPgun = HP.getAttribute("gun")
			gunRecoverSpeed = HP.getAttribute("gunRecoverSpeed")
			shieldRecoverSpeed = HP.getAttribute("shieldRecoverSpeed")
			
			shipData.initHP(HPcoque, HPshield, HPgun, gunRecoverSpeed, shieldRecoverSpeed)
			
			PE = self.getNode(ship, "pushEngine")
			force = PE.getAttribute("force")
			speed = PE.getAttribute("speed")
			sideForce = PE.getAttribute("sideForce")
			sideForceFactor = PE.getAttribute("sideForceFactor")
			shipData.setPushEngine(force, speed, sideForce, sideForceFactor)
			
			SE = self.getNode(ship, "steerEngine")
			hForce = SE.getAttribute("hForce")
			hSpeed = SE.getAttribute("hSpeed")
			pForce = SE.getAttribute("pForce")
			pSpeed = SE.getAttribute("pSpeed")
			rForce = SE.getAttribute("rForce")
			rSpeed = SE.getAttribute("rSpeed")
			shipData.setSteerEngine(hForce, hSpeed, pForce, pSpeed, rForce, rSpeed)
			
			#-----------------------------------------------------------
			# gunslots and guns
			gunsNode = self.getNode(ship, "gunslots")
			
			slots = self.getNodes(gunsNode, "gunslot")
			for slot in slots:
				pointStr = slot.getAttribute("point")
				classe = slot.getAttribute("classe")
				pointCoords = pointStr.split(",")
				if len(pointCoords) == 3:
					point = Point3(float(pointCoords[0]), float(pointCoords[1]), float(pointCoords[2]))
				else:
					print "(ShipFileParser) Error : couldn't process gunslot position :("
				
				shipData.addGunSlot(point, classe)
			#-----------------------------------------------------------
			# default equipped guns, offered on purchase of the ship
			eqGunNodes = self.getNodes(gunsNode, "equippedGun") # node of all guns equipped
			for gun in eqGunNodes:
				gunName = str(gun.getAttribute("name"))
				active = str(gun.getAttribute("active"))
				slot = int(gun.getAttribute("slot"))
				
				if active == "true":
					shipData.setGun(slot, gunDb[gunName])
					#print "(ShipFileParser) Setting gun %s ready to fire for ship %s!" % (gunName, name)
				else:
					shipData.setGun(slot, gunDb[gunName], False)
					#print "(ShipFileParser) WARNING! Setting gun %s NOT ready to fire!" % (gunName)
			#-----------------------------------------------------------
			# cargo
			cargo = self.getSimpleData(ship, "cargo")
			shipData.setCargo(int(cargo))
			
			self.shipDb[name] = shipData
			#print "(ShipFileParser) Adding ship to shipDb : %s" % (name)
			
shipDb = ShipFileParser().shipDb


#-----------------------------------------------------------------------
# ShopData
#-----------------------------------------------------------------------
class ShopData:
	def __init__(self, name):
		self.name = name
		self.loot = {} # lootItem name : LootItemData
		
	def initSellItem(self, name, sell=None, buy=None):
		item = makeLootItemData(name, "inf")
		if item != None:
			if sell != None and sell != "default":
				item.priceSell = sell
			if buy != None and buy != "default":
				item.priceBuy = buy
			self.loot[name] = item
	
	def initBuyItem(self, name, sell=None, buy=None):
		item = makeLootItemData(name, "bought")
		if item != None:
			if sell != None and sell != "default":
				item.priceSell = sell
			if buy != None and buy != "default":
				item.priceBuy = buy
			self.loot[name] = item
			
	
	def setPrices(self, name, sell, buy):
		self.loot[name].priceSell = sell
		self.loot[name].priceBuy = buy
		
	def setCargoPrices(self, cargo):
		for name in self.loot:
			if name in cargo.loot:
				#print "Updated price for %s" % (name)
				cargo.loot[name].priceSell = self.loot[name].priceSell
				cargo.loot[name].priceBuy = self.loot[name].priceBuy

#-----------------------------------------------------------------------
# System DB - systemDb.xml
#-----------------------------------------------------------------------
class SystemData:
	def __init__(self, name):
		self.name = name
		
#-----------------------------------------------------------------------
# Base DB - baseDb.xml
#-----------------------------------------------------------------------

class SpaceBaseData:
	def __init__(self, name):
		self.name = name
		self.shop = ShopData(self.name)
		self.dockPoints = []
		
	def addDockPoint(self, point):
		self.dockPoints.append(point)
		
spaceBaseDb = {}

spaceBaseDb["hesperida"] = SpaceBaseData("hesperida")
'''
spaceBaseDb["hesperida"].shop.initSellItem("copper", 120, 150)
spaceBaseDb["hesperida"].shop.initSellItem("gold", 1200, 1800)
spaceBaseDb["hesperida"].shop.initSellItem("cardamine", 400, 600)
spaceBaseDb["hesperida"].shop.initSellItem("lead", 200, 450)
spaceBaseDb["hesperida"].shop.initSellItem("oil", 400, 600)
spaceBaseDb["hesperida"].shop.initSellItem("bronze", 400, 460)
spaceBaseDb["hesperida"].shop.initBuyItem("wood", 800, 900)
'''
spaceBaseDb["hesperida"].shop.initSellItem("copper")
spaceBaseDb["hesperida"].shop.initSellItem("gold")
spaceBaseDb["hesperida"].shop.initSellItem("cardamine")
spaceBaseDb["hesperida"].shop.initSellItem("lead")
spaceBaseDb["hesperida"].shop.initSellItem("oil")
spaceBaseDb["hesperida"].shop.initSellItem("bronze")
spaceBaseDb["hesperida"].shop.initBuyItem("wood")

#-----------------------------------------------------------------------
# Player Saved Games
#-----------------------------------------------------------------------
class PlayerData:
	def __init__(self):
		self.money = 10000
		self.ship = ShipData("sabre")
		self.currentBase = None
		
		# funstats, to extend when the important stuff will be set up
		self.funstats = {}
		self.funstats["totalCashMade"] = 0
		self.funstats["totalCashSpent"] = 0
		
		
	def setBase(self, spacebasedata):
		self.currentBase = spacebasedata
		self.currentBase.shop.setCargoPrices(self.ship.cargo)
		
	def setShip(self, shipdata):
		self.ship = shipdata
	
	def setMoney(self, amount):
		self.money = int(amount)
	
	def getMoney(self, amount):
		self.money += int(amount)
		print "got money %s, total now : %s" % (amount, self.money)
	def pay(self, amount):
		
		if self.money >= int(amount):
			self.money -= int(amount)
		else:
			print("Error : player doesn't have %s, only %s $" % (amount, self.money))
			
	def getLootItem(self, lootname, quant):
		self.ship.cargo.add(str(lootname), int(quant))
	
	def giveLootItem(self, lootname, quant):
		self.ship.cargo.remove(str(lootname), int(quant))


class PlayerFileParser(FileParserBase):
	def __init__(self, filename):
		self.filename = filename
		try:
			f = open(self.filename)
		except:
			f = None
			
		if f == None:
			print("Error : couldn't find save file %s" % (filename))
			return False
		self.xmlData = f.read()
		f.close()
		
		self.dom = minidom.parseString(self.xmlData) # xml node
		self.playerNode = self.getNode(self.dom, "player") # xml node
		
		self.playerData = PlayerData()
		
		# money
		money = int(self.getSimpleData(self.playerNode, "money"))
		self.playerData.setMoney(money)
		
		# player ship
		shipnode = self.getNode(self.playerNode, "ship")
		shipname = self.getSimpleData(shipnode, "name")
		self.playerData.setShip(shipDb[shipname])
		self.playerData.ship.clearGuns()
		#print "Setting player ship from DB : %s" % (shipname)
		
		# equipped guns
		# the gun slots of the ship better be already made (and emptied of default guns) with data
		# from shipDb, at this point
		
		gunsNode = self.getNode(shipnode, "guns")
		eqGunNodes = self.getNodes(gunsNode, "equippedGun") # node of all guns equipped
		for gun in eqGunNodes:
			name = str(gun.getAttribute("name"))
			active = str(gun.getAttribute("active"))
			slot = int(gun.getAttribute("slot"))
			
			if active == "true":
				self.playerData.ship.setGun(slot, gunDb[name])
				#print "Setting gun %s ready to fire!" % (name)
			else:
				self.playerData.ship.setGun(slot, gunDb[name], False)
		
		# player ship cargo items
		cargonode = self.getNode(shipnode, "cargo") # single node
		itemnodes = self.getNodes(cargonode, "item") # list of nodes
		for item in itemnodes:
			name = item.getAttribute("name")
			quant = item.getAttribute("quant")
			self.playerData.ship.cargo.add(name, quant)
			#print "Player loading : adding %s %s to ship cargo..." % (quant, name)
			
		# base data
		currentBase = self.getSimpleData(self.playerNode, "currentBase")
		if currentBase in spaceBaseDb:
			self.playerData.setBase(spaceBaseDb[currentBase])
		else:
			print "Error!! base %s not found in DB!" % (currentBase)
	
	def save(self):
		xmlData = ""
		xmlData += "<player>"
		
		xmlData += "<money>"
		xmlData += str(self.playerData.money)
		xmlData += "</money>"
		
		xmlData += "<ship>"
		
		xmlData += "<name>"
		xmlData += str(self.playerData.ship.name)
		xmlData += "</name>"
		
		# TODO : handle guns, equipped and stored
		
		xmlData += "<cargo>"
		for name in self.playerData.ship.cargo.loot:
			quant = self.playerData.ship.cargo.loot[name].quant
			text = "<item name = \"" + str(name) + "\" quant = \"" + str(quant) + "\"></item>"
			xmlData += text
			
		xmlData += "</cargo>"
		
		xmlData += "</ship>"
		
		xmlData += "<currentBase>"
		xmlData += str(self.playerData.currentBase.name)
		xmlData += "</currentBase>"
		
		xmlData += "</player>"
		
		f = open("save2.xml", "w")
		f.write(minidom.parseString(xmlData).toprettyxml())
		print "game saved."
