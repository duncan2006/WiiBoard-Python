#!/usr/bin/python
"""scalesgui.py
"""

import sys, time, math, random
from menu import *
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
   
sys_font_weight = None
sys_font_weight_fgcolour = None
screen_res = None
named_calibration = None

import os, math, random
import time as ptime
from pygame.locals import *
from ConfigParser import ConfigParser
from threading import Thread
		
class WeightSprite(pygame.sprite.Sprite):
	"""This class describes a sprite containing the weight."""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.weight = 0.0
		self.update()
		
	def update(self):
		global screen_res, sys_font_weight_fgcolour, sys_font_weight, screen_res
		
		if self.weight > 2:
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
      #   print "Warning, %s reading below lower calibration value" % sensor
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
      
def connect_wiiboard(screen):
   screen.fill(BLACK)   
   desc_font = pygame.font.Font(None, 24)    # Font to use
   screen.blit(desc_font.render("Please press the red 'connect' button on the balance board, inside the battery compartment.", True, WHITE), (15, 330)) 
   pygame.display.flip()
   global wiimote
   #print "Do not step on the balance board."
   #wiimote = None
   try:
      wiimote = cwiid.Wiimote()
      connected = True
   except:
      screen.fill(BLACK)   
      screen.blit(desc_font.render("Failed to connect, please try again.", True, WHITE), (250, 330)) 
      pygame.display.flip()
      print 'exception'
      time.sleep(1.5)
      return False
      
   screen.fill(BLACK)   
   screen.blit(desc_font.render("Please press the red 'connect' button on the balance board, inside the battery compartment.", True, WHITE), (15, 330)) 
   pygame.display.flip()
   return True
      
      
def dynamic_balance(screen):
   global wiimote, named_calibration
   if wiimote == None:
      return
   wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
   wiimote.request_status()
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

   #pygame.init()
   global sys_font_weight, sys_font_weight_fgcolour, screen_res
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
   
   #screen = pygame.display.set_mode(screen_res, screen_options)
   #pygame.display.set_caption("dynamic balance")

   weight_sprite = WeightSprite()
   weight_sprite.weight = 40.33
   frame = 0
   boxes_completed=0
   box_start=0
   start_time = time.time()
   
   random.seed()
   
   x_size = 150
   y_size = 150      
   min_x = random.randrange(0, screen_res[0]-x_size, 1)
   max_x = min_x + x_size
   min_y = random.randrange(0, screen_res[1]-y_size, 1)
   max_y = min_y + y_size 
   while True:
      for event in pygame.event.get():
         if event.type == KEYDOWN:
            return
      
      
      
      wiimote.request_status()
      frame = frame + 1
   
      readings = wiimote.state['balance']
      
      try:
         x_balance = (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'left_bottom')))
         if x_balance > 1:
            x_balance = (((float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))))*-1.)+1.
         else:
            x_balance = x_balance -1.
         y_balance = (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'right_top')))
         if y_balance > 1:
            y_balance = (((float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))))*-1.)+1.
         else:
            y_balance = y_balance -1.
      except:
         x_balance = 1.
         y_balance = 1.
   

      screen.fill(bgcolour) # blank the screen.
   
      xpos = (x_balance * (screen_res[0]/2)) + (screen_res[0]/2)
      ypos = (y_balance * (screen_res[1]/2)) + (screen_res[1]/2)
      
      
      #draw the box to stay in
      pygame.draw.rect(screen, (0,0,255), (min_x, min_y, x_size, y_size), 0)
      
      cur_time = time.time()
      if (xpos >= min_x and xpos <= max_x) and (ypos >= min_y and ypos <= max_y):
         if box_start == 0:
            box_start = cur_time
      else:
         box_start = 0
         
      if cur_time - box_start > 3 and box_start != 0:
         boxes_completed = boxes_completed + 1
         x_size = x_size-25
         y_size = y_size-25
         if x_size < 10:
            x_size = 10
            y_size = 10
         
         box_start = 0
         min_x = random.randrange(0, screen_res[0]-x_size, 1)
         max_x = min_x + x_size
         min_y = random.randrange(0, screen_res[1]-y_size, 1)
         max_y = min_y + y_size 
         
         
         
      if cur_time - start_time > 30:
         return         
         
      pygame.draw.circle(screen, (255,0,0), (int(xpos), int(ypos)), 5)
      
      time_left = 30 - (cur_time-start_time)
      time_disp = "%.2f" % time_left      
      font = pygame.font.Font(None, 24)
      screen.blit(font.render(time_disp, True, WHITE), (15, 30)) 
      
      if box_start != 0:
         box_time = cur_time - box_start
      else:
         box_time = 0
      
      box_disp = "%.2f" % box_time
      screen.blit(font.render(box_disp, True, WHITE), (600, 30))
      
      pygame.display.flip()
      pygame.time.wait(refresh_delay)

def stop_go(screen):
   global wiimote, named_calibration
   if wiimote == None:
      return
   wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
   wiimote.request_status()
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

   #pygame.init()
   global sys_font_weight, sys_font_weight_fgcolour, screen_res
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
   
   #screen = pygame.display.set_mode(screen_res, screen_options)
   #pygame.display.set_caption("dynamic balance")

   weight_sprite = WeightSprite()
   weight_sprite.weight = 40.33
   frame = 0
   start_time = time.time()
   cur_time = start_time
   random.seed()
   go = random.randrange(3, 7, 1)
   stop = random.randrange(2, 5, 1)
   
   go_end_time = go + cur_time
   stop_end_time = stop + go + cur_time
   while True:
      for event in pygame.event.get():
         if event.type == KEYDOWN:
            return     
      
      wiimote.request_status()
      frame = frame + 1
   
      readings = wiimote.state['balance']
      
      try:
         x_balance = (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'left_bottom')))
         if x_balance > 1:
            x_balance = (((float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))))*-1.)+1.
         else:
            x_balance = x_balance -1.
         y_balance = (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'right_top')))
         if y_balance > 1:
            y_balance = (((float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))))*-1.)+1.
         else:
            y_balance = y_balance -1.
      except:
         x_balance = 1.
         y_balance = 1.
   

      screen.fill(bgcolour) # blank the screen.
   
      xpos = (x_balance * (screen_res[0]/2)) + (screen_res[0]/2)
      ypos = (y_balance * (screen_res[1]/2)) + (screen_res[1]/2)
      
      
      cur_time = time.time()
      
      #draw the box to stay in
      if cur_time < go_end_time:
         if xpos < (screen_res[0]/2)-100:
            pygame.draw.rect(screen, (0,0,255), (screen_res[0]/2, 0, screen_res[0]/2, screen_res[1]), 0)
         elif xpos > (screen_res[0]/2)+100:           
            pygame.draw.rect(screen, (0,0,255), (0, 0, screen_res[0]/2, screen_res[1]), 0)
                  
         
      if cur_time - start_time > 30:
         return         
         
      time_left = 30 - (cur_time-start_time)
      time_disp = "%.2f" % time_left      
      font = pygame.font.Font(None, 24)
      screen.blit(font.render(time_disp, True, WHITE), (15, 30)) 
      
      if (cur_time < go_end_time):
         pygame.draw.circle(screen, (0,255,0), (screen_res[0]/2, 25), 20)
      else:
         pygame.draw.circle(screen, (255,0,0), (screen_res[0]/2, 25), 20)
      
      pygame.display.flip()
      pygame.time.wait(refresh_delay)
      
      if cur_time > stop_end_time:
         go = random.randrange(3, 7, 1)
         stop = random.randrange(2, 5, 1)
         go_end_time = cur_time + go
         stop_end_time = cur_time + go + stop


def scalegui(screen):
   print "Please press the red 'connect' button on the balance board, inside the battery compartment."
   print "Do not step on the balance board."

   global wiimote, named_calibration
   if wiimote == None:
      return
   wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
   wiimote.request_status()

   '''
   if wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
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

   #pygame.init()
   global sys_font_weight, sys_font_weight_fgcolour, screen_res
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
   
   #screen = pygame.display.set_mode(screen_res, screen_options)
   pygame.display.set_caption("scales application")

   weight_sprite = WeightSprite()
   weight_sprite.weight = 40.33
   frame = 0
   while True:
	   for event in pygame.event.get():
		   if event.type == KEYDOWN:
			   return
				
	   wiimote.request_status()
	   frame = frame + 1
	   if frame == 50:
		   frame = 0
		   weight = (calcweight(wiimote.state['balance'], named_calibration) / 100.0)
		   #print "%.2fkg" % weight
		   weight_sprite.weight = weight
	
	
	   readings = wiimote.state['balance']
	
	   try:
		   x_balance = (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'left_bottom')))
		   if x_balance > 1:
			   x_balance = (((float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))))*-1.)+1.
		   else:
			   x_balance = x_balance -1.
		   y_balance = (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'right_top')))
		   if y_balance > 1:
			   y_balance = (((float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))))*-1.)+1.
		   else:
			   y_balance = y_balance -1.
	   except:
		   x_balance = 1.
		   y_balance = 1.
	
	   #print "readings:",readings

	   screen.fill(bgcolour) # blank the screen.
	
	   # line up the lines
	   pygame.draw.line(screen, (0,0,255), (screen_res[0]/2,0), (screen_res[0]/2,screen_res[1]), 2)
	   pygame.draw.line(screen, (0,0,255), (0,screen_res[1]/2), (screen_res[0],screen_res[1]/2), 2)
	
	   weight_sprite.update()
	
	   screen.blit(weight_sprite.image, weight_sprite.rect)
	
	   xpos = (x_balance * (screen_res[0]/2)) + (screen_res[0]/2)
	   ypos = (y_balance * (screen_res[1]/2)) + (screen_res[1]/2)
		
	   #print "balance:", x_balance, y_balance
	   #print "position:", xpos,ypos
	   pygame.draw.circle(screen, (255,0,0), (int(xpos), int(ypos)), 5)
	   pygame.display.flip()
	   pygame.time.wait(refresh_delay)
	   
def bodymeasure(screen, height):
   global wiimote, named_calibration
   if wiimote == None:
      return
   wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
   wiimote.request_status()

   '''
   if wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
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

   #pygame.init()
   global sys_font_weight, sys_font_weight_fgcolour, screen_res
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
   
   #screen = pygame.display.set_mode(screen_res, screen_options)
   pygame.display.set_caption("Weight & BMI Measurement")
   
   weight_sprite = WeightSprite()
   BMI_sprite = BMIsprite()
   weight_sprite.weight = 00.00
   BMI_sprite.bmi == 00.00
   frame = 0
   
   screen.fill(bgcolour)
   enter_pressed = False
   
   while (not enter_pressed):
   	for event in pygame.event.get():
   		if event.type == KEYDOWN:
   			if event.key == pygame.K_RETURN:
   				enter_pressed = True;
   	screen.blit(sys_font_weight.render("Press Enter to begin measuring...", True, WHITE), (100, 300))
   	pygame.display.flip()
   	pygame.time.wait(refresh_delay)
   
   start_time = time.time()
   cur_time = time.time()
   
   count = 0
   total_x = 0
   total_y = 0
   total_weight = 0
   total_bmi = 0			

   while ((cur_time - start_time) < 10):
	   for event in pygame.event.get():
		   if event.type == KEYDOWN:
			   return
				
	   wiimote.request_status()
	   frame = frame + 1
	   if frame == 50:
		   frame = 0
		   weight = ((calcweight(wiimote.state['balance'], named_calibration) / 100.0) * 2.20462262) #Weight in lbs
		   #print "%.2fkg" % weight
		   weight_sprite.weight = weight
		   BMI_sprite.bmi = ((weight) / ((height)**2)) * 703
	
	
	   readings = wiimote.state['balance']
	
	   try:
		   x_balance = (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'left_bottom')))
		   if x_balance > 1:
			   x_balance = (((float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))))*-1.)+1.
		   else:
			   x_balance = x_balance -1.
		   y_balance = (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'right_top')))
		   if y_balance > 1:
			   y_balance = (((float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))))*-1.)+1.
		   else:
			   y_balance = y_balance -1.
	   except:
		   x_balance = 1.
		   y_balance = 1.
	
	   #print "readings:",readings

	   screen.fill(bgcolour) # blank the screen.
	   
	   if ((cur_time - start_time) < 5):
	   	screen.blit(sys_font_weight.render("Calibrating, please wait...", True, WHITE), (150, 0))
	   else:
	   	screen.blit(sys_font_weight.render("Measuring, stand still...", True, WHITE), (150, 0))
	
	   # line up the lines
	   pygame.draw.line(screen, (0,0,255), (screen_res[0]/2,0), (screen_res[0]/2,screen_res[1]), 2)
	   pygame.draw.line(screen, (0,0,255), (0,screen_res[1]/2), (screen_res[0],screen_res[1]/2), 2)
	
	   #weight_sprite.update()
	
	   #screen.blit(weight_sprite.image, weight_sprite.rect)
	   
	   weight_sprite.update()
	   BMI_sprite.update()
	
	   screen.blit(weight_sprite.image, weight_sprite.rect)
	   screen.blit(BMI_sprite.image, BMI_sprite.rect)
	   if ((cur_time - start_time) > 5):
	   	total_weight += weight_sprite.weight
	   	total_bmi += BMI_sprite.bmi
	   	
	   xpos = (x_balance * (screen_res[0]/2)) + (screen_res[0]/2)
	   ypos = (y_balance * (screen_res[1]/2)) + (screen_res[1]/2)
	   if ((cur_time - start_time) > 5):
	   	total_x += xpos
	   	total_y += ypos
		
	   #print "balance:", x_balance, y_balance
	   #print "position:", xpos,ypos
	   pygame.draw.circle(screen, (255,0,0), (int(xpos), int(ypos)), 5)
	   pygame.display.flip()
	   pygame.time.wait(refresh_delay)
	   if ((cur_time - start_time) > 5):
	   	count += 1
	   cur_time = time.time()	
   
   screen.fill(bgcolour) # blank the screen.
   # line up the lines
   pygame.draw.line(screen, (0,0,255), (screen_res[0]/2,0), (screen_res[0]/2,screen_res[1]), 2)
   pygame.draw.line(screen, (0,0,255), (0,screen_res[1]/2), (screen_res[0],screen_res[1]/2), 2)
   
   avg_weight = total_weight / count
   avg_bmi = total_bmi / count
   avg_x = total_x / count
   avg_y = total_y / count
   right = (avg_x / screen_res[0]) * 100 #Percent weight on right side
   left = 100 - right					#Left side
   back = (avg_y / screen_res[1]) * 100 #Back
   front = 100 - back					#Front
   cob_score = 500 - ((abs(right-50) + abs(back-50))*10)
     
   bmi_result = "Uncalculated"
   if avg_bmi < 18.5:
   	bmi_result = "Underweight"
   elif avg_bmi < 25:
   	bmi_result = "Normal"
   elif avg_bmi < 30:
   	bmi_result = "Overweight"
   else:
   	bmi_result = "Obese"
   	
   screen.blit(sys_font_weight.render("Press Enter to return to menu...", True, WHITE), (100, 0))
   screen.blit(sys_font_weight.render("Weight: " + "%.2f" % avg_weight + " lbs", True, WHITE), (25, 75))
   screen.blit(sys_font_weight.render("BMI: " + "%.2f" % avg_bmi + "   " + bmi_result, True, WHITE), (25, 150))
   screen.blit(sys_font_weight.render("Center of Balance: " + "%.1f" % right + "R " + "%.1f" % left + "L " + "%.1f" % back + "B " + "%.1f" % front + "F "  , True, WHITE), (25, 225))
   pygame.draw.circle(screen, (255,0,0), (int(avg_x), int(avg_y)), 5)
   pygame.display.flip()
   pygame.time.wait(refresh_delay)
   results = [avg_weight, avg_bmi, cob_score]
   while True:
   	for event in pygame.event.get():
   		if event.type == KEYDOWN:
   			if event.key == pygame.K_RETURN:
   				return results

def setup_calibration():
   global named_calibration, wiimote
   wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
   wiimote.request_status()
   balance_calibration = wiimote.get_balance_cal()
   named_calibration = { 'right_top': balance_calibration[0],
                    'right_bottom': balance_calibration[1],
                    'left_top': balance_calibration[2],
                    'left_bottom': balance_calibration[3],
                  }   
                  
def getpos():
   global wiimote   
   readings = wiimote.state['balance']   
   try:
      x_balance = (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'left_bottom')))
      if x_balance > 1:
         x_balance = (((float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom'))))*-1.)+1.
      elif x_balance < -1:
         x_balance = (float(gsc(readings,'left_top')+gsc(readings,'left_bottom'))) / (float(gsc(readings,'right_top')+gsc(readings,'right_bottom')))+1
      else:
         x_balance = x_balance -1.
         
      y_balance = (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))) / (float(gsc(readings,'left_top')+gsc(readings,'right_top')))
      if y_balance > 1:
         y_balance = (((float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom'))))*-1.)+1.
      elif y_balance < -1:
         y_balance = (float(gsc(readings,'left_top')+gsc(readings,'right_top'))) / (float(gsc(readings,'left_bottom')+gsc(readings,'right_bottom')))+1.
      else:      
         y_balance = y_balance -1.
   except:
      x_balance = 1.
      y_balance = 1.
         
   return x_balance, y_balance
   
def get_direction(x, y):
   if x >=0 and y>=0:
      quad=1;
   elif x<=0 and y>=0:
      quad=2
   elif x<=0 and y<=0:
      quad=3
   elif x>=0 and y<=0:
      quad=4
   
   angle = math.atan(y/x)*(180/math.pi)
   angle1 = math.atan(y/x)*(180/math.pi)
   if quad==2:
      angle = 180+angle
   elif quad==3:
      angle = 180+angle
   elif quad==4:
      angle = 360+angle
   direction = ''   
   if angle <= 45 or angle >= 315:
      direction = 'r'
   elif angle >=45 and angle <=135:
      direction = 'u'
   elif angle >=135 and angle <=225:
      direction = 'l'
   elif angle >=225 and angle <=315:
      direction = 'd'
      
   return direction, angle, quad, angle1
