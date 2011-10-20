#! /usr/bin/python

import sys, pygame, random
from menu import *
from image import *
import scalesgui
import thread
import PyMaze

MAIN        = 0
TRACKWEIGHT = 1
SCALE       = 2
CONNECTING  = 3
MAZE        = 4
EXIT        = 5


def main():
   # Uncomment this to center the window on the computer screen
   os.environ['SDL_VIDEO_CENTERED'] = '1'
   
   # Initialize Pygame
   pygame.init()

   # Create a window of 800x600 pixels
   screen = pygame.display.set_mode((800, 600))
   
   screen.fill(BLACK)
   pygame.display.flip()
 
   menu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('Track Weight',           TRACKWEIGHT, None),
               ('Scale',                  SCALE, None),
               ('Connect Wii Board',      CONNECTING, None),
               ('Maze',                   MAZE, None),
               ('Exit',                   EXIT, None)])
               
               
   menu.set_center(True, True)
   menu.set_alignment('center', 'center')
   
   connectMenu = cMenu(100, 50, 20, 5, 'vertical', 100, screen,
              [('', 0, None)])
              
   connectMenu.set_center(True, True)
   connectMenu.set_alignment('bottom','center')
   
   # Create the state variables (make them different so that the user event is
   # triggered at the start of the "while 1" loop so that the initial display
   # does not wait for user input)
   state = 0
   prev_state = 1
   
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
         pygame.display.flip()

      # Get the next event
      e = pygame.event.wait()

      
      if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
         if state == MAIN:
            rect_list, state = menu.update(e, state)
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
            PyMaze.run()
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

if __name__ == "__main__":
   main()

