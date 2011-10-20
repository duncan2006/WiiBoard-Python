#! /usr/bin/python

import os, pygame
from menu import *

# ---[ READ THE NOTE - THIS IS NOT PART OF THE EXAMPLE ]------------------------
# NOTE!  This function is PURPOSELY not commented since it is not part of this
# example menu system, but is used to load some images to use as buttons for
# demonstration.  Please see my graphics class to see a better load_image
# function and how to use it more effectively.
def load_image(file_name, folder, colorkey = None):
   full_name = os.path.join(folder, file_name)
   try:
      image = pygame.image.load(full_name)
   except pygame.error, message:
      print 'Cannot load image:', full_name
      raise SystemExit, message
   image = image.convert_alpha()
   if colorkey is not None:
      if colorkey is -1:
         colorkey = image.get_at((0,0))
      image.set_colorkey(colorkey, pygame.RLEACCEL)
   return image


# ---[ READ THE NOTE - THIS IS NOT PART OF THE EXAMPLE ]------------------------
# This is just used to describe the current menu to the user - this is not
# implemented "well" since it is not what I am trying to show in this menu
# example (i.e. when this is updated, it changes the ENTIRE screen instead
# of only the portion that changed as we do with the menu system).
DESC = [['MENU 0 - This menu is positioned using the top left corner and '
            'contains only text buttons',
         'Press enter to select a button.  Press \'r\' to remove the currently '
            'selected button.',
         'Select Exit on any menu or press ESC to exit the program'],
        ['MENU 1 - This menu is positioned using the top left corner and '
            'contains only text buttons',
         'The menu has multiple rows and columns (use the arrow keys).  The '
            'colors can also be changed!',
         'Select a button'],
        ['MENU 2 - The center of this menu is placed in the center of the '
            'screen and it contains only picture',
         'buttons.  Can you have a menu with text buttons and images?',
         'Select a button to continue (All buttons go to the next menu)'],
        ['MENU 3 - A mix of text and graphical images!  Add will dynamically '
            'add some buttons.  Center will',
         'center the menu on the screen.  Set (0, 0) will set the top left of '
            'the menu in the top left of the screen.',
         'Rand Colors/Config will change some menu parameters (see console '
            'output for new values).']]
            
TEXT = []
pygame.font.init()
desc_font = pygame.font.Font(None, 24)    # Font to use
for text in DESC:
   tmp = []
   tmp.append(desc_font.render(text[0], True, WHITE))
   tmp.append(desc_font.render(text[1], True, WHITE))
   tmp.append(desc_font.render(text[2], True, WHITE))
   TEXT.append(tmp)
