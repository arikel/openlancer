#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

import sys, math, random, os.path, os, re
#-------------------------------------------------------------------------------
# textColors
#-------------------------------------------------------------------------------
textColors = {}
# VF
textColors["blanc"] = ((1,1,1,1), (0,0,0,0))
textColors["Blanc"] = ((1,1,1,1), (0,0,0,1))
textColors["noir"] = ((0,0,0,1), (1,1,1,0))
textColors["Noir"] = ((0,0,0,1), (1,1,1,1))
textColors["rouge"] = ((1,0.2,0.2,1), (0,0,0,0))
textColors["Rouge"] = ((1,0.2,0.2,1), (0.1,0.1,0.1,1))
textColors["marron"] = ((0.8,0.5,0,1), (0,0,0,0))
textColors["Marron"] = ((0.8,0.5,0,1), (1,1,1,1))
textColors["bleu"] = ((0,0,0.8,1), (0,0,0,0))
textColors["bleuCiel"] = ((0.85,0.92,1,1), (0,0,0,0))
textColors["bleuciel"] = ((0.85,0.92,1,1), (0,0,0,0))
textColors["BleuCiel"] = ((0.85,0.92,1,1), (0,0,0,0))
textColors["Bleuciel"] = ((0.85,0.92,1,1), (0,0,0,0))
textColors["Bleu"] = ((0,0,0.8,1), (1,1,1,1))
textColors["jaune"] = ((1,1,0,1), (1,1,1,0))
textColors["Jaune"] = ((1,1,0,1), (0,0,0,1))
textColors["vert"] = ((0,1,0,1), (1,1,1,0))
textColors["Vert"] = ((0,1,0,1), (0,0,0,1))
textColors["or"] = ((1,0.75,0,1), (1,1,1,0))
textColors["Or"] = ((1,0.75,0,1), (0,0,0,1))
# VO
textColors["white"] = ((1,1,1,1), (0,0,0,0))
textColors["White"] = ((1,1,1,1), (0,0,0,1))
textColors["black"] = ((0,0,0,1), (1,1,1,0))
textColors["Black"] = ((0,0,0,1), (1,1,1,1))
textColors["red"] = ((1,0.2,0.2,1), (0,0,0,0))
textColors["Red"] = ((1,0.2,0.2,1), (0.1,0.1,0.1,1))
textColors["brown"] = ((0.8,0.5,0,1), (0,0,0,0))
textColors["Brown"] = ((0.8,0.5,0,1), (1,1,1,1))
textColors["blue"] = ((0,0,0.8,1), (0,0,0,0))
textColors["Blue"] = ((0,0,0.8,1), (1,1,1,1))
textColors["green"] = ((0,0.8,0,1), (0,0,0,0))
textColors["Green"] = ((0,0.8,0,1), (0,0,0,1))
textColors["yellow"] = ((1,1,0,1), (1,1,1,0))
textColors["Yellow"] = ((1,1,0,1), (0,0,0,1))
textColors["gold"] = ((1,0.75,0,1), (1,1,1,0))
textColors["Gold"] = ((1,0.75,0,1), (0,0,0,1))

FONT0 = loader.loadFont("fonts/arial.ttf")
FONT_SCALE0 = 0.05
FONT1 = loader.loadFont("fonts/euro.egg")
FONT_SCALE1 = (0.04, 0.05, 0.05)
FONT2 = loader.loadFont("fonts/cour.ttf")
FONT_SCALE2 = 0.05

FONT3 = loader.loadFont("fonts/Vera.ttf")
#FONT3.setRenderMode(TextFont.RMSolid)

#FONT3.setScaleFactor(2.0)

#FONT3.setPixelsPerUnit(80)
#FONT3.setPageSize(512,512)
#FONT3.setPointSize(64)
#FONT3.setRenderMode(TextFont.RMWireframe)
#FONT3.setRenderMode(TextFont.RMPolygon)
#FONT3.setRenderMode(TextFont.RMInvalid)
#FONT3.setPointSize(72) # a value of 73 or more crashes Panda/Python
#FONT3.setSpaceAdvance(2) # decrease as point size is decrease
#FONT3.setLineHeight(5)

FONT_SCALE3 = (0.028, 0.04, 1)
#FONT_SCALE3 = (0.06,0.08,1)
#FONT_SCALE3 = (35.0/1024.0, 55.0/1024.0, 1)
#FONT_SCALE3 = (32.0/800, 64.0/600, 1)
FONT = FONT3
FONT_SCALE = FONT_SCALE3

labelFont = loader.loadFont("fonts/arial.ttf", minFilter=Texture.FTNearest, magFilter=Texture.FTNearest)
#labelFont.setPixelsPerUnit(80)
labelFont.setPageSize(64,64)
#labelFont.setPointSize(60)
#labelFont.setRenderMode(TextFont.RMWireframe)
#labelFont.setRenderMode(TextFont.RMPolygon)
labelFont.setRenderMode(TextFont.RMSolid)
#labelFont.setRenderMode(TextFont.RMInvalid)
labelFont.setPointSize(72) # a value of 73 or more crashes Panda/Python
labelFont.setSpaceAdvance(2) # decrease as point size is decrease
labelFont.setLineHeight(5)
minFilter=Texture.FTNearest,
magFilter=Texture.FTNearest
#-------------------------------------------------------------------------------
# divers
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
# quelques variables utiles...
#-------------------------------------------------------------------------------
W = base.win.getXSize()
H = base.win.getYSize()
	

def getMouse():
	"""
	dx et dy compris entre -1 et 1
	"""
	if base.mouseWatcherNode.hasMouse():
		m = base.mouseWatcherNode.getMouse()
		dx = m.getX()
		dy = m.getY()
		return dx, dy
	return 0, 0
		

#-------------------------------------------------------------------------------
# makeImg
#-------------------------------------------------------------------------------
def makeImg(x,y, path, scale = 1):
	a = OnscreenImage(image=path, pos=(float(x),0,float(y)), hpr=None, scale=scale, color=None, parent=None, sort=0)
	a.setTransparency(True)
	return a

#-------------------------------------------------------------------------------
# makeMsg
#-------------------------------------------------------------------------------
def makeMsg(x,y, txt = "msg", color = "white"):
	fg = textColors[color][0]
	bg = textColors[color][1]
	M = OnscreenText(style=1, fg=fg, bg=bg, pos=(x, y), align=TextNode.ACenter, scale = FONT_SCALE, mayChange = 1, font = FONT)
	M.setText(txt)
	return M
	
def makeMsgLeft(x,y, txt = "msg", color = "white"):
	fg = textColors[color][0]
	bg = textColors[color][1]
	M = OnscreenText(fg=fg, bg=bg, pos=(x, y), align=TextNode.ALeft, mayChange = 1, font = FONT, scale=FONT_SCALE)
	M.setText(txt)
	return M
	
def makeMsgRight(x,y, txt = "msg", color = "white"):
	fg = textColors[color][0]
	bg = textColors[color][1]
	M = OnscreenText(style=1, fg=fg, bg=bg, pos=(x, y), align=TextNode.ARight, scale = FONT_SCALE, mayChange = 1, font = FONT)
	M.setText(txt)
	return M
	
def makeMsgCenter(x,y, txt = "msg", color = "white"):
	fg = textColors[color][0]
	bg = textColors[color][1]
	M = OnscreenText(style=1, fg=fg, bg=bg, pos=(x, y), align=TextNode.ACenter, scale = FONT_SCALE, mayChange = 1, font = FONT)
	M.setText(txt)
	return M

	
#-------------------------------------------------------------------------------
# makeGrid
#-------------------------------------------------------------------------------
def makeGrid():
	'''
	affiche une grille de points de 0.1 de côté
	'''
	i = -1.4
	while i<=1.4:
		j= -1.4
		while j <=1.4:
			makeImg(i, j, "img/gui/yellow.png", 1.0/H)
			j+=0.1
		i += 0.1
		
		

