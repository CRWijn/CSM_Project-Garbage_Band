import pygame
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

class PianoClass:
    def __init__(self, screen):
        # Load all images for the piano screen
        self.load_images()

        # Place the images that the screen opens with in a default
        default = [self.images['cover'], self.images['quit_button']] + [self.images[key] for key in self.images if 'oc' in key if '_pressed' not in key]

        # Set the number of channels that will be used in this module (need to include a channel for the metronome)
        pygame.mixer.set_num_channels(10)
        # Piano loop call
        self.mode = self.piano_loop(screen, default)

    def piano_loop(self, screen, blits):
        octave = [None, None] # Initialization of the two octaves that can be played at once
        vol = float(VolumeSlider.get_vol()) # Get the volume (read from settings.txt)

        metronome = Metronome(vol) # Create the metronome object

        self.key_chan, channels = PianoClass.make_channels() # Create the channels and the channel dictionary

        # Game loop
        while True:
            # Loop over the events that occured this iteration
            for event in pygame.event.get():
                # If the X in the top right is pressed send back a 'quit' command
                if event.type == QUIT:
                    return 'quit'
                # If a keyboard key is pressed
                elif event.type == KEYDOWN:
                    if event.key == 27:  # ESCAPE = 27
                        return 'main_menu'
                    else:
                        event.unicode = event.unicode.lower()
                        # Calling keypress handler function
                        self.handle_keypress(event.unicode, channels, octave, vol, blits)
                # If key is let go: drown out the sound if it's still being played
                elif event.type == KEYUP:
                    event.unicode = event.unicode.lower()
                    for chid in range(len(channels)): # Loop over the channels
                        if event.unicode == self.key_chan["Channel " + str(chid)] and octave[0] is not None: # If key let go is in the active channels
                            self.remove(event.unicode, blits) # Remove the animation picture for this key
                            self.key_chan["Channel " + str(chid)] = None # Set the channel activity to none
                            channels[chid].fadeout(750) # Fade out the sound over 750 ms
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # If the right mouse button is pressed
                    pressed = PianoClass.find_button(event.pos) # Find if a button is perssed
                    if pressed is not None: # If the press occured on a button
                        self.handle_press(pressed, octave, blits) # Mouse press handle function call
                elif event.type == MOUSEBUTTONUP and event.button == 1: # If the right mouse button is let go
                    if 60 <= event.pos[0] <= 160 and 60 <= event.pos[1] <= 160 and pressed == 'quit': # If the button pressed is the quit button
                        return 'main_menu' # Send back a call to the main menu
                    elif metronome.pos_x <= event.pos[0] <= metronome.pos_x + metronome.width and metronome.pos_y <= event.pos[1] <= metronome.pos_y + metronome.height and pressed == 'metronome': # If the metronome button is pressed
                        metronome.update() # Update the metronome
                    else:
                        if self.images['quit_button_pressed'] in blits: # If the mouse let go wasn't on the quit button or the metronome and the quit button was previously pressed
                            index = blits.index(self.images['quit_button_pressed'])
                            blits[index] = self.images['quit_button'] # Unpress the quit button
                elif event.type == metronome.metronome_tick: # If the metronome needs to play
                    metronome.play() # Tick the metronome

            for obj in blits: # For every object that needs to be put on the screen
                screen.blit(obj.surf, obj.pos) # Put it on the screen
            # Update the graphics of the metronome
            metronome.refresh(screen)
            # Refresh the screen
            pygame.display.update()

    # Keyboard press handling function
    def handle_keypress(self, unicode, channels, octave, vol, blits):
        # Get the key-note pair mapping
        key_note_mapping_lower_uh, key_note_mapping_uh, key_note_mapping_lower_lh, key_note_mapping_lh = PianoClass.get_key_note_mapping()
        # Lower side lower octave key pressed:
        if unicode in key_note_mapping_lower_lh and octave[0] is not None: # If the key pressed is in the lower half and on the lower octave
            key = pygame.mixer.Sound("resources/sounds/Piano/Octave " + str(octave[0] - 1) + "/" + key_note_mapping_lower_lh[unicode] + ".wav") # Load the corresponding sound
            self.play(channels, unicode, key, vol, blits) # Play the note
        # Lower side normal octave key pressed
        elif unicode in key_note_mapping_lh and octave[0] is not None: # If the key pressed is in the lower half and on the current octave
            key = pygame.mixer.Sound("resources/sounds/Piano/Octave " + str(octave[0]) + "/" + key_note_mapping_lh[unicode] + ".wav")
            self.play(channels, unicode, key, vol, blits)
        # Upper side lower octave key pressed:
        elif unicode in key_note_mapping_lower_uh and octave[1] is not None: # If the key pressed is in the upper half and on the lower octave
            key = pygame.mixer.Sound("resources/sounds/Piano/Octave " + str(octave[1] - 1) + "/" + key_note_mapping_lower_uh[unicode] + ".wav")
            self.play(channels, unicode, key, vol, blits)
        # Upper side normal octave key pressed
        elif unicode in key_note_mapping_uh and octave[1] is not None: # If the key pressed is in the upper half and on the lower octave
            key = pygame.mixer.Sound("resources/sounds/Piano/Octave " + str(octave[1]) + "/" + key_note_mapping_uh[unicode] + ".wav")
            self.play(channels, unicode, key, vol, blits)

    def play(self, channels, unicode, key, vol, blits):
        for chid in range(len(channels)): # Find a channel that isn't busy
            if self.key_chan["Channel " + str(chid)] is None and not channels[chid].get_busy():
                if unicode not in self.key_chan.values(): # If the note is not being played in any channel (avoids duplicate sounds)
                    self.add(unicode, blits) # Add the animation to the piano key
                    self.key_chan["Channel " + str(chid)] = unicode # Add the note to the channel dictionaries
                    channels[chid].set_volume(vol) # Set the channel volume
                    channels[chid].play(key) # Play the audio of the note

    # Add the key animation to the piano on the screen
    def add(self, key, blits):
        key = PianoKey(key) # Make a piano key object
        key = GameObject(self.images[key.typ], (key.pos_x, key.pos_y)) # Turn the piano key object into a game object
        blits.append(key) # Add the object to the list of objects to be placed on the screen

    # Remove the key animation from the piano on the screen
    def remove(self, key, blits):
        key = PianoKey(key)
        key = GameObject(self.images[key.typ], (key.pos_x, key.pos_y))
        blits.remove(key) # Remove the object from the list of objects to be placed on the screen

    # Handle mouse button presses
    def handle_press(self, pressed, octave, blits):
        if pressed == 'quit': # Return button was pressed
            index = blits.index(self.images['quit_button'])
            blits[index] = self.images['quit_button_pressed'] # Replace the default return button with the pressed return button
        elif not pressed == 'metronome': # Metronome doesn't do anything here so it is ignore
            pressed = int(pressed)
            if octave[0] is None and octave[1] is None: # If neither octave is being used
                octave[0] = pressed
                index = blits.index(self.images['oc' + str(octave[0])]) # Press the respective octave button
                blits[index] = self.images['oc' + str(octave[0]) + '_pressed'] # Add it to the list of objects to be blitted
                blits.append(self.images['piano_lh']) # Add the lower half piano to the list of objects to be blitted
            elif octave[0] is not None and octave[1] is None: # If one octave button is already pressed
                if not octave[0] == pressed: # Check if the new one pressed is the same as the already pressed one
                    octave[1] = pressed
                    index = blits.index(self.images['oc' + str(octave[1])])
                    blits[index] = self.images['oc' + str(octave[1]) + '_pressed'] # Press the new octave button
                    blits.append(self.images['piano_uh']) # Add the upper half piano to the list of objects to be blitted onto the screen
            elif octave[0] is not None and octave[1] is not None: # If both octaves are active
                index1 = blits.index(self.images['oc' + str(octave[0]) + '_pressed'])
                index2 = blits.index(self.images['oc' + str(octave[1]) + '_pressed'])
                blits[index1] = self.images['oc' + str(octave[0])]
                blits[index2] = self.images['oc' + str(octave[1])] # The above code resets the buttons to their default
                octave[0] = pressed
                octave[1] = None
                index = blits.index(self.images['oc' + str(octave[0])])
                blits[index] = self.images['oc' + str(octave[0]) + '_pressed'] # Press in the new active octave button
                blits.remove(self.images['piano_uh']) # Remove the upper half piano from the list of objects

    # Find the button pressed function for mouse clicks
    @staticmethod
    def find_button(pos):
        button = None
        if 360 <= pos[0] <= 430 and pos[1] <= 70: # Octave 1 button location
            button = '1'
        elif 458 <= pos[0] <= 528 and pos[1] <= 70: # Octave 2 button location
            button = '2'
        elif 556 <= pos[0] <= 626 and pos[1] <= 70: # Octave 3 button location
            button = '3'
        elif 654 <= pos[0] <= 724 and pos[1] <= 70: # Octave 4 button location
            button = '4'
        elif 752 <= pos[0] <= 822 and pos[1] <= 70: # Octave 5 button location
            button = '5'
        elif 850 <= pos[0] <= 920 and pos[1] <= 70: # Octave 6 button location
            button = '6'
        elif 60 <= pos[0] <= 160 and 60 <= pos[1] <= 160: # Return button location
            button = 'quit'
        elif 1120 <= pos[0] <= 1220 and 60 <= pos[1] <= 160: # Metronome button location
            button = 'metronome'
        return button

    # Function to load all images used in this module
    def load_images(self):
        self.images = {} # Image dictionary

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


        # Load the unpressed and pressed octave buttons
        for octave in range(1, 7):
            img_unpressed = pygame.image.load("resources/piano_screen/Octave" + str(octave) + "_new.png")
            img_unpressed = pygame.transform.scale(img_unpressed, (70, 70))
            self.images['oc' + str(octave)] = GameObject(img_unpressed, (360 + (octave-1)*98, 0))
            img_pressed = pygame.image.load("resources/piano_screen/Octave" + str(octave) + "_Pressed_new.png")
            img_pressed = pygame.transform.scale(img_pressed, (70, 70))
            self.images['oc' + str(octave) + '_pressed'] = GameObject(img_pressed, (360 + (octave-1)*98, 0))

        # Load the black key pressed image
        black_key = pygame.image.load("resources/piano_screen/black_key.png")
        rect = black_key.get_rect()
        black_key = pygame.transform.scale(black_key, (int((680 / 1280) * rect.width), int((250 / 469) * rect.height)))
        self.images['black_key'] = black_key

        # Load the white key: both pressed image
        white_key_both = pygame.image.load("resources/piano_screen/white_key_both.png")
        rect = white_key_both.get_rect()
        white_key_both = pygame.transform.scale(white_key_both, (int((680 / 1280) * rect.width) + 3, int((250 / 469) * rect.height)))
        self.images['white_key_both'] = white_key_both

        # Load the white key: right pressed image
        white_key_right = pygame.image.load("resources/piano_screen/white_key_right.png")
        rect = white_key_right.get_rect()
        white_key_right = pygame.transform.scale(white_key_right, (int((680 / 1280) * rect.width) + 2, int((250 / 469) * rect.height)))
        self.images['white_key_right'] = white_key_right

        # Load the white key: left pressed image
        white_key_left = pygame.image.load("resources/piano_screen/white_key_left.png")
        rect = white_key_left.get_rect()
        white_key_left = pygame.transform.scale(white_key_left, (int((680 / 1280) * rect.width) + 3, int((250 / 469) * rect.height)))
        self.images['white_key_left'] = white_key_left

        # Load the lower half piano image
        piano_lh = pygame.image.load("resources/piano_screen/piano_lh.png")
        piano_lh = pygame.transform.scale(piano_lh, (680, 250))
        self.images['piano_lh'] = GameObject(piano_lh, (300, 441))

        # Load the upper half piano image
        piano_uh = pygame.image.load("resources/piano_screen/piano_uh.png")
        piano_uh = pygame.transform.scale(piano_uh, (680, 250))
        self.images['piano_uh'] = GameObject(piano_uh, (300, 163))

    # Function to get key note pairs dictionaries
    @staticmethod
    def get_key_note_mapping():
        key_note_mapping_lower_uh = {
            'q': 'A',
            '2': 'Bb',
            'w': 'B'
        }
        key_note_mapping_uh = {
            'e': 'C',
            '4': 'Db',
            'r': 'D',
            '5': 'Eb',
            't': 'E',
            'y': 'F',
            '7': 'Gb',
            'u': 'G',
            '8': 'Ab',
            'i': 'A',
            '9': 'Bb',
            'o': 'B'
        }
        key_note_mapping_lower_lh = {
            'z': 'A',
            's': 'Bb',
            'x': 'B'
        }
        key_note_mapping_lh = {
            'c': 'C',
            'f': 'Db',
            'v': 'D',
            'g': 'Eb',
            'b': 'E',
            'n': 'F',
            'j': 'Gb',
            'm': 'G',
            'k': 'Ab',
            ',': 'A',
            'l': 'Bb',
            '.': 'B'
        }
        return (key_note_mapping_lower_uh, key_note_mapping_uh, key_note_mapping_lower_lh, key_note_mapping_lh)

    # Function to make number of channels initialised in the __init__ function
    @staticmethod
    def make_channels():
        channels = []
        key_chan = {}
        for chid in range(pygame.mixer.get_num_channels() - 1):
            chan = pygame.mixer.Channel(chid) # Create a pygame mixer object
            key_chan["Channel " + str(chid)] = None # Put it in the channels dictionary
            channels.append(chan) # Append it to the list of channels
        return (key_chan, channels)

# Piano key object
class PianoKey:
    def __init__(self, key):
        #Mapping from keyboard to the required animation image
        key_typ_mapping = {
            #Upper Half
            'q': 'white_key_both',
            '2': 'black_key',
            'w': 'white_key_left',
            'e': 'white_key_right',
            '4': 'black_key',
            'r': 'white_key_both',
            '5': 'black_key',
            't': 'white_key_left',
            'y': 'white_key_right',
            '7': 'black_key',
            'u': 'white_key_both',
            '8': 'black_key',
            'i': 'white_key_both',
            '9': 'black_key',
            'o': 'white_key_left',
            #Lower Half
            'z': 'white_key_both',
            's': 'black_key',
            'x': 'white_key_left',
            'c': 'white_key_right',
            'f': 'black_key',
            'v': 'white_key_both',
            'g': 'black_key',
            'b': 'white_key_left',
            'n': 'white_key_right',
            'j': 'black_key',
            'm': 'white_key_both',
            'k': 'black_key',
            ',': 'white_key_both',
            'l': 'black_key',
            '.': 'white_key_left'
        }
        key_loc_mapping = {
            # Upper Half
            'q': '396, 164',
            '2': '434, 164',
            'w': '444, 164',
            'e': '494, 164',
            '4': '531, 164',
            'r': '542, 164',
            '5': '580, 164',
            't': '590, 164',
            'y': '640, 164',
            '7': '677, 164',
            'u': '687, 164',
            '8': '725, 164',
            'i': '736, 164',
            '9': '774, 164',
            'o': '784, 164',
            # Lower Half
            'z': '396, 442',
            's': '434, 442',
            'x': '444, 442',
            'c': '494, 442',
            'f': '531, 442',
            'v': '542, 442',
            'g': '580, 442',
            'b': '590, 442',
            'n': '640, 442',
            'j': '677, 442',
            'm': '688, 442',
            'k': '725, 442',
            ',': '736, 442',
            'l': '774, 442',
            '.': '784, 442'
        }
        self.typ = key_typ_mapping[key] # Type of animation picture
        loc = key_loc_mapping[key].split(', ')
        self.pos_x = int(loc[0]) # Animation image x location
        self.pos_y = int(loc[1]) # Animation image y location
