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
#import weighttracker

MAIN            = 0
TRACKWEIGHT     = 1
SCALE           = 2
CONNECTING      = 3
MAZE            = 4
EXIT            = 5
CREATEPROFILE   = 6

#Maze variables
MAZESIZE        = 7
MAZEDIFF        = 8
SMALL           = 9
MEDIUM          = 10
LARGE           = 11
EASY            = 12
HARD            = 13

def main():
   # Uncomment this to center the window on the computer screen
   os.environ['SDL_VIDEO_CENTERED'] = '1'
   
   # Initialize Pygame
   pygame.init()

   # Create a window of 800x600 pixels
   screen = pygame.display.set_mode((800, 600))
   pygame.display.set_caption("Wii Balance Board Physiotherapy")

   screen.fill(BLACK)
   pygame.display.flip()

   start_menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
	      [('Connect Wii Balance Board', CONNECTING, None),
	       ('Create Profile',            CREATEPROFILE, None),
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
   profile_name = ""
   profile_feet = "__ft"
   profile_inches = "__in"
   
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

	    screen.blit(desc_font.render("User: " + profile_name, True, WHITE), (0, 0))
      screen.blit(desc_font.render("Height: " + profile_feet + " " + profile_inches, True, WHITE), (600, 0))
   
      pygame.display.flip()

      # Get the next event
      e = pygame.event.wait()
      
      if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
         if state == MAIN:
            if wii_status:
               rect_list, state = menu.update(e, state)
            else:
               rect_list, state = start_menu.update(e, state)
         elif state == SCALE:
            scalesgui.scalegui(screen)
            state=MAIN            
         elif state == CONNECTING:
            rect_list, state = connectMenu.update(e, state)
            wii_status = scalesgui.connect_wiiboard(screen)          
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
            screen.fill(BLACK)
            profile_name = ask(screen, "Name")
            screen.fill(BLACK)
            profile_feet = ask(screen, "Height (feet)") + "ft"
            screen.fill(BLACK)
            profile_inches = ask(screen, "Height (inches)") + "in"
            state=MAIN
         else:
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

#Toggling fullscreen probably not a good idea
def toggle_fullscreen():
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()
    cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 
    
    w,h = screen.get_width(),screen.get_height()
    flags = screen.get_flags()
    bits = screen.get_bitsize()
    
    pygame.display.quit()
    pygame.display.init()
    
    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    screen.blit(tmp,(0,0))
    pygame.display.set_caption(*caption)
 
    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
 
    pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
    
    return screen
    
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

