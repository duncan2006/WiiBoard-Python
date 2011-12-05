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
import datetime
import subprocess

MAIN            	= 0
EXIT					= 1
BACK					= 2
CONNECTING			= 3
CREATEPROFILE		= 4
LOADPROFILE       = 5
MEASUREMENTS      = 6
SINGLELEG			= 7
DYNAMICBALANCE 	= 8
STOPANDGO			= 9
MAZE					= 10
DISPLAYRESULTS		= 11

#Maze variables
MAZESIZE        	= 20
MAZEDIFF        	= 21
SMALL           	= 22
MEDIUM          	= 23
LARGE           	= 24
EASY            	= 25
HARD            	= 26



#Profile loading defaults to 100+

def main():
   # Uncomment this to center the window on the computer screen
   os.environ['SDL_VIDEO_CENTERED'] = '1'
   # Initialize Pygame
   pygame.init()
   # Create a window of 800x600 pixels
   screen = pygame.display.set_mode((800, 600))
   #Add caption to top of window
   pygame.display.set_caption("Wii Balance Board Physiotherapy")
   
   #Create profile loading menu dynamically
   profiles = []
   listing = os.listdir("profiles/")
   i = 100
   for infile in listing:
		name = infile.replace(".csv", "")
		menu_entry = (name, i, None)
		profiles.append(menu_entry)
		i += 1

   profiles.append(('Back to Menu',	BACK, None))
   
   #Create start menu for initial display
   start_menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
	      [('Connect Balance Board',     CONNECTING, None),
	       ('Create Profile',            CREATEPROFILE, None),
	       ('Load Profile',					 LOADPROFILE, None),
	       ('Exit',                      EXIT, None)])
   start_menu.set_center(True, True)
   start_menu.set_alignment('center', 'center')
 
   #Menu after board connected and profile loaded
   menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
         [('Daily Measurements',        MEASUREMENTS, None),
          ('Single Leg Balance',			 SINGLELEG, None),
          ('Dynamic Balance',           DYNAMICBALANCE, None),
          ('Stop & Go',						 STOPANDGO, None),
          ('Maze',                      MAZESIZE, None),
          ('Display Results',				 DISPLAYRESULTS, None),
          ('Exit',                      EXIT, None)])
   menu.set_center(True, True)
   menu.set_alignment('center', 'center')
   
   #Menu displayed for pairing balance board to computer
   connectMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
						[('', 0, None)])           
   connectMenu.set_center(True, True)
   connectMenu.set_alignment('bottom','center')
   
   #Menu displayed for loading existing profiles		
   loadprof_menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen, profiles)          
   loadprof_menu.set_center(True, True)
   loadprof_menu.set_alignment('center', 'center')
   
   #Menu for choosing size of maze
   mazeSizeMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Small',               SMALL, None),
	            ('Medium',              MEDIUM, None),
               ('Large',               LARGE, None)])
   mazeSizeMenu.set_center(True, True)
   mazeSizeMenu.set_alignment('center','center')
   
   #Menu for choosing difficulty of maze
   mazeDiffMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Easy',               EASY, None),
	            ('Hard',               HARD, None)])
   mazeDiffMenu.set_center(True, True)
   mazeDiffMenu.set_alignment('center','center')
   
   #Black display and flip screen
   screen.fill(BLACK)
   pygame.display.flip()
   
   # Create the state variables (make them different so that the user event is
   # triggered at the start of the "while 1" loop so that the initial display
   # does not wait for user input)
   state = 0
   prev_state = 1
   
   #Initialize maze size and difficulty
   mazeSize = -1
   mazeDiff = -1
   
   #Initialize empty profile information and measurement results
   profile_info = ["", "__ft__in", 0]
   meas_results = [0, 0, 0, 0, 0, 0, 0]
   user_profile = None
   
   # rect_list is the list of pygame.Rect's that will tell pygame where to
   # update the screen (there is no point in updating the entire screen if only
   # a small portion of it changed!)
   rect_list = []

   # Ignore mouse motion (greatly reduces resources when not needed)
   pygame.event.set_blocked(pygame.MOUSEMOTION)

   # seen the random number generator (used here for choosing random colors
   # in one of the menu when that button is selected)
   random.seed()

	#Initialize state booleans
   wii_status = False
   load_status = False
   profile_loaded = False
   results_logged = False
   
   # The main while loop
   while 1:
      # Check if the state has changed, if it has, then post a user event to
      # the queue to force the menu to be shown at least once
      #print "beginning of while loop"
		if prev_state != state:
			pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
			prev_state = state
			screen.fill(BLACK)
			pygame.display.set_caption("Wii Balance Board Physiotherapy")
			desc_font = pygame.font.Font(None, 24)    # Font to use
			if wii_status!=False:
				screen.blit(desc_font.render("Wii Balance Board is connected!", True, WHITE), (300, 570))
			else:
				screen.blit(desc_font.render("Wii Balance Board is not connected", True, WHITE), (300, 570))

		screen.blit(desc_font.render("User: "   + profile_info[0], True, WHITE), (0, 0))
		screen.blit(desc_font.render("Height: " + profile_info[1], True, WHITE), (650, 0))
   
		pygame.display.flip()

      # Get the next event
		e = pygame.event.wait()

		if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
			if state == MAIN:
				if (wii_status and profile_loaded):
					#When profile loaded and balance board connected move to game menu
					rect_list, state = menu.update(e, state)
				elif load_status:
					#If load profile requested, load that menu
					rect_list, state = loadprof_menu.update(e, state)
				else:
					#Otherwise, stay at initial screen
					rect_list, state = start_menu.update(e, state)
			elif state == CONNECTING:
				rect_list, state = connectMenu.update(e, state)
				wii_status = scalesgui.connect_wiiboard(screen)          
				state=MAIN		
			elif state == CREATEPROFILE:
				profile_info = create_profile(screen)
				profile_path = "profiles/" + profile_info[0] + ".csv"
				if (os.path.isfile(profile_path)):
					print "Username " + profile_info[0] + " already exists, please try a different name."
					profile_info = ["", "__ft__in", 0]
					#ygame.quit()
					#ys.exit()
				else:
					user_profile = open(profile_path, 'a')			
					user_profile.write('Username,' + profile_info[0] + ',Height,' + profile_info[1] + ',Inches,' + str(profile_info[2]) + '\n')
					user_profile.write('Date,Weight(lbs),BMI,Center of Balance,Single Leg Balance,Dynamic Balance,Stop&Go,Maze\n')        
				profile_loaded = True
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
				#States greater than 100 are the dynamically allocated profiles to load	
				user_profile = open("profiles/" + listing[state-100], 'a+')
				reader = csv.reader(user_profile)
				for row in reader:
					profile_info[0] = row[1] #Get name from first row
					profile_info[1] = row[3] #Get height from first row
					profile_info[2] = row[5] #Get height in inches from first row 
					break
				load_status = False
				profile_loaded = True
				state=MAIN	
			elif state == MEASUREMENTS:
				bodymeasure_results = scalesgui.bodymeasure(screen, int(profile_info[2]))
				meas_results[0] = bodymeasure_results[0]
				meas_results[1] = bodymeasure_results[1]
				meas_results[2] = bodymeasure_results[2]
				state=MAIN
			elif state == SINGLELEG:
				singleleg_results = scalesgui.singleleg(screen)
				meas_results[3] = singleleg_results
				state=MAIN
			elif state == DYNAMICBALANCE:
				dbal_results = scalesgui.dynamic_balance(screen)
				meas_results[4] = dbal_results
				state=MAIN
			elif state == STOPANDGO:
				stop_go_result = scalesgui.stop_go(screen)
				meas_results[5] = stop_go_result
				state=MAIN	
			elif state == MAZE: 
				maze_result = PyMaze.run(mazeSize, mazeDiff)
				meas_results[6] = maze_result
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
			elif state == DISPLAYRESULTS:
				if (not results_logged):
					#Write new results when they haven't been logged
					results_logged = True
					now = datetime.datetime.now()
					user_profile.write(now.strftime("%Y-%m-%d %H:%M")+','
					+ str(meas_results[0])+',' 
					+ str(meas_results[1])+','
					+ str(meas_results[2])+',' 
					+ str(meas_results[3])+','
					+ str(meas_results[4])+',' 
					+ str(meas_results[5])+','   
					+ str(meas_results[6])+'\n')
					user_profile.close()
					
				prof_name = '"%s.csv"'%profile_info[0]					
				proc = subprocess.Popen(['gnuplot','-p'], shell=True, stdin=subprocess.PIPE,)
				proc.stdin.write('reset\n')
				proc.stdin.write('set term x11 0\n')
				proc.stdin.write('set xdata time\n')
				proc.stdin.write('set timefmt "%Y-%m-%d %H:%M"\n')
				proc.stdin.write('set title "Your Weight Tracker"\n')
				proc.stdin.write('set xlabel "Date"\n')
				proc.stdin.write('set ylabel "Weight (lbs)"\n')
				proc.stdin.write('set y2label "BMI"\n')
				proc.stdin.write('set y2tics nomirror\n')
				proc.stdin.write('set xtics 86400\n')
				proc.stdin.write('set autoscale\n')
				proc.stdin.write('set datafile separator ","\n')
				proc.stdin.write('cd "profiles"\n')
				proc.stdin.write('plot ' + prof_name + ' using 1:2 axis x1y1 title "Weight (lbs)" with linespoints,' + prof_name + ' using 1:3 axis x1y2 title "BMI" with linespoints\n')
				proc.stdin.write('reset\n')
				proc.stdin.write('set term x11 1\n')
				proc.stdin.write('set xdata time\n')
				proc.stdin.write('set timefmt "%Y-%m-%d %H:%M"\n')
				proc.stdin.write('set title "Your Test Results"\n')
				proc.stdin.write('set xlabel "Date"\n')
				proc.stdin.write('set ylabel "Points"\n')
				proc.stdin.write('set xtics 86400\n')
				proc.stdin.write('set autoscale\n')
				proc.stdin.write('set datafile separator ","\n')
				proc.stdin.write('plot ' + prof_name + ' using 1:4 title "Center of Balance" with linespoints,' \
				                         + prof_name + ' using 1:5 title "Single Leg Balance" with linespoints,'\
				                         + prof_name + ' using 1:6 title "Dynamic Balance" with linespoints,'\
				                         + prof_name + ' using 1:7 title "Stop and Go" with linespoints,'\
				                         + prof_name + ' using 1:8 title "Maze" with linespoints\n')
				proc.stdin.write('pause -1\n')
				state=MAIN
			else:
				#Otherwise, exit the program. If a user profile has been loaded, then write current results
				if (user_profile):
					if (not results_logged):
						now = datetime.datetime.now()
						user_profile.write(now.strftime("%Y-%m-%d %H:%M")+','
						+ str(meas_results[0])+',' 
						+ str(meas_results[1])+','
						+ str(meas_results[2])+',' 
						+ str(meas_results[3])+','
						+ str(meas_results[4])+',' 
						+ str(meas_results[5])+','   
						+ str(meas_results[6])+'\n')
						user_profile.close()
				pygame.quit()
				sys.exit()

      #print state
      # Quit if the user presses the exit button
		if e.type == pygame.QUIT:
			if (user_profile):
				now = datetime.datetime.now()
				user_profile.write(now.strftime("%Y-%m-%d %H:%M")+','
				+ str(meas_results[0])+',' 
				+ str(meas_results[1])+','
				+ str(meas_results[2])+',' 
				+ str(meas_results[3])+','
				+ str(meas_results[4])+',' 
				+ str(meas_results[5])+','   
				+ str(meas_results[6])+'\n')
				user_profile.close()
			pygame.quit()
			sys.exit()
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_ESCAPE:
				if (user_profile): 
					now = datetime.datetime.now()
					user_profile.write(now.strftime("%Y-%m-%d %H:%M")+','
					+ str(meas_results[0])+',' 
					+ str(meas_results[1])+','
					+ str(meas_results[2])+',' 
					+ str(meas_results[3])+','
					+ str(meas_results[4])+',' 
					+ str(meas_results[5])+','   
					+ str(meas_results[6])+'\n')
					user_profile.close()
				pygame.quit()
				sys.exit()          
				
		# Update the screen on every loop
		pygame.display.update(rect_list)
	#End game loop

def create_profile(screen):
		screen.fill(BLACK)
		profile_name = ask(screen, "Name")
		screen.fill(BLACK)
		profile_feet = ask(screen, "Height (feet)")
		screen.fill(BLACK)
		profile_inches = ask(screen, "Height (inches)")
		profile_height = int(profile_feet) * 12 + int(profile_inches)
		profile_info = [profile_name, profile_feet + "ft" + profile_inches + "in", profile_height ]
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

