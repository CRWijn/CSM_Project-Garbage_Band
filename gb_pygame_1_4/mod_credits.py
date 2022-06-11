import time
import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN
    )
from mod_volumeslider import VolumeSlider
from obj_game_object import GameObject

class Credits:
    def __init__(self, screen):
        # Load all the credits text
        self.load_text()
        self.mode = self.cred_loop(screen)

    # Game loop function
    def cred_loop(self, screen):
        # Initialize the music, events and the start time
        next_cred, cred_move, start = self.loop_init()
        cred_list = [] # Credits list
        playing = False # Credits music playing set to false
        done = False # Credits finished set to false
        # Game loop
        while True:
            # If it's not playing and 1.9 seconds has passed
            if not playing and time.time() - start > 1.9:
                playing = True # Set music playing to true
                pygame.mixer.music.play() # Play the music
            # Loop over all events that occured this iteration
            for event in pygame.event.get():
                if event.type == QUIT: # If the X in the top right is pressed
                    pygame.mixer.music.stop() # Stop playing music
                    return 'quit' # Send a quit call back
                elif event.type == KEYDOWN: # If a keyboard input is detected
                    if event.key == 27: #ESCAPE = 27
                        pygame.mixer.music.stop() # Stop playing music
                        return 'settings' # Go back to the settings menu
                elif event.type == next_cred: # Event next occurs
                    if len(self.element) > 0: # If there is credits that aren't on the screen
                        done = True # One of the two bools to check if the credits is finished
                        cred_list.append(self.element[0]) # Add the next credit to the credits list
                        self.element.pop(0) # Remove it from the list credits queue list
                elif event.type == cred_move: # Move the credits event
                    screen.fill((255, 255, 255)) # White background
                    for obj in cred_list: # For every credit in the credits list
                        if obj.update(): # Call the move function "update" and if it returns true then the credit is out of the screen
                            cred_list.pop(0) # Remove the finished credit from the credits lsit
                            continue # Skip the rest of the code in this for loop
                        obj.blit(screen) # Custom blit function
            # If the credits list is empty and the done variable has been set to true (done = True after every credit is added to the credits list)
            if len(cred_list) == 0 and done:
                pygame.mixer.music.stop() # Stop playing the music
                return 'settings' # Return to the settings screen
            # Refresh the screen
            pygame.display.update()

    # Initialize some things before the game loop
    def loop_init(self):
        # Next credit event creation
        next_cred = pygame.USEREVENT + 2
        # Move credits event creation
        cred_move = pygame.USEREVENT + 3
        # Set the timer for the next credit event
        pygame.time.set_timer(next_cred, 2000)
        # Set the timer for the move credit event
        pygame.time.set_timer(cred_move, 20)
        # Start time
        start = time.time()
        # Loading the credits music file
        pygame.mixer.music.load('resources/settings_screen/Credits_Music.wav')
        # Setting the volume of the music
        pygame.mixer.music.set_volume(float(VolumeSlider.get_vol()))
        # Return the two events created and the start time
        return next_cred, cred_move, start

    # Load all the credits text
    def load_text(self):
        self.element = []
        # Garbage Band title
        gb_title_txt = "GARBAGE BAND"
        gb_title = CreditObj(gb_title_txt, False, True)
        self.element.append(gb_title)
        # Scrum master credit
        scrum_txt = ["Scrum Master   Wesmond Lee"]
        scrum = CreditObj(scrum_txt)
        self.element.append(scrum)
        # Product owner credit
        product_owner_txt = ["Product Owner   Calvin Wijnveen"]
        product_owner = CreditObj(product_owner_txt)
        self.element.append(product_owner)
        # Graphics design credit
        graphic_design_txt = ["Graphic Design   Joop Sluimer", "   Steven Zhou"]
        graphic_design = CreditObj(graphic_design_txt)
        self.element.append(graphic_design)
        # Audio recording research credit
        audio_research_txt = ["Audio Recording Research   Anthony Dai"]
        audio_research = CreditObj(audio_research_txt)
        self.element.append(audio_research)
        # Software design credit
        software_design_txt = ["Software Design   Joop Sluimer", "   Calvin Wijnveen"]
        software_design = CreditObj(software_design_txt)
        self.element.append(software_design)
        # Testing contributors
        testing_txt = ["Script Testing   Anthony Dai", "   Wesmond Lee", "   Steven Zhou"]
        testing = CreditObj(testing_txt)
        self.element.append(testing)
        # Music creation
        guitar_audio_txt = ["Guitar Audio   Wesmond Lee"]
        guitar_audio = CreditObj(guitar_audio_txt)
        self.element.append(guitar_audio)
        # Special thanks to
        thanks_txt = ["Special Thanks To   Otto Kaaij", "   Roald van der Heijden", "   TI3111TU Staff"]
        thanks = CreditObj(thanks_txt)
        self.element.append(thanks)
        # Credits song
        song_txt = ["Credits Song   American Idiot - Green Day"]
        song = CreditObj(song_txt)
        self.element.append(song)
        # Garbage Band Logo
        gb_logo = CreditObj('', True)
        self.element.append(gb_logo)

# Credits object
class CreditObj:
    def __init__(self, txt, logo = False, title = False):
        #If it's the logo at the end of the credits
        self.logo = logo # Is true or false if the object is the logo
        self.title = title # Credits title
        if logo: # If it is the logo
            img = pygame.image.load("resources/logo_transparent.png") # Load the logo image
            self.surf = pygame.transform.scale(img, (400, 400)) # Rescale the logo
            self.rect = self.surf.get_rect()
            self.rect = self.rect.move((440, 720)) # Move it underneath the screen
        elif title: # If it's the title at the beginning of the credits
            font = pygame.font.Font('freesansbold.ttf', 40) # Creating the font for the text
            self.surf = font.render(txt, True, (0, 0, 0)) # Rendering the font
            self.rect = self.surf.get_rect()
            self.rect = self.rect.move((640 - self.rect.width//2, 720)) # Placing it centered underneath the screen
        else: # If it's text in the credits
            self.lines = [] # Lines in the credit object
            font = pygame.font.SysFont('consolas', 25) # Create the font
            for i, line in enumerate(txt): # For every line in the specific credit object
                surf = font.render(line, True, (0, 0, 0)) # Render the line
                rect = surf.get_rect()
                if i == 0: # If it's the first line then the placement needs to change
                    rect = rect.move(((640 - int(rect.width*len(line.split("   ")[0])/len(line))), 720)) # Place the text so that the gap in between the credit title and credit is centered
                else:
                    rect = rect.move(640, 720 + i*32) # Place it with the gap centered and every line will be 32 pixels lower than the last
                obj = GameObject(surf, rect) # Create the special object
                self.lines.append(obj) # Add it to the lines of this specific credit

    # Update for a credit object
    def update(self):
        if self.logo or self.title: # If it's the title or the logo
            self.rect.move_ip(0, -1) # Move it up a pixel
            if self.rect.bottom <= 0: # If the bottom of the credit is above the top of the screen
                return True # Return true which should delete the credit object from the list of credit objects
        else: # If it's not the title or the logo then it's possible it will have multiple lines
            last = None
            for line in self.lines: # For every line in the credit object
                line.pos.move_ip(0, -1) # Move it up 1 pixel
                last = line
            if last.pos.bottom <= 0: # Since this is outside the for loop it will take the bottom of the last line
                return True
        return False # Do not delete the credit object from the credit list

    # Custom blit
    def blit(self, screen):
        if self.logo or self.title: # If it's the header or logo nothing special needs to happen
            screen.blit(self.surf, self.rect) # Simply blit the surface and rectangle
        else: # If it's not a header or title then it might be made up of multiple lines
            for line in self.lines: # Blit every line in the credit object
                screen.blit(line.surf, line.pos)
