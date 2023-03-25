import pygame
#from pygame import Color
from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYDOWN,
    KEYUP
)
from mod_metronome import Metronome
from obj_game_object import GameObject
from mod_volumeslider import VolumeSlider


class DrumsClass:
    def __init__(self, screen):
        # Load all images for drums screen
        self.load_images()
        # Place the images that the screen opens with in a default
        default = [self.images['cover'], self.images['quit_button'], self.images['drums']]
        # Set the number of channels to 10 (1 reserved for the metronome)
        pygame.mixer.set_num_channels(10)
        # Call drums loop
        self.mode = self.drums_loop(screen, default)

    def drums_loop(self, screen, blits):
        # Read the volume from settings
        vol = float(VolumeSlider.get_vol())
        # Metronome init
        metronome = Metronome(vol)
        # Get the key-beat mapping dictionary
        key_beat_mapping = DrumsClass.get_key_mapping()
        # Make the channels
        self.key_chan, channels = DrumsClass.make_channels()
        # Game loop
        while True:
            # Loop over every event in this iteration
            for event in pygame.event.get():
                if event.type == QUIT: # If the X in the top right is pressed
                    return 'quit' # Send a quit call back
                elif event.type == KEYDOWN: # If a keyboard key is pressed
                    if event.key == 27: # 27 == escape
                        return 'main_menu' # Send a main_menu call back
                    elif event.key in key_beat_mapping: # If it's a drum note
                        self.play_sound(channels, vol, event.key, key_beat_mapping[event.key], blits) # Call the play_sound function
                elif event.type == KEYUP: # Keyboard key is let go
                    self.stop_playing(channels, event.key, blits) # Stop playing functino called
                elif event.type == MOUSEBUTTONDOWN and event.button == 1: # Left mouse button pressed
                    hover = self.find_button(event.pos) # Find if a button is pressed
                    if hover == 'main_menu': # The return button was pressed
                        index = blits.index(self.images['quit_button'])
                        blits[index] = self.images['quit_button_pressed'] # Replace the return button with a pressed return button
                elif event.type == MOUSEBUTTONUP and event.button == 1: # Left mouse button let go
                    pressed = self.find_button(event.pos) # Find where the mouse was when the button is let go
                    if pressed == hover and hover == 'main_menu': # If the mouse let go over the return and it was pressed in send a main_menu call back
                        return pressed # Send the main_menu call back
                    elif pressed == hover and pressed == 'metronome': # If the metronome was pressed and the mouse is let go over it
                        metronome.update() # Update the metronome
                    else:
                        if self.images['quit_button_pressed'] in blits: # If the return button was pressed
                            index = blits.index(self.images['quit_button_pressed'])
                            blits[index] = self.images['quit_button'] # Replace the pressed return button with the normal return button
                elif event.type == metronome.metronome_tick and metronome.switch: # Metronome bpm event
                    metronome.play() # Play the metronome
            # For every object in the blits array
            for obj in blits:
                screen.blit(obj.surf, obj.pos) # Place it in it's respective place
            # Refresh the metronome
            metronome.refresh(screen)
            # Refresh the screen
            pygame.display.update()

    # Add the key animation to the drums on the screen
    def add(self, key, blits, hi_hat = False):
        key = DrumsKey(key) # Make a drums key object
        if hi_hat: # If a hi-hat animation needs to be added
            if self.images['hihat_open'] not in blits and self.images['hihat_closed'] not in blits: # Only add 1 of the two
                key = self.images[key.typ] # Get the key from the images
                blits.append(key) # Append it to the blits array
        else: # If it's not a hi-hat animation
            if self.images[key.typ] not in blits: # Only add it if it's not already in blits
                key = self.images[key.typ]
                blits.append(key) # Add the object to the list of objects to be placed on the screen

    # Remove the key animation from the drums on the screen
    def remove(self, key, blits, hi_hat = False):
        key = DrumsKey(key)
        if hi_hat: # If a hi-hat animation needs to be removed
            # Remove the hi-hat animation that is already in the blits array
            if self.images['hihat_open'] in blits:
                blits.remove(self.images['hihat_open'])
            elif self.images['hihat_closed'] in blits:
                blits.remove(self.images['hihat_closed'])
        else: # Animation to be removed is not a hi-hat animation
            key = self.images[key.typ]
            blits.remove(key) # Remove the object from the list of objects to be placed on the screen

    # Play sound
    def play_sound(self, channels, vol, pressed, mapping, blits):
        key = pygame.mixer.Sound("resources/sounds/Drums/" + mapping + ".wav") # Load the sound
        for chid in range(len(channels)): # Loop over the channels
            if self.key_chan["Channel " + str(chid)] is None and not channels[chid].get_busy(): # If the sound is not in the channel dictionary
                if pressed not in self.key_chan.values(): # Check if the sound is being played in a different channel
                    if pressed in (pygame.K_LEFT, pygame.K_RIGHT): # Hi-hat keys pressed
                        self.add(pressed, blits, True) # Special animation add since it is a hi-hat
                    else:
                        self.add(pressed, blits) # Not special animation
                    self.key_chan["Channel " + str(chid)] = pressed # Put the key pressed in the channels dictionary
                    channels[chid].set_volume(vol) # Set the channel volume
                    channels[chid].play(key) # Play the sound on the respective channel

    # Stop playing a certain key
    def stop_playing(self, channels, key, blits):
        for chid in range(len(channels)): # Loop over the channels
            if key == self.key_chan["Channel " + str(chid)]: # If the key it's looking for is in a specific channel
                if key in (pygame.K_UP, pygame.K_RSHIFT): # If it's a symbal
                    self.remove(key, blits) # Remove it from the blits array
                    self.key_chan["Channel " + str(chid)] = None # Remove it from the channel dictionary
                    channels[chid].fadeout(1000) # Fadeout the sound over 1000 ms
                elif key in (pygame.K_LEFT, pygame.K_RIGHT): # If it's a hi-hat
                    self.remove(key, blits, True) # Remove it from the blits array
                    self.key_chan["Channel " + str(chid)] = None # Remove it from the channel dictionary
                    channels[chid].fadeout(500) # Fade out the sound over 500 ms
                else:
                    self.remove(key, blits) # Remove it from the blits array
                    self.key_chan["Channel " + str(chid)] = None # Remove it from the channels dictionary
                    channels[chid].fadeout(500) # Fadeout the sound over 500 ms

    # Find if a button was pressed
    def find_button(self, pos):
        button = None
        if 60 <= pos[0] <= 160 and 60 <= pos[1] <= 175: # Return button
            button = 'main_menu'
        elif 1120 <= pos[0] <= 1220 and 60 <= pos[1] <= 160: # Metronome button location
            button = 'metronome'
        return button

    # Make channels function
    @staticmethod
    def make_channels():
        channels = []
        key_chan = {}
        # Make the number of channels that was set in the __init__
        for chid in range(pygame.mixer.get_num_channels() - 1):
            chan = pygame.mixer.Channel(chid)
            key_chan["Channel " + str(chid)] = None
            channels.append(chan)
        return key_chan, channels

    # This function simply gets a dictionary
    @staticmethod
    def get_key_mapping():
        # Mapping of keys
        key_beat_mapping = {
            pygame.K_UP: 'crash', # Up Arrow
            pygame.K_RIGHT: 'hihat_open', # Right Arrow
            pygame.K_DOWN: 'bass', # Down Arrow
            pygame.K_LEFT: 'hihat_closed', # Left Arrow
            pygame.K_RSHIFT: 'ride', # Right Shift
            pygame.K_a: 'snare', # A key
            pygame.K_w: 'tom_1', # W key
            pygame.K_d: 'tom_2', # D key
            pygame.K_s: 'tom_floor' # S key
        }
        return key_beat_mapping

    # Load every image and its correct position that is needed for this module and put it in a attribute as a dictionary
    def load_images(self):
        # Add new attribute of dict type
        self.images = {}

        # Background
        cover = pygame.Surface((1280, 720))
        cover.fill((255, 255, 255))
        self.images['cover'] = GameObject(cover, (0, 0))

        # Load the return button image
        quit_surf = pygame.image.load("resources/main_menu/Quit_Button_new.png")
        quit_surf = pygame.transform.scale(quit_surf, (100, 115))
        self.images['quit_button'] = GameObject(quit_surf, (60, 60))

        # Load the pressed return button image
        quit_pressed = pygame.image.load("resources/main_menu/Quit_Button_Pressed_new.png")
        quit_pressed = pygame.transform.scale(quit_pressed, (100, 115))
        self.images['quit_button_pressed'] = GameObject(quit_pressed, (60, 60))

        # Load Drum Kit consisting of 2 tom-toms, 1 ride, 1 crash, 1 hi-hat, 1 bass, 1 floor tom and 1 snare drum
        drums = pygame.image.load("resources/drums_screen/Drum.png")
        drums = pygame.transform.scale(drums, (889, 576))
        self.images['drums'] = GameObject(drums, (150, 90))

        # Load blue highlights for the drum kit
        for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT, pygame.K_a, pygame.K_w, pygame.K_d, pygame.K_s]:
            drums_key = DrumsKey(key)
            pressed_surf = pygame.image.load("resources/drums_screen/" + drums_key.typ + ".png")
            rect = pressed_surf.get_rect()
            pressed_surf = pygame.transform.scale(pressed_surf, (round(rect.width), round(rect.height)))
            self.images[drums_key.typ] = GameObject(pressed_surf, (drums_key.pos_x, drums_key.pos_y))

# Return blue highlight for one part of the Drums and its position according to the given key
class DrumsKey:
    def __init__(self, key):
        key_typ_mapping = DrumsClass.get_key_mapping()
        # Location of the parts on the screen
        key_loc_mapping = {
            pygame.K_UP: '297, 106', # Up arrow
            pygame.K_RIGHT: '158, 261', # Right arrow
            pygame.K_DOWN: '532, 430', # Down arrow
            pygame.K_LEFT: '158, 261', # Left arrow
            pygame.K_RSHIFT: '772, 99', # Right shift
            pygame.K_a: '296, 407', # A key
            pygame.K_w: '447, 236', # W key
            pygame.K_d: '646, 228', # D key
            pygame.K_s: '770, 413' # S Key
        }
        # Add part and its position to self
        self.typ = key_typ_mapping[key]
        loc = key_loc_mapping[key].split(', ')
        self.pos_x = int(loc[0])
        self.pos_y = int(loc[1])
