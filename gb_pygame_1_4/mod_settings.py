import webbrowser as wb
import pygame
from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN
)
from mod_metronome import Metronome
from obj_game_object import GameObject
import mod_volumeslider
import mod_bpmslider

class Settings:
    def __init__(self, screen):
        self.load_images()
        # Default blits array
        default = [self.images['background'], self.images['quit'], self.images['credits_button'],
                   self.images['sound credit'], self.images['slider exp']]
        # Initialise both volume and metronome BPM sliders
        self.vol_slider = mod_volumeslider.VolumeSlider()
        self.bpm_slider = mod_bpmslider.BPMSlider()
        # Variables to keep track whether the slider is pressed
        self.vslider_pressed = False
        self.bslider_pressed = False
        # Variables to keep track of text input
        self.vol_txt = ''
        self.bpm_txt = ''
        # Create a channel for the metronome
        pygame.mixer.set_num_channels(1)

        self.mode = self.sett_loop(screen, default)

    # Main settings loop
    def sett_loop(self, screen, default):
        # Initialize the metronome
        metronome = Metronome(self.vol_slider.get_vol(), True)
        # Copy the default blits to the blitting array
        blits = default.copy()
        # Game loop
        while True:
            # Loop over every event that occured this iteration
            for event in pygame.event.get():
                if event.type == QUIT: # If the X in the top right is pressed
                    return 'quit' # Send back a quit call
                elif event.type == MOUSEBUTTONDOWN and event.button == 1: # Left mouse button pressed
                    hover = self.md_event(event.pos, blits) # Go to mouse down event handler function
                    self.handle_text(hover)
                elif event.type == MOUSEBUTTONUP and event.button == 1: # Left mouse button released
                    # Update metronome
                    if (metronome.pos_x <= event.pos[0] <= metronome.pos_x + metronome.width and metronome.pos_y <= event.pos[1] <= metronome.pos_y + metronome.height) and hover == 'metronome':
                        metronome.update()
                    next_action = self.mu_event(event.pos, hover) # Go to mouse release event handler function
                    if next_action in ('main_menu', 'credits'): # If the program needs to send a call back
                        return next_action # Returns the call back
                    elif next_action is None: # If the user released the mouse on nothing
                        blits = default.copy() # Reset the blits array to the default blits
                    elif isinstance(next_action,float): # If the return value is a float then the volume slider was interacted with
                        metronome.overwrite_vol(next_action) # Overwrite the metronome volume
                elif event.type == MOUSEMOTION: # Mouse movement event
                    self.mm_event(event.pos) # Go to mouse movement event handler
                elif event.type == KEYDOWN: # Keyboard key pressed event
                    if event.key == 27:  # ESCAPE = 27
                        return 'main_menu' # Send a main_menu call back
                    elif self.vol_slider.typing: # If typing mode is activated for the volume slider
                        self.vol_text_update(event.key) # Update the volume slider text value
                        metronome.overwrite_vol(self.vol_slider.get_vol()) # Overwrite the volume
                    elif self.bpm_slider.typing: # If the typing mode is activated for the bpm slider
                        self.bpm_text_update(event.key) # Update the bpm slider text value
                elif event.type == metronome.metronome_tick: # Metronome tick event
                    metronome.overwrite_bpm(metronome.get_bpm()) # Overwrite the bpm to send another tick
                    metronome.play() # Play a sound

            # For every obj in the blits array
            for obj in blits:
                screen.blit(obj.surf, obj.pos) # Blit the object
            # Refresh the volume slider
            self.vol_slider.refresh(screen)
            # Refresh the bpm slider
            self.bpm_slider.refresh(screen)
            # Refresh the metronome
            metronome.refresh(screen)
            # Refresh the screen
            pygame.display.update()

    # Upon the event of holding a mouse button down, depending on the position,
    # images or sliders must change
    def md_event(self, pos, blits):
        #initialize return value
        event = None
        # Quit button pressed
        if 60 <= pos[0] <= 160 and 60 <= pos[1] <= 175:
            # Replace the return button with the return button pressed image
            index = blits.index(self.images['quit'])
            blits[index] = self.images['quit_pressed']
            event = 'quit'
        # Credits button pressed
        elif 60 <= pos[0] <= 396 and 450 <= pos[1] <= 568:
            # Replace the credits button with the credits button pressed image
            index = blits.index(self.images['credits_button'])
            blits[index] = self.images['credits_button_pressed']
            event = 'credits'
        elif 1120 <= pos[0] <= 1220 and 60 <= pos[1] <= 160: # Metronome button location
            event = 'metronome'
        # Link pressed within source table
        elif 190 <= pos[0] <= 680 and 215 <= pos[1] <= 448:
            event = 'source'
        # Volume text value pressed
        elif 675 <= pos[0] <= 765 and 70 <= pos[1] <= 105:
            self.vol_slider.typing = True
            event = 'vol txt'
        # BPM text value pressed
        elif 675 <= pos[0] <= 765 and 105 <= pos[1] <= 140:
            self.bpm_slider.typing = True
            event = 'bpm txt'
        # Volume slider pressed, slider should change to where pressed
        elif self.vol_slider.barx <= pos[0] <= self.vol_slider.barxmax + 10 and self.vol_slider.bary <= pos[1] <= self.vol_slider.bary + 20:
            self.vol_slider.slider_rect.move_ip(pos[0] - self.vol_slider.slider_rect.x, 0)
            self.vslider_pressed = True
            # If the slider is outside it's bounds then this if statement corrects it
            if self.vol_slider.slider_rect.left < self.vol_slider.barx:
                self.vol_slider.slider_rect.x = self.vol_slider.barx
            elif self.vol_slider.slider_rect.right > self.vol_slider.barxmax + 10:
                self.vol_slider.slider_rect.x = self.vol_slider.barxmax
            self.vol_slider.update()
            event = 'vslider'
        # Metronome BPM slider pressed, slider should change to where pressed
        elif self.bpm_slider.barx <= pos[0] <= self.bpm_slider.barxmax + 10 and self.bpm_slider.bary <= pos[1] <= self.bpm_slider.bary + 20:
            self.bpm_slider.slider_rect.move_ip(pos[0] - self.bpm_slider.slider_rect.x, 0)
            self.bslider_pressed = True
            # If the slider is outside it's bounds then this if statement corrects it
            if self.bpm_slider.slider_rect.left < self.bpm_slider.barx:
                self.bpm_slider.slider_rect.x = self.bpm_slider.barx
            elif self.bpm_slider.slider_rect.right > self.bpm_slider.barxmax + 10:
                self.bpm_slider.slider_rect.x = self.bpm_slider.barxmax
            self.bpm_slider.update()
            event = 'bpmslider'
        return event

    # Upon the event of realising the mouse button, depending on the position,
    # images or sliders must change
    def mu_event(self, pos, hover):
        # Quit button pressed, return to the main menu
        if 60 <= pos[0] <= 160 and 60 <= pos[1] <= 160 and hover == 'quit':
            return 'main_menu'
        # Credits button pressed, go to credits screen
        elif 60 <= pos[0] <= 396 and 450 <= pos[1] <= 568 and hover == 'credits':
            return 'credits'
        else:
            # Link clicked, source link opened
            if 190 <= pos[0] <= 680 and 215 <= pos[1] <= 425 and hover == 'source':
                self.source_open(pos)
            # Change variable if either slider is pressed
            elif self.vslider_pressed:
                self.vslider_pressed = False
                vol = round((self.vol_slider.slider_rect.x - self.vol_slider.barx) / 190, 2)
                new_settings('volume', vol) # Write the new value to settings
                return float(vol)
            elif self.bslider_pressed:
                self.bslider_pressed = False
                bpm = round(((self.bpm_slider.slider_rect.x - self.bpm_slider.barx) * 215 / 190) + 35)
                new_settings('bpm', bpm) # Write the new value to settings
                return bpm
            return None

    # Handle mouse movement events
    def mm_event(self, pos):
        # If the volume slider is pressed, move rectangle to match new mouse x position
        if self.vslider_pressed:
            self.vol_slider.slider_rect.move_ip(pos[0] - self.vol_slider.slider_rect.x, 0)
            self.vol_slider.update()
        # If the mouse is outside of the slider, slider updated to match maximum values
        if self.vol_slider.slider_rect.left < self.vol_slider.barx:
            self.vol_slider.slider_rect.x = self.vol_slider.barx
            self.vol_slider.update()
        elif self.vol_slider.slider_rect.right > self.vol_slider.barxmax + 10:
            self.vol_slider.slider_rect.x = self.vol_slider.barxmax
            self.vol_slider.update()
        # If the Metronome BPM slider pressed, move rectangle to match new mouse x position
        if self.bslider_pressed:
            self.bpm_slider.slider_rect.move_ip(pos[0] - self.bpm_slider.slider_rect.x, 0)
            self.bpm_slider.update()
        # If the mouse is outside of the slider, slider updated to match maximum values
        if self.bpm_slider.slider_rect.left < self.vol_slider.barx:
            self.bpm_slider.slider_rect.x = self.vol_slider.barx
            self.bpm_slider.update()
        elif self.bpm_slider.slider_rect.right > self.bpm_slider.barxmax + 10:
            self.bpm_slider.slider_rect.x = self.bpm_slider.barxmax
            self.bpm_slider.update()

    # This function handles the text for the volume and bpm if another mouse down is pressed
    def handle_text(self, hover):
        if self.vol_slider.typing and hover != 'vol txt': # If the vol text was pressed and the press is not volume
            self.vol_slider.update() # Update the volume slider text
            self.vol_txt = '' # Set the user input to an empty string
            self.vol_slider.typing = False # Turn off typing mode
        elif self.bpm_slider.typing and hover != 'bpm txt':
            self.bpm_slider.update() # Update the bpm slider text
            self.bpm_txt = '' # Set the user input to an empty string
            self.bpm_slider.typing = False # Turn off typing mode
        elif hover is None: # If the mouse down wasn't on anything
            self.vol_slider.update()
            self.bpm_slider.update(self.bpm_slider.get_bpm())
            self.vol_txt = ''
            self.bpm_txt = ''
            self.vol_slider.typing = False
            self.bpm_slider.typing = False

    # Method to handle volume changes via text
    def vol_text_update(self, key):
        # Pygame keys for keyboard buttons 0-9
        pg_numbers = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                      pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
        # Numpad pygame keys
        numpad_pg_numbers = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3,
                             pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7,
                             pygame.K_KP8, pygame.K_KP9]
        # Enter pressed, change volume to entered value
        if key == pygame.K_RETURN:
            self.vol_slider.typing = False
            # If nothing changed, return to old value
            if self.vol_txt == '':
                self.vol_slider.update()
            else:
                if int(self.vol_txt) > 100:
                    self.vol_txt = 1
                else:
                    self.vol_txt = int(self.vol_txt)/100

                # Write new value to settings.txt and update things depending on volume
                # Volume value is stored as a float: 100% = 1, 5% = 0.05
                new_settings('volume', self.vol_txt)
                self.vol_slider.update(round(self.vol_txt*100))
                self.vol_slider.slider_rect.x = self.vol_slider.barx + self.vol_txt*190

                self.vol_txt = ''
        # Allow for backspacing of volume number
        elif key == pygame.K_BACKSPACE:
            self.vol_txt = self.vol_txt[:-1]
            self.vol_slider.update(self.vol_txt)
        # Only allow input from 0-9, and add to text
        elif (key in pg_numbers or key in numpad_pg_numbers) and len(self.vol_txt) < 3:
            if key in pg_numbers:
                self.vol_txt += str(pg_numbers.index(key))
            elif key in numpad_pg_numbers:
                self.vol_txt += str(numpad_pg_numbers.index(key))
            self.vol_slider.update(self.vol_txt)

    # Method to handle bpm changes via text
    def bpm_text_update(self, key):
        # Pygame keys for keyboard buttons 0-9
        pg_numbers = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                      pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
        # Numpad pygame keys
        numpad_pg_numbers = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3,
                             pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7,
                             pygame.K_KP8, pygame.K_KP9]
        # Enter pressed, change bpm to entered value
        if key == pygame.K_RETURN:
            self.bpm_slider.typing = False
            # If nothing changed, return to old value
            if self.bpm_txt == '':
                self.bpm_slider.update()
            else:
                if int(self.bpm_txt) < 35:
                    self.bpm_txt = 35
                if int(self.bpm_txt) > 250:
                    self.bpm_txt = 250
                else:
                    self.bpm_txt = int(self.bpm_txt)

                # Write new value to settings.txt and update things depending on BPM
                new_settings('bpm', self.bpm_txt)
                self.bpm_slider.update(self.bpm_txt)
                self.bpm_slider.slider_rect.x = self.bpm_slider.barx + (self.bpm_txt-35)/215*190
                self.bpm_txt = ''
        # Allow for backspacing of volume number
        elif key == pygame.K_BACKSPACE:
            self.bpm_txt = self.bpm_txt[:-1]
            self.bpm_slider.update(self.bpm_txt)
        # Only allow input from 0-9, and add to text
        elif (key in pg_numbers or key in numpad_pg_numbers) and len(self.bpm_txt) < 3:
            if key in pg_numbers:
                self.bpm_txt += str(pg_numbers.index(key))
            elif key in numpad_pg_numbers:
                self.bpm_txt += str(numpad_pg_numbers.index(key))
            self.bpm_slider.update(self.bpm_txt)

    # Method to open link to source websites if pressed
    @staticmethod
    def source_open(pos):
        if 190 <= pos[0] <= 680:
            if 238 < pos[1] <= 273:
                wb.open_new('http://denhaku.com/')
            elif 273 < pos[1] <= 308:
                wb.open_new('https://freesound.org/')
            elif 308 < pos[1] <= 343:
                wb.open_new('http://www.burnkit2600.com/')
            elif 343 < pos[1] <= 378:
                wb.open_new('http://trxcymbals.com/')
            elif 413 < pos[1] <= 448:
                wb.open_new('http://theremin.music.uiowa.edu/MISpiano.html')


    # Method to load all objects used in the settings
    def load_images(self):
        self.images = {}

        # Cover all previous surfaces
        # Any other covers are to ensure that the buttons load properly
        cover = pygame.Surface((1280, 720))
        cover.fill((255, 255, 255))
        cover = GameObject(cover, (0, 0))
        self.images['background'] = cover

        # Load return button
        quit_button = pygame.image.load("resources/main_menu/Quit_Button_new.png")
        quit_button = pygame.transform.scale(quit_button, (100, 115))
        quit_button = GameObject(quit_button, (60, 60))
        self.images['quit'] = quit_button

        # Load pressed return button
        quit_button_p = pygame.image.load("resources/main_menu/Quit_Button_Pressed_new.png")
        quit_button_p = pygame.transform.scale(quit_button_p, (100, 115))
        quit_button_p = GameObject(quit_button_p, (60, 60))
        self.images['quit_pressed'] = quit_button_p

        # Load credits button
        cred_button = pygame.image.load("resources/settings_screen/Credits_button.png")
        cred_button = pygame.transform.scale(cred_button, (336, 118))
        cred_button = GameObject(cred_button, (60, 450))
        self.images['credits_button'] = cred_button

        # Load pressed credits button
        cred_button_p = pygame.image.load("resources/settings_screen/Credits_button_pressed.png")
        cred_button_p = pygame.transform.scale(cred_button_p, (336, 118))
        cred_button_p = GameObject(cred_button_p, (60, 450))
        self.images['credits_button_pressed'] = cred_button_p

        # Load interactive table with all website sources
        sound_credits = pygame.image.load("resources/settings_screen/Sound_credits2.png")
        sound_credits = pygame.transform.scale(sound_credits, (620, 245))
        sound_credits = GameObject(sound_credits, (60, 203))
        self.images['sound credit'] = sound_credits

        slider_exp = pygame.image.load("resources/settings_screen/Slider_exp.png")
        slider_exp = pygame.transform.scale(slider_exp, (600, 65))
        slider_exp = GameObject(slider_exp, (180, 140))
        self.images['slider exp'] = slider_exp


# Stand alone method, to read and write onto the
# settings.txt file according to changes made in the settings
def new_settings(key, value):
    # Loop over every line of the settings file
    with open('settings.txt', 'r', encoding="utf8") as file:
        for line in file:
            temp = line
            line = line.strip().split(": ") # Split the file into data and key
            if line[0] == key: # If the key is the same as the value that should be replace
                break
    with open('settings.txt', 'r', encoding="utf8") as file: # Open the settings file in read mode
        data = file.read() # Store the data
        if key == 'bpm':
            data = data.replace(temp, 'bpm: ' + str(value) + '\n') # Replace the old value with the new value
        elif key == 'volume':
            data = data.replace(temp, 'volume: ' + str(value) + '\n')

    with open('settings.txt', 'w', encoding="utf8") as file:# Open the settings file in write mode
        file.write(data) # Write the new data
