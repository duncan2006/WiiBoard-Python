#!/usr/bin/python
"""scalesgui.py
"""

import sys

sys.path.insert(0, '/home/cwiid_lib')

try:
	import pygame
except:
	print "Sorry, I can't seem to import pygame for some reason."
	print "Please check that the python-pygame package is installed, or get the latest version of pygame from http://www.pygame.org/"
	sys.exit(1)
	
try:
	import cwiid
except:
	print "Sorry, I can't seem to import cwiid for some reason."
	print "Please check that it and it's python bindings are installed, and also the balance board patch from:"
	print "http://abstrakraft.org/cwiid/ticket/63"
	sys.exit(1)

import os, math, random
import time as ptime
from pygame.locals import *
from ConfigParser import ConfigParser
from threading import Thread
#import wiimenu

class WeightSprite(pygame.sprite.Sprite):
	"""This class describes a sprite containing the weight."""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.weight = 0.0
		self.update()
		
	def update(self):
		global screen_res, sys_font_weight_fgcolour, sys_font_weight, screen_res
		
		if self.weight > 2:
			if lbs_kg:
				self.text = "%.2f" % self.weight + " kg"
			else:
				self.text = "%.2f" % self.weight + " lbs"
		else:
			self.text = "_.__"
			#print "LESS THAN 2"
		#while len(self.text) < 4:
		#	self.text = "0" + self.text
			
		self.image = sys_font_weight.render(self.text, True, sys_font_weight_fgcolour)

		self.rect = self.image.get_rect()
		self.rect.bottomright = screen_res

class BMIsprite(pygame.sprite.Sprite):
	"""This class describes a sprite containing the BMI."""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.bmi = 0.0
		self.update()
		
	def update(self):
		global screen_res, sys_font_weight_fgcolour, sys_font_weight, screen_res
		
		if self.bmi > 1:
			self.text = "%.2f" % self.bmi + " BMI"
		else:
			self.text = "_.__"
			#print "LESS THAN 2"
		#while len(self.text) < 4:
		#	self.text = "0" + self.text
			
		self.image = sys_font_weight.render(self.text, True, sys_font_weight_fgcolour)

		self.rect = self.image.get_rect()
		self.rect.bottomleft = (0, 600)


def quit_app():
	pygame.quit()
	sys.exit(0)
	
def calcweight( readings, calibrations ):
	"""
	Determine the weight of the user on the board in hundredths of a kilogram
	"""
	weight = 0
	for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
		reading = readings[sensor]
		calibration = calibrations[sensor]
		#if reading < calibration[0]:
		#	print "Warning, %s reading below lower calibration value" % sensor
		if reading > calibration[2]:
			print "Warning, %s reading above upper calibration value" % sensor
		# 1700 appears to be the step the calibrations are against.
		# 17kg per sensor is 68kg, 1/2 of the advertised Japanese weight limit.
		if reading < calibration[1]:
			weight += 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
		else:
			weight += 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700

	return weight
	
def gsc(readings, pos):
	global named_calibration
	reading = readings[pos]
	calibration = named_calibration[pos]
	
	if reading < calibration[1]:
		return 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
	else:
		return 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700
		
	
print "Please press the red 'connect' button on the balance board, inside the battery compartment."
print "Do not step on the balance board."

global wiimote
if len(sys.argv) > 1:
	wiimote = cwiid.Wiimote(sys.argv[1])
else:
	wiimote = cwiid.Wiimote()

wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
wiimote.request_status()

'''if wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
	print 'This program only supports the Wii Balance Board'
	wiimote.close()
	sys.exit(1)
'''
balance_calibration = wiimote.get_balance_cal()
named_calibration = { 'right_top': balance_calibration[0],
					  'right_bottom': balance_calibration[1],
					  'left_top': balance_calibration[2],
					  'left_bottom': balance_calibration[3],
					}

system_file = "system.ini"

if not os.path.lexists(system_file):
	print "Problem: System configuration file (system.ini) doesn't exist."
	sys.exit(1)

sconf = ConfigParser()
sconf.read(system_file)


xdisplay = sconf.get("display", "xdisplay")
if len(xdisplay) > 1:
	# using alternate display.
	print "Attempting to use device", xdisplay, "instead of the default."
	os.putenv("DISPLAY", xdisplay)

pygame.init()

sys_font_weight = pygame.font.SysFont(sconf.get("font_weight", "face"), int(sconf.get("font_weight", "size")))

sys_font_weight.set_italic(False)
sys_font_weight.set_underline(False)

bgcolour = (0, 0, 0)
sys_font_weight_fgcolour = (255, 255, 255)
screen_res = (int(sconf.get("display", "width")), int(sconf.get("display", "height")))
refresh_delay = int(sconf.get("display", "refresh_delay"))

screen_options = 0
if int(sconf.get("display", "fullscreen")) >= 1 and len(xdisplay) <= 1:
	screen_options = screen_options | pygame.FULLSCREEN

if int(sconf.get("display", "double_buffers")) >= 1:
	screen_options = screen_options | pygame.DOUBLEBUF

if int(sconf.get("display", "hardware_surface")) >= 1:
	screen_options = screen_options | pygame.HWSURFACE

if int(sconf.get("display", "opengl")) >= 1:
	screen_options = screen_options | pygame.OPENGL

screen = pygame.display.set_mode(screen_res, screen_options)
pygame.display.set_caption("Weight Tracker")

weight_sprite = WeightSprite()
BMI_sprite = BMIsprite()
weight_sprite.weight = 00.00
BMI_sprite.bmi == 00.00
frame = 0
lbs_kg = 0

feet = 6
inches = 0

#Game loop
while True:
	for event in pygame.event.get():
		#Quit with F12
		if event.type == KEYDOWN:
			if event.key == K_F12:
				quit_app()
			elif event.key == K_F11:
				lbs_kg = not(lbs_kg)
				
	wiimote.request_status()
	frame = frame + 1
	if frame == 50:
		frame = 0
		weight = (calcweight(wiimote.state['balance'], named_calibration) / 100.0)
		weight_lbs = (weight * 2.20462262)


#English Units: BMI = Weight (lb) / (Height (in) x Height (in)) x 703 
		#print "%.2fkg" % weight
		if lbs_kg:
			weight_sprite.weight = weight
			#BMI_sprite.bmi =
		else:
			weight_sprite.weight = weight_lbs
			#BMI_sprite.bmi = (int(wiimenu.profile_feet)*12)+int(profile_inches)
			BMI_sprite.bmi = ((weight_lbs) / ((feet*12.0 + inches)**2)) * 703
	
	readings = wiimote.state['balance']
	
	#print "readings:",readings

	screen.fill(bgcolour) # blank the screen.
	
	weight_sprite.update()
	BMI_sprite.update()
	
	screen.blit(weight_sprite.image, weight_sprite.rect)
	screen.blit(BMI_sprite.image, BMI_sprite.rect)

	pygame.display.flip()
	pygame.time.wait(refresh_delay)	


