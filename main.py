# -*- coding: utf-8 -*-

# --------------------------------------------------------
# 2D Action Game using Pygame
# doc100@gmail.com
# --------------------------------------------------------

import os
import sys
import random
import string
import fpformat
import copy
import profile
import math

import pygame
import yaml
from pygame.locals import *

# Global
VERSION = ""
CS = 16      # Charactor chip Size (Pixel)
DL0 = 0      # Debug Level Low
DL1 = 1      # Debug Level
DL2 = 2      # Debug Level High
BLACK = 0, 0, 0
WHITE = 255, 255, 255
IMAGE_DIRECTORY = "image"
DATA_DIRECTORY = "data"
UP	 = K_UP
RIGHT= K_RIGHT
DOWN = K_DOWN
LEFT = K_LEFT
ENTER = K_x
CANCEL = K_z



class Config:

	def __init__(self):

		self.configData = yaml.load( open(os.path.join(DATA_DIRECTORY, 'config.yml') ))

		self.win_alpha 	 = self.get("win_alpha", 255)
		self.disp_bpp	 = self.get("disp_bpp", 0)
		self.fps		 = self.get("fps", 30)
		self.mouse_support = self.get("mouse_support", 0)
		self.music_freq	 = self.get("music_freq", 44100)
		self.music_bits	 = self.get("music_bits", 16)
		self.music_volume = self.getFloat("music_volume", 1.0)
		self.fontsize	 = self.get("fontsize", 20)
		self.fontpath	 = self.getStr("fontpath", os.path.join("font", "ipag\\ipag.otf"))
		self.fonttype	 = self.get("fonttype", 1)
		self.lineheight	 = self.getFloat("lineheight", 1.5)
		self.gDebugLevel	 = self.get("debuglevel", 0)
		self.doMouseView	 = self.get("domouseview", 0)
		self.flipKey	 = self.get("flipkey", 0)

		self.disp_flags	 = 0
		if self.get("fullscreen", 0):
			self.disp_flags |= FULLSCREEN
		if self.get("hwsurface", 0):
			self.disp_flags |= HWSURFACE
			self.disp_flags |= DOUBLEBUF
		if self.get("asyncblit", 0):
			self.disp_flags |= ASYNCBLIT

	def get(self, key, default):
		if self.configData.has_key(key):
			return int(self.configData[key])
		return default

	def getFloat(self, key, default):
		if self.configData.has_key(key):
			return float(self.configData[key])
		return float(default)

	def getStr(self, key, default):
		if self.configData.has_key(key):
			return self.configData[key]
		return default

	def display(self):
		print self.configData



class GameState:

	def __init__(self):
		self.playerLife = 100
		self.playerrx
		self.gamePauseFlag	 = False
		pass

	def writeToFile(self):
		pass


class Pos:

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.map = {0:self.x, 1:self.y}

	def __getitem__(self, index):
		if index == 0:
			return self.x
		elif index == 1:
			return self.y

	def __setitem__(self, index, value):
		if index == 0:
			self.x = value
		elif index == 1:
			self.y = value

	def __len__(self):
		return len(self.__dict__)


class Size:

	def __init__(self, w, h):
		self.w = w
		self.h = h

	def __getitem__(self, index):
		if index == 0:
			return self.w
		elif index == 1:
			return self.h

	def __len__(self):
		return len(self.__dict__)


class Dir:

	def __init__(self, top, right, bottom, left):
		self.top = top
		self.right = right
		self.bottom = bottom
		self.left = left


class ControlInterface:

	def __init__(self):
		self.key = {
			UP:		False, RIGHT:	False, DOWN:	False, LEFT:	False,
			ENTER:	False, CANCEL:	False,
		}
		self.keyOnce = {
			UP:		False, RIGHT:	False, DOWN:	False, LEFT:	False,
			ENTER:	False, CANCEL:	False,
		}
		self.connection = False
		self.scrollAmount = 0

	def connect(self):
		self.connection = True

	def disconnect(self):
		self.connection = False


class Controller(ControlInterface):

	def __init__(self):
		self.state = { K_UP:False, K_RIGHT:False, K_DOWN:False, K_LEFT:False,\
		               K_z:False, K_x:False }
		self.newstate = []
		self.link = None
		self.connection = False
		self.ctllist = []
		self.memMousePos = None
		self.gestureMargin = 32
		self.scrollAmount = 0

	def call(self):

		if self.connection == True:
			new = pygame.key.get_pressed()
			newstate = {
					UP:new[UP],
					RIGHT:new[RIGHT],
					DOWN:new[DOWN],
					LEFT:new[LEFT],
					ENTER:new[ENTER],
					CANCEL:new[CANCEL],
					}
			for dictkey in self.link.keyOnce.keys():
				self.link.keyOnce[dictkey] = False
			self.scrollAmount = 0

			if g.joypad != None:
				x = g.joypad.get_axis(0)
				y = g.joypad.get_axis(1)

				if abs(x) < 0.1:
					x = 0.0

				if abs(y) < 0.1:
					y = 0.0

				if x > 0:
					newstate[RIGHT] = True
				elif x < 0:
					newstate[LEFT] = True

				if y < 0:
					newstate[UP] = True
				elif y > 0:
					newstate[DOWN] = True

				if joypad.get_button(1):
					newstate[ENTER] = True

				if joypad.get_button(0):
					newstate[CANCEL] = True

			for e in g.state.event:
				if e.type == KEYDOWN:
					if e.dict['key'] == ENTER:
						self.link.keyOnce[ENTER] = True

					if e.dict['key'] == CANCEL:
						self.link.keyOnce[CANCEL] = True

					if e.dict['key'] == UP:
						self.link.keyOnce[UP] = True
					elif e.dict['key'] == DOWN:
						self.link.keyOnce[DOWN] = True

					if e.dict['key'] == RIGHT:
						self.link.keyOnce[RIGHT] = True
					elif e.dict['key'] == LEFT:
						self.link.keyOnce[LEFT] = True


			for dictkey in self.link.key.keys():
				self.link.key[dictkey] = False

			if newstate[UP] == True:
				self.link.key[UP] = True

			if newstate[RIGHT]:
				self.link.key[RIGHT] = True

			if newstate[DOWN]:
				self.link.key[DOWN] = True

			if newstate[LEFT]:
				self.link.key[LEFT] = True

			if newstate[ENTER]:
				self.link.key[ENTER] = True

			if newstate[CANCEL]:
				self.link.key[CANCEL] = True

			for dictkey in self.link.keyOnce.keys():
				self.link.keyOnce[dictkey] = False

			if (newstate[UP] == True) & (newstate[UP] <> self.state[UP]):
				self.link.keyOnce[UP] = True

			if (newstate[RIGHT] == True) & (newstate[RIGHT] <> self.state[RIGHT]):
				self.link.keyOnce[RIGHT] = True

			if (newstate[DOWN] == True) & (newstate[DOWN] <> self.state[DOWN]):
				self.link.keyOnce[DOWN] = True

			if (newstate[LEFT] == True) & (newstate[LEFT] <> self.state[LEFT]):
				self.link.keyOnce[LEFT] = True

			if (newstate[ENTER] == True) & (newstate[ENTER] <> self.state[ENTER]):
				self.link.keyOnce[ENTER] = True

			if (newstate[CANCEL] == True) & (newstate[CANCEL] <> self.state[CANCEL]):
				self.link.keyOnce[CANCEL] = True

			if self.scrollAmount == 0:
					self.scrollAmount = 1

			self.link.scrollAmount = self.scrollAmount

			flag = False
			for s in newstate:
				if s:
					flag = True

			if flag == False:
				pass

			self.state[K_UP] = newstate[K_UP]
			self.state[K_RIGHT] = newstate[K_RIGHT]
			self.state[K_DOWN] = newstate[K_DOWN]
			self.state[K_LEFT] = newstate[K_LEFT]
			self.state[K_x] = newstate[K_x]
			self.state[K_z] = newstate[K_z]

			self.key = self.link.key
			self.keyOnce = self.link.keyOnce

	def connect(self, link):
		self.ctllist.append(link)

		if self.link != None:
			self.link.disconnect()
			for dictkey in self.link.key.keys():
					self.link.key[dictkey] = False

			for dictkey in self.link.keyOnce.keys():
					self.link.keyOnce[dictkey] = False

		self.link = link
		self.connection = True

		self.link.connect()

	def disconnect(self):
		if len(self.ctllist) >= 2:
			self.ctllist.pop()
			self.connect(self.ctllist.pop())
		else:
			if len(self.ctllist) == 1:
				self.ctllist.pop()
			self.connection = False
			self.link = None

	def free(self):
		while(len(self.ctllist) > 0):
			self.disconnect()









class Object:
	def __init__(self):
		self.id = 0
		self.count = 0
		self.locking = False

	def draw(self):
		pass

	def call(self):
		pass

	def __del__(self):
		pass

	def lock(self):
		self.locking = True

	def unlock(self):
		self.locking = False


class VisibleObject(Object):

	def __init__(self):
		Object.__init__(self)
		self.pos = Pos(0,0)
		self.old_pos = Pos(0,0)
		self.zpos = 0
		self.zindex = 0
		self.useCol = False
		self.type = ""
		self.battle = False

	def call(self):
		pass

	def draw(self, screen, campos=(0,0)):
		pass


class Window(Object, ControlInterface):

	def __init__(self, pos, size, mode=0):
		padding=Dir(g.config.fontsize, int(g.config.fontsize/2), int(g.config.fontsize/2), g.config.fontsize)
		self.pos = pos
		self.size = Size(0,0)
		self.boxpos = Pos(0,0)
		self.boxsize = Size(0,0)
		self.frameSrcPosX = 32
		self.frameSrcPosY = 16
		self.padding = padding
		self.border = Dir(8, 8, 8, 8)
		if mode == 1:
			self.forceWinAlpha = True
		else:
			self.forceWinAlpha = False

		self.bgcolor_A = [25,28,51]
		self.bgcolor_B = [57,86,115]
		self.highlight_bgcolor_A = [14,28,115]
		self.highlight_bgcolor_B = [91,121,242]
		self.bordercolor = [0,0,0]
		self.count = 0
		self.mode = mode

		self.setSize(size)
		self.setPos(pos)
		self.drawBuffer()

	def setSize(self, size):
		self.size = Size( int(size.w), int(size.h) )
		self.boxsize = Size( self.size.w + (self.padding.left + self.padding.right) + (self.border.left + self.border.right), \
		                self.size.h + (self.padding.top + self.padding.bottom) + (self.border.top + self.border.bottom))
		self.scrbuf = pygame.Surface((self.boxsize.w, self.boxsize.h)).convert()
		self.scrbuf.fill((0,0,0))
		self.scrbuf.set_colorkey((0,0,0))

		if g.config.win_alpha != 255:
			if g.config.disp_flags & HWSURFACE:
				pass
			else:
				self.scrbuf.set_alpha(g.config.win_alpha)
		else:
			if self.mode == 1:
				self.scrbuf.set_alpha(g.config.win_alpha)

		if self.forceWinAlpha:
			self.scrbuf.set_alpha(214)

		self.drawBuffer()

	def setPos(self, pos):
		self.pos = pos
		self.boxpos = Pos( self.pos.x - (self.padding.left + self.border.left), \
		              self.pos.y - (self.padding.top + self.border.top) )

	def call(self):
		count+=1

	def setMode(self, mode):
		oldmode = self.mode
		self.mode = mode
		if self.mode != oldmode:
			self.drawBuffer()

	def drawBuffer(self):
		bgcolor_A = self.bgcolor_A
		bgcolor_B = self.bgcolor_B
		if self.mode == 1:
			bgcolor_A = self.highlight_bgcolor_A
			bgcolor_B = self.highlight_bgcolor_B

		winDeco = True
		if winDeco:
			fx = self.frameSrcPosX
			fy = self.frameSrcPosY

			drawRect( self.scrbuf,
			          Rect( self.border.left, self.border.top, \
			                self.boxsize.w - (self.border.left + self.border.right), \
			                self.boxsize.h - (self.border.top + self.border.bottom) ), \
			          bgcolor_A, bgcolor_B )

			for i in range(self.border.left, self.boxsize.w-self.border.right):
				self.scrbuf.blit(g.img["parts"], (i,0), (fx+8, fy, 1, 8))

			self.scrbuf.blit(g.img["parts"], (self.boxsize.w-self.border.right, 0), (fx+16, fy, 8, 8))

			for i in range(self.border.top, self.boxsize.h-self.border.bottom):
				self.scrbuf.blit(g.img["parts"], (self.boxsize.w-self.border.right,i), (fx+16, fy+8, 8, 1))

			self.scrbuf.blit(g.img["parts"], (self.boxsize.w-self.border.right, self.boxsize.h-self.border.bottom), (fx+16, fy+16, 8, 8))

			for i in range(self.border.left, self.boxsize.w-self.border.right):
				self.scrbuf.blit(g.img["parts"], (i,self.boxsize.h-self.border.bottom), (fx+8, fy+16, 1, 8))

			self.scrbuf.blit(g.img["parts"], (0,self.boxsize.h-self.border.bottom), (fx, fy+16, 8, 8))

			for i in range(self.border.top, self.boxsize.h-self.border.bottom):
				self.scrbuf.blit(g.img["parts"], (0,i), (fx, fy+8, 8, 1))

			self.scrbuf.blit(g.img["parts"], (0,0), (fx, fy, 8, 8))
		else:
			rect = Rect(0,0,self.boxsize.w, self.boxsize.h)
			color = [0,0,0]
			color_A = bgcolor_A
			color_B = bgcolor_B

			rezo = 8
			for i in range(rect.h/rezo):
				for j in range(3):
					color[j] = (color_A[j] * (rect.h-i*rezo) + color_B[j] * i*rezo) / rect.h
				self.scrbuf.fill(color, (rect.x, rect.y + i*rezo, rect.w, rezo))

			pygame.draw.rect(self.scrbuf, (240,240,240), (0,0,self.boxsize.w, self.boxsize.h/rezo*rezo), 1)

	def draw(self, screen, campos=(0,0)):
		screen.blit(self.scrbuf, (self.boxpos.x, self.boxpos.y))



class Map:
	def __init__(self):  # コンストラクタ
		self.filepath = ""
		self.size = Size(0,0)
		self.pos = Pos(0,0)
		self.zindex = -1

	def load(self, filePath):
		self.filePath = fileOath

		# マップ画像読み込み
		try:
			trace(DL2, "map.setMap().filepath: "+`filepath`)
			block = string.split(filepath, '.')
			name = block[0]
			extend = block[1]
			self.src, self.size = loadImage(os.path.join(IMAGE_DIRECTORY, name+'.'+extend))
		except Exception, message:
			trace(DL1, "map.setMap() - Error occured on map image load. set temporary map image.")
			self.src = pygame.Surface((640,480)).convert()
			self.size = Size(640,480)



class MenuItem:

	def __init__(self, name, cmd, obj=None):
		self.name = name
		self.cmd = cmd
		self.obj = obj

class Menu(ControlInterface, VisibleObject):

	ITEM_CANTSELECT = 10
	ITEM_NORMAL = None

	def __init__(self, **prm):
		VisibleObject.__init__(self)
		ControlInterface.__init__(self)
		self.connected = False
		self.idtag = None
		self.zindex = 0
		self.screen = g.screen
		self.pos = Pos(0, 0)
		self.size = Size(0, 0)
		self.rect = Rect(0,0,0,0)
		self.help = ""
		self.itemsel = 0
		self.lines = 1
		self.olditemsel = self.itemsel
		self.itemlist = []
		self.itemnum = 0
		self.disp_itemnum = 0
		self.scroll_pos = 0
		self.old_scroll_pos = 0
		if prm.has_key('forceWinAlpha'):
			self.forceWinAlpha = 1
		else:
			self.forceWinAlpha = 0
		self.fontcolor = [255,255,255]
		self.selcolor = [255,192,0]
		self.helpbgcolor = [72,80,88]
		self.lineheight = 1.5
		self.padding = Dir(g.config.fontsize, int(g.config.fontsize/2), int(g.config.fontsize/2), g.config.fontsize)
		self.border = Dir(2, 6, 4, 2)
		self.count = 0
		self.keycount = 0
		self.anchorL = False
		self.anchorR = False
		self.doDispCursor = False
		self.win = None
		self.helpfontsize = 16
		self.helpfont = pygame.font.Font(g.config.fontpath, self.helpfontsize)
		self.itemHeight = int(g.config.fontsize * self.lineheight)
		self.history = []
		self.oldkey = self.key.copy()
		self.doDraw = True
		for menu in g.menuMgr.menulist:
			self.history.append(menu)
		self.load()

	def getMenu(self):
		pass

	def resetFromSize(self):
		max_itemnum = int(math.floor(self.size.h / (g.config.fontsize * self.lineheight)))
		if max_itemnum > self.itemnum:
			self.disp_itemnum = self.itemnum*self.lines
		else:
			self.disp_itemnum = max_itemnum*self.lines

	def setPos(self, pos):
		self.pos = pos
		self.win.setPos(pos)

	def setSize(self, size):
		self.size = size
		self.win.setSize(size)

	def load(self):
		self.getMenu()
		self.itemnum = len(self.itemlist)

		self.rect.w = self.rect.w*self.lines + ((self.lines-1)*2*g.config.fontsize)
		self.pos = Pos(self.rect.x, self.rect.y)
		self.size = Size(self.rect.w, self.rect.h)
		if self.size.w < 0:
			maxlen = 0
			for item in self.itemlist:
				if maxlen < len(item.name):
					maxlen = len(item.name)
			self.size.w = int(maxlen * fontsize)

		if self.size.h < 0:
			self.size.h = int(len(self.itemlist) * (g.config.fontsize *g.config.lineheight))
		self.win = Window(self.pos, self.size, self.forceWinAlpha)

		self.resetFromSize()
		self._cashRender()
		self.drawBuffer()

		if self.help != '':
			ren = self.helpfont.render(self.help, g.config.fonttype, (255,255,255))
			self.ren_help = pygame.Surface(ren.get_size()).convert()
			color = self.helpbgcolor
			#if colCtrSw:
			#	color = colCtrChg(color, 1)
			self.ren_help.fill(color)
			self.ren_help.blit( ren, (0,0), (0, 0, ren.get_width(), ren.get_height()) )

	def _cashRender(self):
		self.buf = pygame.Surface((self.size.w, self.size.h)).convert()

		self.buf.set_colorkey((0,0,0))
		self.ren_upanchor = pygame.Surface((32, 16)).convert()
		self.ren_upanchor.blit( g.img["parts"], (0,0), (11*16, 0, 32, 16) )
		self.ren_upanchor.set_colorkey((0,0,0))
		self.ren_downanchor = pygame.Surface((32, 16)).convert()
		self.ren_downanchor.blit( g.img["parts"], (0,0), (13*16, 0, 32, 16) )
		self.ren_downanchor.set_colorkey((0,0,0))
		self.ren_leftanchor = pygame.Surface((16, 32)).convert()
		self.ren_leftanchor.blit( g.img["parts"], (0,0), (15*16, 0, 16, 32) )
		self.ren_leftanchor.set_colorkey((0,0,0))
		self.ren_rightanchor = pygame.Surface((16, 32)).convert()
		self.ren_rightanchor.blit( g.img["parts"], (0,0), (15*16, 2*16, 16, 32) )
		self.ren_rightanchor.set_colorkey((0,0,0))

		self.ren_cursor = pygame.Surface((32, 32)).convert()
		self.ren_cursor.blit( g.img["parts"], (0,0), (0, 16, 32, 32) )
		self.ren_cursor.set_colorkey((0,0,0))
		self._cashRenderText()

	def _cashRenderText(self):
		self.ren_iname = []
		for i in range(0, self.disp_itemnum):
			inum = i + self.scroll_pos
			try:
				item = self.itemlist[inum]
			except IndexError, message:
				trace(DL2, "Index Error. TeamItemMenu.drawBuffer().self.itemlist[inum]")
				continue
			ren = self._renderText(item, None, i)
			self.ren_iname.append(ren)

	def _renderText(self, menuItem, apColor=None, i=0):
		item = menuItem

		if item.obj == False:
			t = float(i) / float(self.disp_itemnum)
			r = self.win.highlight_bgcolor_A[0]*(1-t) + self.win.highlight_bgcolor_B[0]*(t)
			g = self.win.highlight_bgcolor_A[1]*(1-t) + self.win.highlight_bgcolor_B[1]*(t)
			b = self.win.highlight_bgcolor_A[2]*(1-t) + self.win.highlight_bgcolor_B[2]*(t)
			color = (r,g,b)
			markcolor = 0
		elif item.obj == True:
			color = (176,176,176)
			markcolor = 0
		elif item.obj == -1:
			color = (96,240,96)
			markcolor = 0
		elif item.obj == self.ITEM_CANTSELECT:
			color = (96,96,96)
			markcolor = 0
		else:
			color = self.fontcolor
			markcolor = 0

		if apColor != None:
			color = apColor
		"""
		elif self.itemsel == inum:
			color = self.selcolor
			markcolor = 1
		"""
		#if colCtrSw:
		#	color = colCtrChg(color, 1)
		global g
		ren = render(g.font, item.name, 0, color).convert()

		return ren

	def reload(self):
		self.keyClear()
		self.load()
		self.call()

	def setFontsize(self, fontsize):
		pass

	def receive(self, message):
		pass

	def reRender(self):
		self._cashRenderText()
		self.drawBuffer()

	def drawBuffer(self):
		d = self.scroll_pos - self.old_scroll_pos

		if len(self.itemlist) > 0:
			self.ren_iname_select = self._renderText(self.itemlist[self.itemsel], self.selcolor)

		if d != 0:
			temp = []
			for i in range(0,abs(d)):
				if d > 0:
					index =  i  + self.scroll_pos + self.disp_itemnum-self.lines
				else:
					index = i + self.scroll_pos
				item = self.itemlist[index]
				temp.append(self._renderText(item))

			for i in range(0, self.disp_itemnum):
				shift = d / abs(d)
				if d > 0:
					targetIndex = i - abs(d)
					if targetIndex >= 0:
						self.ren_iname[targetIndex] = self.ren_iname[i]
				else:
					i = (self.disp_itemnum-1) - i
					targetIndex = i + abs(d)
					if targetIndex < self.disp_itemnum:
						self.ren_iname[targetIndex] = self.ren_iname[i]

			for i in range(0,abs(d)):
				if d > 0:
					index = (i - abs(d)) + (self.disp_itemnum)
					self.ren_iname[index] = temp[i]
				else:
					index = i
					self.ren_iname[index] = temp[i]

		self.buf.fill((0,0,0,255))
		for i in range(0, self.disp_itemnum):
			self.buf.blit(self.ren_iname[i], self._getTextPos(i)  )

	def _getTextPos(self, index):
		i = index
		return ((i%self.lines)*14*g.config.fontsize, 0 + (i/self.lines * g.config.fontsize * self.lineheight)	)

	def _drawText(self, index):
		pass

	def draw(self, screen, campos=(0,0)):
		if not self.doDraw:
			return

		self.win.draw(screen)
		screen.blit(self.buf, (self.win.pos.x, self.win.pos.y))

		if hasattr(self, "ren_iname_select"):
			tPos = self._getTextPos(self.itemsel-self.scroll_pos)
			tPos = (tPos[0] + self.pos.x, tPos[1] + self.pos.y)
			screen.blit(self.ren_iname_select, tPos )

		if self.help != '':
			pos = self.helpPos
			screen.fill( (8,8,8), (pos.x, pos.y, (len(self.help)*self.helpfontsize)+6, self.helpfontsize*lineheight) )
			color = self.helpbgcolor
			if colCtrSw:
				color = colCtrChg(color, 1)
			screen.fill( color, (pos.x+1, pos.y+1, (len(self.help)*self.helpfontsize)+4, self.helpfontsize*lineheight-2) )
			self.screen.blit(self.ren_help, (pos.x+4, pos.y+4) )

		if len(self.itemlist) >= 1:
			if self.disp_itemnum < self.itemnum:
				barpos = Pos( self.win.boxpos.x + (self.win.boxsize.w - self.border.right+1),
							  self.win.boxpos.y + self.win.border.top + (self.scroll_pos * (self.win.boxsize.h - (self.win.border.top+self.win.border.bottom)) / self.itemnum ))
				barsize = Size( self.win.border.right-2,
								(self.win.boxsize.h - (self.win.border.top+self.win.border.bottom)) / self.itemnum * self.disp_itemnum )

				screen.fill((0,0,0), (barpos.x-2, barpos.y, barsize.w+4, barsize.h))
				screen.fill((255,255,255), (barpos.x+1, barpos.y+2, barsize.w-2, barsize.h-4))

			if (self.scroll_pos) > 0:
				screen.blit(self.ren_upanchor, (self.win.pos.x+self.win.size.w/2 - self.ren_upanchor.get_width()/2,
				                  self.win.boxpos.y) )

			if (self.scroll_pos+self.disp_itemnum) < self.itemnum:
				screen.blit(self.ren_downanchor, (self.win.pos.x+self.win.size.w/2 - self.ren_upanchor.get_width()/2,
				                  self.win.pos.y+self.win.size.h) )

			if self.anchorL:
				screen.blit(self.ren_leftanchor, (self.win.pos.x - 26 - self.ren_leftanchor.get_width()/2,
				                  self.win.boxpos.y+self.win.size.h/2) )

			if self.anchorR:
				screen.blit(self.ren_rightanchor, (self.win.pos.x + 16 + self.win.size.w - self.ren_rightanchor.get_width()/2,
				                  self.win.boxpos.y+self.win.size.h/2) )

			if self.connection:
				curpos = Pos( (self.itemsel%(self.lines)*(self.size.w/self.lines+fontsize))+self.win.boxpos.x + 4 - 16 + resoSin(3, def_fps/3, self.count), self.pos.y - 3 + ((self.itemsel/self.lines - self.scroll_pos/self.lines) * self.itemHeight))
				screen.blit(self.ren_cursor, (curpos.x, curpos.y))

	def calcScrollPos(self, itemsel):
		return (itemsel / self.disp_itemnum) * self.disp_itemnum

	def call(self):
		self.olditemsel = self.itemsel
		self.old_scroll_pos = copy(self.scroll_pos)

		firstinterval = 8
		interval = 2
		if self.key != self.oldkey and self.key[ENTER] == False:
			self.keycount = 0
			self.oldkey = self.key.copy()

		if (self.keycount == 0) or ( (((self.keycount) % interval) == 0) & (self.keycount > firstinterval) ):
			if self.key[UP]:
				self.itemsel -= self.lines
				if self.itemsel < self.scroll_pos:
					if self.scroll_pos > 0:
						self.scroll_pos -= self.lines
			if self.key[DOWN]:
				self.itemsel += self.lines
				if self.itemsel/self.lines > (self.scroll_pos + self.disp_itemnum)/self.lines-1:
					if self.scroll_pos < (self.itemnum - self.disp_itemnum):
						self.scroll_pos += self.lines
		self.keycount += 1

		if self.keyOnce[LEFT]:
			if (self.itemsel%self.lines) > 0:
				self.itemsel -= 1
			self.back()

		if self.keyOnce[RIGHT]:
			if (self.itemsel%self.lines) < (self.lines-1):
				self.itemsel += 1
			self.forward()

		if self.disp_itemnum == self.itemnum:
			isScrollMenu = True
		else:
			isScrollMenu = False

		if self.itemsel < 0:
			if isScrollMenu:
				self.itemsel += self.itemnum
				self.scroll_pos = self.itemnum - self.disp_itemnum
			else:
				self.itemsel = copy(self.olditemsel)
		elif self.itemsel >= self.itemnum:
			if isScrollMenu:
				self.itemsel -= self.itemnum
				self.scroll_pos = 0
			else:
				self.itemsel = copy(self.olditemsel)

		if self.keyOnce[ENTER]:
			if self.itemlist[self.itemsel].obj != self.ITEM_CANTSELECT:
				self.action()
			else:
				sound.playSound(3)

		if self.keyOnce[CANCEL]:
			self.cancel()

		if self.itemsel != self.olditemsel:
			self.onSelChange()

		if self.connection:
			self.count += 1

	def onSelChange(self, reRenderFlag=False):
		sound.playSound(0)
		if reRenderFlag:
			self.reRender()
		else:
			self.drawBuffer()

	def action(self):
		sound.playSound(1)

	def cancel(self):
		sound.playSound(2)
		menuMgr.pop()

	def forward(self):
		pass

	def back(self):
		pass

	def connect(self):
		ControlInterface.connect(self)
		self.doDispCursor = True
		self.doDraw = True
		self.connected = True

	def disconnect(self):
		ControlInterface.disconnect(self)
		self.doDispCursor = False

	def keyClear(self):
		self.key = ControlInterface().key.copy()
		self.oldkey = ControlInterface().key.copy()
		self.keyOnce = ControlInterface().keyOnce.copy()


class ExitMenu(Menu):

	def __init__(self):
		global doCharCall
		doCharCall = False
		Menu.__init__(self)
		self.zindex = 100

	def getMenu(self):
		self.itemlist = []
		self.rect = Rect(240, 240, 160, -1)
		self.help = u"Exit game?"
		self.itemlist.append( MenuItem(u"exit", "end") )
		self.itemlist.append( MenuItem(u"continue", "continue") )

	def action(self):
		Menu.action(self)
		cmd = self.itemlist[self.itemsel].cmd
		if cmd == 'continue':
			menuMgr.pop()
		elif cmd == 'end':
			exit()

	def __del__(self):
		global doCharCall
		doCharCall = True


class MenuManager:

	def __init__(self):
		self.menulist = []
		self.menuHideList = [-1]
		self.memItemsel = {}
		self.memScroll_pos = {}
		self.session = {}
		self.gNaviList = []
		self.helpfontsize = 16
		self.helpfont = pygame.font.Font(g.config.fontpath, self.helpfontsize)

	def add(self, menu, doConnect=False):
		if menu.__class__ is tuple or menu.__class__ is list:
			self.menulist.append(menu)
		else:
			listmenu = []
			listmenu.append(menu)
			self.menulist.append(listmenu)

		if doConnect:
			self.post(self, ["connect", menu.__class__.__name__])
		self.menuHideList.append(self.menuHideList[-1])

	def disconnect(self):
		controller.disconnect()

	def getAllMenu(self):
		menulist = []
		for menublock in self.menulist:
			for menu in menublock:
				menulist.append(menu)

		return menulist

	def getMenuByName(self, className):
		for menu in self.getAllMenu():
			trace(DL2, 'getMenuByName: ' + `menu`)
			if isclass(menu, className):
				return menu

		return None

	def pop(self):
		menu = self.menulist.pop()

		for m in menu:
			if hasattr(m, "itemsel"):
				if m.connection:
					key = m.__class__.__name__
					if hasattr(m, "idtag"):
						if m.idtag != None:
							key += `m.idtag`
					self.memItemsel[key] = m.itemsel
					self.memScroll_pos[key] = m.scroll_pos

		controller.disconnect()
		self.menuHideList.pop()
		if len(self.gNaviList) >= 1:
			self.gNaviList.pop()

	def call(self):
		if len(self.menulist) == 0:
			return

		for menu in self.getAllMenu():
			menu.call()

		for menu in self.getAllMenu():
			if controller.link is menu:
				menu.win.setMode(1)
			else:
				menu.win.setMode(0)

	def post(self, transmitter, message):
		cmd, prm = message[0], message[1:]
		trace(DL2, "post cmd: "+ `cmd`)

		if cmd == 'connect':
			className = prm[0]
			for menu in self.getAllMenu():
				trace(DL2, "menuMgr.post.menu class name:" + menu.__class__.__name__)
				if menu.__class__.__name__ == className:
					g.controller.connect(menu)
					if hasattr(menu, "itemsel"):
						key = menu.__class__.__name__
						if hasattr(menu, "idtag"):
							if menu.idtag != None:
								key += `menu.idtag`
						if self.memItemsel.has_key(key):
							menu.itemsel = self.memItemsel[key]
							menu.scroll_pos = self.memScroll_pos[key]
							menu.olditemsel = copy(menu.itemsel)
							menu.old_scroll_pos = copy(menu.scroll_pos)
							menu.onSelChange(True)
			print "menulist: ", self.menulist
		elif cmd == 'hide':
			self.menuHideList[-1] = prm[0]
		else:
			for menu in self.getAllMenu():
				menu.receive(message)

	def draw(self, screen, campos=(0,0)):
		cnt = 0
		sortedMenulist = []
		for menulist in self.menulist:
			for menu in menulist:
				sortedMenulist.append(menu)

		sortedMenulist.sort(self.cmpHideLevel)
		for menu in sortedMenulist:
			if menu.zindex > self.menuHideList[-1]:
				menu.draw(screen, campos)

		str = ""

	def cmpHideLevel(self, A, B):
		if A.zindex > B.zindex:
			return 1
		elif A.zindex == B.zindex:
			return 0

		return -1

	def reload(self):
		for menu in self.getAllMenu():
			menu.reload()

	def free(self):
		while(len(self.menulist) > 0):
			menu = self.pop()

		self.menuHideList = [-1]
		self.gNaviList = []



class SoundItem:

	def __init__(self, id, name, filepath):
		self.id = id
		self.name = name
		self.filepath = filepath



class Sound:

	def __init__(self, filepath):
		self.filebuf = loadFileToList(filepath)
		self.musiclist = {}
		self.selist = {}
		self.soundlist = {}

		for line in self.filebuf:
			block = string.split(line, ',')
			type = block[0]
			num = int(block[1])
			title = block[2]
			filename = block[3]
			if type == "music":
				self.musiclist[num] = SoundItem(num, title, filename)
			else:
				self.selist[num] = SoundItem(num, title, filename)
				if pygame.mixer.get_init() != None:
					self.soundlist[num] = loadSound(filename)

	def playMusic(self, num):
		if pygame.mixer.get_init() != None:
			pygame.mixer.music.stop()
			loadMusic(self.musiclist[int(num)].filepath)
			playMusic(-1)

	def playSound(self, num):
		if pygame.mixer.get_init() != None:
			self.soundlist[num].play()

	def stopMusic(self):
		if pygame.mixer.get_init() != None:
			pygame.mixer.music.stop()



class SceneInterface(ControlInterface):

	def __init__(self):
		ControlInterface.__init__(self)
		self.order = 0
		pass

	def call(self):
		pass

	def display(self):
		pass



class SceneTitle(SceneInterface):

	def __init__(self):
		SceneInterface.__init__(self)
		self.order = 1000

		g.sound.playMusic(1)


	def call(self):

		for e in g.state.event:

			if (e.type == KEYDOWN and e.key == K_z):
				g.sceneMgr.add(SceneStage())
				g.sceneMgr.remove(SceneTitle)


	def display(self):
		g.screen.blit(g.img["title"], (0, 0))
		pass



class SceneStage(SceneInterface):

	def __init__(self):
		SceneInterface.__init__(self)

		g.sound.playMusic(1)

		self.player = Char(g.img["char"], FRect(12*CS,8*CS,CS,CS), (0,5*CS,CS,CS))
		g.controller.connect(self)

	def call(self):
		# player move
		if (self.key[UP]):
			self.player.move(0, -1)
		if (self.key[DOWN]):
			self.player.move(0, 1)
		if (self.key[LEFT]):
			self.player.move(-1, 0)
		if (self.key[RIGHT]):
			self.player.move(1, 0)
		#self.player.setPos(100+100*math.cos(g.counter/100.0), 100+100*math.sin(g.counter/100.0))

	def display(self):
		g.screen.blit(g.img["stage1"], (0, 0))
		g.screen.blit(g.img["char"], (0, 160))
		self.player.display();
		pass



class SceneSystem(SceneInterface):

	def __init__(self):
		SceneInterface.__init__(self)
		self.order = -100
		self.fullscreenFlag = False

	def call(self):
		g.clock.tick(g.config.fps)
		g.state.fps = g.clock.get_fps()

		g.state.event = pygame.event.get()
		mousex, mousey = pygame.mouse.get_pos()

		for e in g.state.event:
			if e.type == QUIT:
				exit()

			if (e.type == KEYDOWN and e.key == K_ESCAPE):
				if g.menuMgr.getMenuByName('ExitMenu') == None:
					g.menuMgr.add(ExitMenu(), True)

			elif (e.type == KEYDOWN and e.key == K_s):
				global pauseflag
				pauseflag = not pauseflag

			elif (e.type == KEYDOWN and e.key == K_a):
				if (self.fullscreenFlag == False):
					screen = pygame.display.set_mode((320,240), pygame.FULLSCREEN)
					self.fullscreenFlag = True
				else:
					screen = pygame.display.set_mode((320,240))
					self.fullscreenFlag = False

			"""
			elif (e.type == KEYDOWN and e.key == K_a):
				if gameinfo.state == BATTLE:
					btlMgr.onBattleEnd()
				else:
					if len(menuMgr.menulist) <= 1:
						menuMgr.add(DebugMenu(), True)
			"""

	def display(self):
		g.screen.fill((0, 0, 0))



class SceneDebug(SceneInterface):

	def __init__(self):
		SceneInterface.__init__(self)
		self.order = 100
		self.mesPosY = 0

	def call(self):
		pass
		#self.mesPosY = 100 * math.sin(math.pi * 0.1 * g.counter  )

	def display(self):
		mes("fps:"+`g.state.fps`, (0, CS))




class SceneManager:

	def __init__(self):
		self.sceneList = []

	def add(self, scene):
		self.sceneList.append(scene)

	def remove(self, classPrototype):
		counter = 0
		for scene in self.sceneList:
			if (isinstance(scene, classPrototype)):
				self.sceneList.pop(counter)
				return
			counter += 1

	def call(self):
		self.sceneList.sort(self._compareOrder)
		for scene in self.sceneList:
			scene.call()

	def display(self):
		for scene in self.sceneList:
			scene.display()

	def _compareOrder(self, x, y):
		return x.order - y.order

	def clear(self):
		self.sceneList = []


class State:

	def __init__(self):
		self.fps = 0


class FRect:

	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.cX = x + (w / 2.0)
		self.cY = y + (h / 2.0)

	def __getitem__(self, index):
		if index == 0:
			return self.x
		elif index == 1:
			return self.y
		elif index == 2:
			return self.w
		elif index == 3:
			return self.h

	def __len__(self):
		return len(self.__dict__)


class Char:

	def __init__(self, srcSurface, dest=FRect(0,0,0,0), src=FRect(0,0,0,0)):
		self.dest = dest
 		self.src = src
 		self.collision = dest
 		self.surface = srcSurface

	def move(self, x, y):
		self.dest.x += x
		self.dest.y += y

	def setPos(self, x, y):
		self.dest.x = x
		self.dest.y = y

	def display(self):
		g.screen.blit(self.surface, (self.dest.x, self.dest.y), self.src)



class Game:

	def __init__(self):
		pass

	def run(self):
		g.config = Config()
		g.state = State()

		g.img = {}
		g.img["event"] = None
		g.img["char"] = None
		g.img["enemy"] = None
		g.img["alpha"] = None

		g.counter = 0

		mousex =	0
		mousey = 0

		if g.config.gDebugLevel >= DL1:
			sys.stdout = file("stdout.txt", "w")

		print "DebugLevel: " + `g.config.gDebugLevel`

		self.initPygame()
		self.logEnv()
		self.loadDataFile();

		self.controller = Controller()
		self.menuMgr = MenuManager()
		g.sceneMgr = SceneManager()
		g.sceneMgr.add(SceneTitle())
		g.sceneMgr.add(SceneSystem())
		g.sceneMgr.add(SceneDebug())

		self.mainLoop()

	def mainLoop(self):
		while 1:
			g.controller.call()
			g.sceneMgr.call()
			g.sceneMgr.display()
			pygame.display.flip()
			g.counter += 1

	def initPygame(self):
		disp_size			 = 320, 240

		# Pygame initialize
		pygame.mixer.pre_init(g.config.music_freq, g.config.music_bits, 2, 2048)
		initRes = pygame.init()
		trace(DL0, "init result: " + `initRes`)
		trace(DL0, pygame.mixer.get_init())
		if pygame.mixer.get_init() != None:
			pygame.mixer.music.set_volume(g.config.music_volume)
		trace(DL1, 'mixer.get_init(): ' + `pygame.mixer.get_init()`)

		# Screen
		g.screen = pygame.display.set_mode(disp_size, g.config.disp_flags, g.config.disp_bpp)
		pygame.mouse.set_visible(g.config.doMouseView)

		# Font
		g.font = pygame.font.Font(g.config.fontpath, 24)

		# Joy Stick
		pygame.joystick.init()
		trace(DL0, 'joystick_module_init: ' + `pygame.joystick.get_init()`)
		joypad_num = pygame.joystick.get_count()
		trace(DL1, "joypad_num: " + `joypad_num`)
		g.joypad = None
		if joypad_num >= 1:
			g.joypad = pygame.joystick.Joystick(0)
			trace(DL2, 'joypad_name: ' + `g.joypad.get_name()`)
			trace(DL2, 'joypad_id: ' + `g.joypad.get_id()`)
			g.joypad.init()
			trace(DL0, 'joypad_init: ' + `g.joypad.get_init()`)
			joypad_num_buttons = g.joypad.get_numbuttons()
			joypad_num_hats = g.joypad.get_numhats()
			trace(DL1, "joypad_num_buttons: " + `joypad_num_buttons`)
			trace(DL1, "joypad_num_hats: " + `joypad_num_hats`)

		#Timer
		g.clock = pygame.time.Clock()

	def logEnv(self):
		trace(DL2, g.config.display())
		trace(DL2, 'builtin_module_names: \t' + `sys.builtin_module_names`)
		trace(DL2, 'copyright : \t' + `sys.copyright`)
		trace(DL2, 'path : \t' + `sys.path`)
		trace(DL2, 'platform : \t' + `sys.platform`)
		trace(DL2, 'version : \t' + `sys.version`)

	def loadDataFile(self):
		FILEPATH_MUSICLIST	 = os.path.join(DATA_DIRECTORY, "musiclist.csv")
		FILEPATH_EVENTLIST	 = os.path.join(DATA_DIRECTORY, "mo.xml")
		FILEPATH_ITEMLIST	 = os.path.join(DATA_DIRECTORY, 'itemlist.csv')
		FILEPATH_CHARDATA	 = os.path.join(DATA_DIRECTORY, 'charlist.csv')

		savefileVer = 0.01
		saveFileDir = "save"
		saveFilenameHead = "emsave"
		saveFileExt = ".dat"

		# load Image
		filelist = getfilelist(IMAGE_DIRECTORY)
		f_filelist = extfilter(filelist, ['png','PNG'])
		for path in f_filelist:
			filename = os.path.splitext( os.path.split(path)[1] )[0]
			g.img[filename] = pygame.image.load(path)
			if filename[-2:] != "_a":
				g.img[filename].convert_alpha()
			else:
				g.img[filename].convert()
				#g.img[filename].set_colorkey((0,0,0))
				g.img["char"].set_colorkey(g.img["char"].get_at((0, 0)))

		g.sound = Sound(FILEPATH_MUSICLIST)



def drawRect(screen, rect, color_A, color_B):
	color = [0,0,0]
	for i in range(rect.h):
		for j in range(3):
			color[j] = (color_A[j] * (rect.h-i) + color_B[j] * i) / rect.h
		screen.fill(color, (rect.x, rect.y + i, rect.w, 1))

def trace(level, message):
	if g.config.gDebugLevel >= level:
		print "[DL"+`level`+"]",message

def render(font, str, type, color, bgcolor=(64,64,64,255)):
	if str != "":
		ren = font.render(str, g.config.fonttype, color, bgcolor)
		if ren != None:
			ren.set_colorkey(bgcolor)
			ren.set_alpha(None)
		return ren

	return pygame.Surface((0,0))


def isclass(obj, classname):
	if obj.__class__.__name__ == classname:
		return True
	else:
		return False

def drawText(surface, font, text, pos=(0,0), color=(255,255,255)):
	ren = render(font, text, fonttype, color)
	surface.blit(ren, pos)
	return ren.get_size()

def mes(text, pos=(0,0), color=(255,255,255)):
	ren = render(g.font, text, g.config.fonttype, color)
	g.screen.blit(ren, pos)
	return ren.get_size()

def loadFileToList(filepath):
	filebuf = []

	f = open(filepath, 'r')
	while 1:
		line = f.readline()
		if line == "":
			break
		if (line[0] == "#") | (line[0] == "\n") | (line[0] == "\r"):
			continue
		line = line.replace("\n", "")
		line = line.replace("\r", "")

		filebuf.append( unicode(line.rstrip("\n"), 'Shift_JIS') )
	f.close()
	return filebuf



def loadImage(name, colorkey=None):
	try:
		image = pygame.image.load(name)
	except pygame.error, message:
		print 'load image failed: image path:', name
		raise SystemExit, message

	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	rect = image.get_rect()

	return image, Size(rect.w, rect.h)

def loadCharImage(name, colorkey=None, surface=None):
	s_char = None
	if surface == None:
		s_char, size = loadImage(name, colorkey)
	else:
		s_char = surface

	return s_char, size

def loadMusic(name):
	fullname = os.path.join('music', name)
	try:
		pygame.mixer.music.load(fullname)
	except pygame.error, message:
		print 'load music failed, file path: ', fullname
		raise SystemExit, message

	return

def loadSound(name):
	class NoneSound:
		def play(self): pass

	if not pygame.mixer:
		return NoneSound()

	fullname = os.path.join('se', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'load sound failed, file path:', wav
		raise SystemExit, message

	return sound

def playMusic(loops=0, startpos=0.0):
	pygame.mixer.music.play(loops, startpos)

def setTitle(mes):
	pygame.display.set_caption(mes)


def exit():
	pygame.quit()
	sys.exit()

def drawRect(screen, rect, color_A, color_B):
	color = [0,0,0]
	for i in range(rect.h):
		for j in range(3):
			color[j] = (color_A[j] * (rect.h-i) + color_B[j] * i) / rect.h
		screen.fill(color, (rect.x, rect.y + i, rect.w, 1))

def checkKeyCmd(buf, p, pattern):
	flag = True
	for i in range(len(pattern)):
		if buf[p - i] <> pattern[-i]:
			flag = False

	return flag

def fmtStr(text,num):
	buf = u''
	for i in range(len(text), num):
		buf += u' '
	buf += text
	return buf



def curdir():
	return os.listdir('.')

def dir(path):
	return os.listdir(path)


def getfilelist(path):
	list = os.listdir(path)
	pathlist = [ os.path.join(path, x) for x in list]
	return filter(lambda x:os.path.isfile(x), pathlist)


def abspath(pathlist):
	for i in range(len(pathlist)):
		pathlist[i] = os.path.abspath(pathlist[i])

	return pathlist

def extfilter(filelist, extlist):
	return filter(lambda x: os.path.splitext(x)[1][1:] in extlist, filelist)

def textlinesToList(lines):
	lst = lines.split("")
	for i in range(len(lines)):
		line = f.readline()
		if line == "":
			break
		line = line.replace("\n", "")
		line = line.replace("\r", "")
		filebuf.append( unicode(line, 'japanese.shift-jis') )



if __name__ == '__main__':

	g = Game()

	if (len(sys.argv) == 1):
		g.run()
	else:
		if sys.argv[1] == "profile":
			profile.run('g.run()')