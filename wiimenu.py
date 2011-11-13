#! /usr/bin/python
'''Wii Balance Board Physiotherapy Main Menu'''

import sys, random

sys.path.insert(0, '/home/cwiid_lib')

try:
	import pygame, pygame.font, pygame.event, pygame.draw, string
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

from menu import *
from image import *
from pygame.locals import *

import scalesgui
import thread
import PyMaze

import os
import csv
#import weighttracker

MAIN            	= 0
TRACKWEIGHT     	= 1
SCALE           	= 2
CONNECTING      	= 3
MAZE            	= 4
EXIT            	= 5
CREATEPROFILE   	= 6
LOADPROFILE			= 7
BACK					= 8

#Maze variables
MAZESIZE        = 9
MAZEDIFF        = 10
SMALL           = 11
MEDIUM          = 12
LARGE           = 13
EASY            = 14
HARD            = 15

def main():
   # Uncomment this to center the window on the computer screen
   os.environ['SDL_VIDEO_CENTERED'] = '1'
   
   # Initialize Pygame
   pygame.init()

   # Create a window of 800x600 pixels
   screen = pygame.display.set_mode((800, 600))
   pygame.display.set_caption("Wii Balance Board Physiotherapy")
   
   profiles = []
   listing = os.listdir("profiles/")
   i = 100
   for infile in listing:
		name = infile.replace(".csv", "")
		menu_entry = (name, i, None)
		profiles.append(menu_entry)
		i += 1

   profiles.append(('Back to Menu',	BACK, None))
   
   #print listing[0] + listing[1]
   
   screen.fill(BLACK)
   pygame.display.flip()

   start_menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
	      [('Connect Wii Balance Board', CONNECTING, None),
	       ('Create Profile',            CREATEPROFILE, None),
	       ('Load Profile',					 LOADPROFILE, None),
	       ('Exit',                      EXIT, None)])
   start_menu.set_center(True, True)
   start_menu.set_alignment('center', 'center')
 
   menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Create Profile',         CREATEPROFILE, None),
	           ('Track Weight',           TRACKWEIGHT, None),
               ('Scale',                  SCALE, None),
               ('Maze',                   MAZESIZE, None),
               ('Exit',                   EXIT, None)])
               

   menu.set_center(True, True)
   menu.set_alignment('center', 'center')
   
   connectMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
						[('', 0, None)])           
   connectMenu.set_center(True, True)
   connectMenu.set_alignment('bottom','center')
   		
   loadprof_menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen, profiles)          
   loadprof_menu.set_center(True, True)
   loadprof_menu.set_alignment('center', 'center')
   
   #user_profile = open("profiles/Jay_Oatts.csv", 'w')
   
   #user_profile.write('Username,Height(in),Weight(lbs),BMI')
   
   mazeSizeMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Small',               SMALL, None),
	             ('Medium',              MEDIUM, None),
               ('Large',               LARGE, None)])
   mazeSizeMenu.set_center(True, True)
   mazeSizeMenu.set_alignment('center','center')
   
   
   mazeDiffMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Easy',               EASY, None),
	             ('Hard',              HARD, None)])
   mazeDiffMenu.set_center(True, True)
   mazeDiffMenu.set_alignment('center','center')
   
   # Create the state variables (make them different so that the user event is
   # triggered at the start of the "while 1" loop so that the initial display
   # does not wait for user input)
   state = 0
   prev_state = 1
   
   mazeSize=-1
   mazeDiff=-1
   
   #Profile stats
   #profile_name = ""
   #profile_feet = "__ft"
   #profile_inches = "__in"
   profile_info = ["", "__ft__in"]
   
   # rect_list is the list of pygame.Rect's that will tell pygame where to
   # update the screen (there is no point in updating the entire screen if only
   # a small portion of it changed!)
   rect_list = []

   # Ignore mouse motion (greatly reduces resources when not needed)
   pygame.event.set_blocked(pygame.MOUSEMOTION)

   # seen the random number generator (used here for choosing random colors
   # in one of the menu when that button is selected)
   random.seed()

   wii_status = False
   load_status = False
   # The main while loop
   while 1:
      # Check if the state has changed, if it has, then post a user event to
      # the queue to force the menu to be shown at least once
      #print "beginning of while loop"
		if prev_state != state:
			pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
			prev_state = state
			screen.fill(BLACK)
			desc_font = pygame.font.Font(None, 24)    # Font to use
			if wii_status!=False:
				screen.blit(desc_font.render("Wiiboard is connected!", True, WHITE), (300, 570))
			else:
				screen.blit(desc_font.render("Wiiboard is not connected", True, WHITE), (300, 570))

		screen.blit(desc_font.render("User: " + profile_info[0], True, WHITE), (0, 0))
		screen.blit(desc_font.render("Height: " + profile_info[1] , True, WHITE), (600, 0))
   
		pygame.display.flip()

      # Get the next event
		e = pygame.event.wait()

		if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
			if state == MAIN:
				if wii_status:
					rect_list, state = menu.update(e, state)
				elif load_status:
					rect_list, state = loadprof_menu.update(e, state)
				else:
					rect_list, state = start_menu.update(e, state)
			elif state == SCALE:
				#rect_list, state = menu.update(e, state)
				scalesgui.scalegui(screen)
				state=MAIN            
			elif state == CONNECTING:
				rect_list, state = connectMenu.update(e, state)
				wii_status = scalesgui.connect_wiiboard(screen)          
				#thread.start_new_thread( scalesgui.connect_wiiboard, (screen, None ) )
				state=MAIN
			elif state == MAZE: 
				PyMaze.run(mazeSize, mazeDiff)
				state=MAIN
				mazeSize=-1
				mazeDiff=-1
			elif state == MAZESIZE: 
				rect_list, mazeSize = mazeSizeMenu.update(e, state)
				if mazeSize==SMALL or mazeSize==MEDIUM or mazeSize==LARGE:
					state = MAZEDIFF
			elif state == MAZEDIFF: 
				rect_list, mazeDiff = mazeDiffMenu.update(e, state)
				if mazeDiff==EASY or mazeDiff==HARD:
					state = MAZE
			elif state == CREATEPROFILE:
				profile_info = create_profile(screen)
				profile_path = "profiles/" + profile_info[0] + ".csv"
				if (os.path.isfile(profile_path)):
					print "Username " + profile_info[0] + " already exists, please try a different name."
					pygame.quit()
					sys.exit()
				else:
					user_profile = open(profile_path, 'a')
							
				user_profile.write('Username,' + profile_info[0] + ',' + 'Height,' + profile_info[1] + '\n')
				user_profile.write('Weight(lbs),BMI\n')        
				
				state=MAIN
			elif state == LOADPROFILE:
				#profile_info = load_profile(screen)
				#load_profile(screen)
				load_status = True
				state=MAIN
			elif state == BACK:
				rect_list, state = menu.update(e, state)
				load_status = False
				state=MAIN
			elif state >= 100:	
				user_profile = open("profiles/" + listing[state-100], 'a+')
				reader = csv.reader(user_profile)
				for row in reader:
					profile_info[0] = row[1]
					profile_info[1] = row[3]
					break
				load_status = False
				state=MAIN
			else:
				user_profile.close()
				pygame.quit()
				sys.exit()

      #print state
      # Quit if the user presses the exit button
		if e.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()          
				
		# Update the screen
		pygame.display.update(rect_list)

def create_profile(screen):
		screen.fill(BLACK)
		profile_name = ask(screen, "Name")
		screen.fill(BLACK)
		profile_feet = ask(screen, "Height (feet)") + "ft"
		screen.fill(BLACK)
		profile_inches = ask(screen, "Height (inches)") + "in"
		profile_info = [profile_name, profile_feet + profile_inches]
		return profile_info

def load_profile(screen):
		screen.fill(BLACK)
		profiles = []
		listing = os.listdir("profiles/")
		i = 0
		for infile in listing:
			name = infile.replace(".csv", "")
			menu_entry = (name, i, None)
			profiles.append(menu_entry)
			i += 1
		
		menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen, profiles)          
		menu.set_center(True, True)
		menu.set_alignment('center', 'center')
		
		state = 0
		prev_state = 1
		
		rect_list = []
		
		random.seed()
		
		while 1:
		  # Check if the state has changed, if it has, then post a user event to
		  # the queue to force the menu to be shown at least once
		  #print "beginning of while loop"
			if prev_state != state:
				pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
				prev_state = state
				screen.fill(BLACK)

				pygame.display.flip()

		    # Get the next event
				e = pygame.event.poll()
		    
				if e.type == KEYDOWN or e.type == EVENT_CHANGE_STATE:
					if state == MAIN:
						rect_list, state = menu.update(e, state)
		   
					else:
						pygame.quit()
						sys.exit()
			
			# Quit if the user presses the exit button
			if e.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()      
					
		   # Update the screen
			pygame.display.update(rect_list)

			#return profile_info
    
def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.Font(None,18)
  pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
  pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
  pygame.display.flip()

def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + string.join(current_string,""))
  while 1:
    inkey = get_key()
    if inkey == K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == K_RETURN:
      break
    elif (inkey == K_RSHIFT or inkey == K_LSHIFT):
      inkey = get_key()
      inkey = inkey - 32
      current_string.append(chr(inkey))  
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + ": " + string.join(current_string,""))
  return string.join(current_string,"")


if __name__ == "__main__":
   main()

