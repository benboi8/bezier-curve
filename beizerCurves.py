import pygame as pg
from pygame import gfxdraw
import random
pg.init()

clock = pg.time.Clock()
fps = 20

sf = 2
width, height = 640 * sf, 360 * sf
screen = pg.display.set_mode((width, height))

black = (0, 0, 0)
white = (255, 255, 255)
red = (205, 0, 0)
green = (0, 205, 0)
blue = (0, 0, 205)
lightBlue = (0, 167, 205)
yellow = (205, 205, 0)
darkGreen = (60, 200, 60)
darkGray = (55, 55, 55)
lightGray = (205, 205, 205)
running = True

bezierCurves = []

colors = {
	0: red,
	1: green,
	2: blue,			
	3: lightGray,			
	4: white,			
	5: black		
}

def DrawRectOutline(surface, color, rect, width=1, outWards=False):
	x, y, w, h = rect
	width = max(width, 1)  # Draw at least one rect.
	width = min(min(width, w//2), h//2)  # Don't overdraw.

	# This draws several smaller outlines inside the first outline
	# Invert the direction if it should grow outwards.
	if outWards:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x-i, y-i, w+i*2, h+i*2), color)
	else:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x+i, y+i, w-i*2, h-i*2), color)


def DrawObround(surface, color, rect, filled=False, additive=True, vertical=False):
	if not vertical:
		x, y, w, h = rect
		radius = h // 2	
		# check if semicircles are added to the side or replace the side
		if not additive:
			x += radius
			w -= radius * 2
		# checks if it should be filled
		if not filled:
			pg.draw.aaline(surface, color, (x, y), (x + w, y), 3 * sf)
			pg.draw.aaline(surface, color, (x, y + h), (x + w, y + h), 3 * sf)
			pg.gfxdraw.arc(surface, x, y + radius, radius, 90, -90, color)
			pg.gfxdraw.arc(surface, x + w, y + radius, radius, -90, 90, color)
		else:
			pg.gfxdraw.filled_circle(surface, x, y + radius, radius, color)	
			pg.gfxdraw.filled_circle(surface, x + w, y + radius, radius, color)	
			pg.draw.rect(surface, color, (x, y, w, h))	
	else:
		x, y, w, h = rect
		radius = w // 2	
		# check if semicircles are added to the side or replace the side
		if not additive:
			y += radius
			h -= radius * 2
		# checks if it should be filled
		if not filled:
			pg.draw.aaline(surface, color, (x, y), (x, y + h), 3 * sf)
			pg.draw.aaline(surface, color, (x + w, y), (x + w, y + h), 3 * sf)
			pg.gfxdraw.arc(surface, x + radius, y, radius, 180, 360, color)
			pg.gfxdraw.arc(surface, x + radius, y + h, radius, 0, 180, color)
		else:
			pg.gfxdraw.filled_circle(surface, x + radius, y, radius, color)	
			pg.gfxdraw.filled_circle(surface, x + radius, y + h, radius, color)	
			pg.draw.rect(surface, color, (x, y, w, h))	


class Curve:
	def __init__(self, surface, color, step, points):
		self.surface = surface
		self.color = color
		self.step = step
		self.points = points
		self.drawLines = False
		self.activePoint = None
		self.pointRects = []
		for point in self.points:
			rect = pg.Rect(point[0], point[1], 6 * sf, 6 * sf)
			rect.x -= rect.w // 2
			rect.y -= rect.h // 2
			self.pointRects.append(rect)

		bezierCurves.append(self)

	def Draw(self):
		if self.drawLines:
			pg.gfxdraw.bezier(self.surface, self.points, self.step, self.color)
			for i in range(len(self.points)):
				pg.draw.circle(self.surface, self.color, self.points[i], 3 * sf)
				if i + 1 >= len(self.points):
					pg.draw.aaline(self.surface, self.color, self.points[i], self.points[i - 1])
				else:
					pg.draw.aaline(self.surface, self.color, self.points[i], self.points[i + 1])
		else:
			pg.gfxdraw.bezier(self.surface, self.points, self.step, lightGray)

		# for rect in self.pointRects:
			# pg.draw.rect(self.surface, red, rect)


	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				activePointCheck = True
				for curve in bezierCurves:
					if curve.activePoint != None:
						activePointCheck = False

				if activePointCheck:
					for rect in self.pointRects:
						if rect.collidepoint(pg.mouse.get_pos()):
							self.activePoint = self.pointRects.index(rect)
							break
						else:
							self.activePoint = None

		if self.activePoint != None:
			rect = self.pointRects[self.activePoint]
			point = self.points[self.activePoint]
			point = (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
			rect.x, rect.y = point[0] - rect.w // 2, point[1] - rect.h // 2
			self.points[self.activePoint] = point

		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				self.activePoint = None

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_SPACE:
				self.drawLines = not self.drawLines


def MakePoints(number, startPos, endPos, points=[]):
	if len(points) == 0:
		points = [startPos]
		for i in range(number):
			points.append((random.randint(min(startPos[0], endPos[1]), max(startPos[0], endPos[1])), random.randint(min(endPos[0], startPos[1]), max(endPos[0], startPos[1]))))
		points.append(endPos)

	else:
		points.insert(0, startPos)
		points.insert(-1, endPos)

	if len(bezierCurves) >= 1:
		bezierCurves.pop(0)
	Curve(screen, colors[random.randint(0, len(colors) - 1)], 20, points)


def DrawLoop():
	global board
	screen.fill(darkGray)

	for curve in bezierCurves:
		curve.Draw()

	pg.display.update()

for j in range(4):
	startPoint = ((j + 1) * 50 * sf, (j + 1) * 25 * sf)
	points = [startPoint]
	for i in range(4):
		point = (startPoint[0] + (i + 1) * (50 * sf), startPoint[1])
		points.append(point)

	Curve(screen, colors.get(j, lightGray), 10, points) 
	
while running:
	clock.tick_busy_loop(fps)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

		for curve in bezierCurves:
			curve.HandleEvent(event)



	DrawLoop()
