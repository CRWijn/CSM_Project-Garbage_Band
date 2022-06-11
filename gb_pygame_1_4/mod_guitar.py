import pygame
from pygame import Color
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
#import mod_main_menu


class GuitarClass:
    def __init__(self, screen, last_chord=None, string_list=None):
        # Various lists of images used throughout the guitar screen
        self.load_images()

        #initialize variables
        self.last_chord = last_chord
        self.string_list = string_list
        self.blits = [self.images['background'], self.images['guitar'], self.images['quit'],
                   self.images['chord button'], self.images['chord exp'], self.images['chord text']]

        # Initiate the settings and run loop
        pygame.mixer.set_num_channels(5)
        self.mode = self.guitar_loop(screen)

    def guitar_loop(self, screen):
        # Retreive volume chosen from settings
        self.vol = float(VolumeSlider.get_vol())
        metronome = Metronome(self.vol)

        # Always start in chord mode, can be switched to notes mode via button
        guitar_style = 'Chord'

        # Event and variable responsible for animating chord
        guitarchord = pygame.USEREVENT + 4
        guitar_cur = 1

        # List for displaying chords or notes, each item represents a string of the guitar
        self.string_list = [None, None, None, None, None, None]
        chord_list = []

        # Variable used to decide if the same button is pressed and released for action to occur
        hover = None
        self.last_chord = None

        # Setup channels and keyboard mappings
        self.key_chan, channels = GuitarClass.make_channels()

        while True:
            for event in pygame.event.get():
                # Handle when the X is pressed in top right of the window
                if event.type == QUIT:
                    return 'quit'
                # Handle keyboard inputs
                elif event.type == KEYDOWN:
                    if event.key == 27:
                        return 'main_menu'
                    else:
                        event.unicode = event.unicode.lower()
                        chord_list = self.kd_event(event.unicode, channels, guitar_style)
                        # guitar_cur represents current node in chord animation, reset at new press
                        # the guitarchord timer must also be reset, always starts at new key press
                        if guitar_style == 'Chord':
                            pygame.time.set_timer(guitarchord, 0)
                            pygame.time.set_timer(guitarchord, 40, True)
                            guitar_cur = 1
                # Handle release of keyboard inputs
                elif event.type == KEYUP:
                    event.unicode = event.unicode.lower()
                    self.ku_event(event.unicode, channels, guitar_style)
                    if guitar_style == 'Chord' and event.unicode == self.last_chord:
                        chord_list = []
                # Handle single mouse press
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if 60 <= event.pos[0] <= 160 and 60 <= event.pos[1] <= 175:
                        self.blits[2] = self.images['quit pressed']
                        hover = 'quit'
                    elif metronome.pos_x <= event.pos[0] <= metronome.pos_x + metronome.width and metronome.pos_y <= event.pos[
                            1] <= metronome.pos_y + metronome.height:
                        hover = 'metronome'
                    elif 472 <= event.pos[0] <= 808 and 20 <= event.pos[1] <= 138:
                        hover = 'switch'
                # Handle release of the single mouse press
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    # Quit button previously pressed and now also released, return to main menu
                    if 60 <= event.pos[0] <= 160 and 60 <= event.pos[1] <= 175 and hover == 'quit':
                        return 'main_menu'
                    else:
                        # Return to unpressed quit button
                        self.blits[2] = self.images['quit']
                        # Check if the metronome was pressed and released, if so turn it on
                        if metronome.pos_x <= event.pos[0] <= metronome.pos_x + metronome.width and metronome.pos_y <= event.pos[
                            1] <= metronome.pos_y + metronome.height and hover == 'metronome':
                            metronome.update()
                        # Check if the switch was pressed and released, if so switch style: chord-> notes or notes->chord
                        elif 472 <= event.pos[0] <= 808 and 20 <= event.pos[1] <= 138 and hover == 'switch':
                            guitar_style = self.switch_mode(guitar_style)
                # METRONOMETICK is event that repeats at speed of Metronome BPM, play sound if metronome is on
                elif event.type == metronome.metronome_tick:
                    metronome.play()
                # guitarchord is event that repeats at 40ms speed, time between notes in a chord strum
                elif event.type == guitarchord and guitar_style == 'Chord' and chord_list:
                    # guitar_cur represents current node in chord animation, add more nodes if chord is continued
                    # new timer for guitarchord started for next note in chord
                    pygame.time.set_timer(guitarchord, 40, True)
                    if guitar_cur < len(chord_list):
                        guitar_cur += 1

            # Initiate screen images
            for obj in self.blits + chord_list[:guitar_cur] + self.string_list:
                if obj is not None:
                    # Both string_list and chord_list items are a GameObject and key responsible
                    # for the item, needed in the key up event. Hence blit only the GameObject
                    if isinstance(obj, list):
                        screen.blit(obj[1].surf, obj[1].pos)
                    else:
                        screen.blit(obj.surf, obj.pos)

            metronome.refresh(screen)
            pygame.display.update()

    # Method responsible for switching between chords mode and notes mode
    def switch_mode(self, guitar_style):
        # Update number of channels and metronome channel
        # Reset the string list, only relevant in chord mode
        # Update the screen to match chosen mode
        if guitar_style == 'Chord':
            pygame.mixer.set_num_channels(10)
            pygame.mixer.Channel(pygame.mixer.get_num_channels() - 1)

            self.string_list = [None, None, None, None, None, None]
            self.blits[3] = self.images['notes button']
            self.blits[4] = self.images['notes exp']
            return 'Notes'
        else:
            pygame.mixer.set_num_channels(5)
            pygame.mixer.Channel(pygame.mixer.get_num_channels() - 1)

            self.string_list = [None, None, None, None, None, None]
            self.last_chord = None
            self.blits[3] = self.images['chord button']
            self.blits[4] = self.images['chord exp']
            return 'Chord'

    # Method to handle in case a key is pressed down: Note/Chord should be played
    def kd_event(self, key, channels, guitar_style):
        chord_mapping, string_start, note_mapping = self.key_to_notation_mapping()
        # Different events require to occur in case of chords/notes mode
        if guitar_style == 'Chord' and key in chord_mapping:
            self.last_chord = key
            # Play the according sound
            file = pygame.mixer.Sound("resources/sounds/Guitar/Chords/" +
                chord_mapping[key][0] + "/" + chord_mapping[key] + ".wav")
            self.play_sound(key, channels, file)

            # Return a list of all notes in a chord, GameObject present for every note. This way
            # the chord can be easily animated as more of the chord is revealed every guitarchord event
            to_display = self.guitar_chord_coords(key)
            chord_list = self.animate_chord(to_display)

            # Display the chord on screen with text, actual chord displayed later
            if chord_mapping[key][1] == 'm':
                chord_txt = chord_mapping[key][:2]
            else:
                chord_txt = chord_mapping[key][0]

            chord_text = self.chord_font.render(chord_txt, True, (0, 0, 0))
            self.blits[5] = GameObject(chord_text, (1087, 500))

            return chord_list
        elif guitar_style == 'Notes':
            # Notes mode only allows one note at a time per string, like an actual guitar
            for string in range(6):
                if key in note_mapping[string]:
                    file = pygame.mixer.Sound("resources/sounds/Guitar/" + str(string+1) +
                        "_String_" + string_start[string] + '/fret' + note_mapping[string][key] + ".wav")
                    self.play_sound(key, channels, file)

                    # Display the note being played on the guitar
                    to_display = self.guitar_note_coords(key)
                    self.string_list[string] = self.animate_note(to_display)
                    break
        return []

    # Method to handle in case a key is released: Note/Chord should stop playing
    def ku_event(self, key, channels, guitar_style):
        # Fade out sound
        self.fade_sound(key, channels)

        # If chord key is released prior to the chord finished playing, reset it
        if guitar_style == 'Chord' and key == self.last_chord:
            chord_text = self.chord_font.render(' ', True, (0, 0, 0))
            self.blits[5] = GameObject(chord_text, (1087, 500))
        # In notes mode 6 independant strings present, can be released at any point
        elif guitar_style == 'Notes':
            for item in self.string_list:
                if item is not None and item[2] == key:
                    # If the note on the current string matches the key, no longer display this note
                    self.string_list[self.string_list.index(item)] = None

    # Upon release of a button the sound should be faded out, and channel emptied
    def fade_sound(self, key, channels):
        for chid in range(len(channels)):
            if key == self.key_chan["Channel " + str(chid)]:
                self.key_chan["Channel " + str(chid)] = None
                channels[chid].fadeout(350)

    # Method to play sounds according to key input
    def play_sound(self, key, channels, file):
        for chid in range(len(channels)):
            if self.key_chan["Channel " + str(chid)] is None and not channels[chid].get_busy():
                if key not in self.key_chan.values():
                    self.key_chan["Channel " + str(chid)] = key
                    channels[chid].set_volume(self.vol)
                    channels[chid].play(file)

    # Method to return a generator function for all notes in a chord
    def guitar_chord_coords(self, key):
        chord_mapping = GuitarClass.key_to_key_mapping()[0]

        return [self.guitar_note_coords(note) for note in chord_mapping[key] if key in chord_mapping] if key in chord_mapping else None

    @staticmethod
    # Method returns coordinates for individual notes
    def guitar_note_coords(key):
        chord_mapping, line_mapping, note_mapping = GuitarClass.key_to_key_mapping()
        coords = chord_mapping
        coords = None
        # Return array for type, position and equivalent key pressed
        if key in note_mapping:
            coords = ['note', note_mapping[key], key]
        elif key in line_mapping:
            coords = ['line', line_mapping[key], key]
        return coords

    # Method to return a list of lists, containing all variables needed to display a chord
    def animate_chord(self, to_display):
        chord = []
        for note in to_display:
            chord.append(self.animate_note(note))
        return chord
    @staticmethod
    # Method to display animation for notes played
    def animate_note(to_display):
        display = None
        if to_display[0] == 'line':
            line_press = pygame.image.load("resources/guitar_screen/line_pressed.png")
            line_press = pygame.transform.scale(line_press, (838, 20))
            display = ['line', GameObject(line_press, to_display[1]), to_display[2]]
        elif to_display[0] == 'note':
            note_press = pygame.image.load("resources/guitar_screen/key_pressed.png")
            note_press = pygame.transform.scale(note_press, (20, 20))
            display = ['note', GameObject(note_press, to_display[1]), to_display[2]]
        return display

    # Method responsible for creating pygame mixer channels and dictionary to match
    @staticmethod
    def make_channels():
        channels = []
        key_chan = {}
        for chid in range(pygame.mixer.get_num_channels() - 1):
            chan = pygame.mixer.Channel(chid)
            key_chan["Channel " + str(chid)] = None
            channels.append(chan)
        return (key_chan, channels)

    # Method to return dictionaries mapping keys to musical notes/chords
    @staticmethod
    def key_to_notation_mapping():
        chord_mapping = {
            '1': 'A_D',
            '2': 'B_D',
            '3': 'C_D',
            '4': 'D_D',
            '5': 'E_D',
            '6': 'F_D',
            '7': 'G_D',

            'q': 'A_U',
            'w': 'B_U',
            'e': 'C_U',
            'r': 'D_U',
            't': 'E_U',
            'y': 'F_U',
            'u': 'G_U',

            'a': 'Am_D',
            's': 'Bm_D',
            'd': 'Cm_D',
            'f': 'Dm_D',
            'g': 'Em_D',
            'h': 'Fm_D',
            'j': 'Gm_D',

            'z': 'Am_U',
            'x': 'Bm_U',
            'c': 'Cm_U',
            'v': 'Dm_U',
            'b': 'Em_U',
            'n': 'Fm_U',
            'm': 'Gm_U'}
        string_start = ['E', 'A', 'D', 'G', 'B', 'E']
        note_mapping = [{
                    't': '0',
                    'r': '1',
                    'e': '2',
                    'w': '3',
                    'q': '4'
                    },{
                    'g': '0',
                    'f': '1',
                    'd': '2',
                    's': '3',
                    'a': '4'
                    },{
                    'b': '0',
                    'v': '1',
                    'c': '2',
                    'x': '3',
                    'z': '4'
                    },{
                    'p': '0',
                    'o': '1',
                    'i': '2',
                    'u': '3',
                    'y': '4'
                    },{
                    ';': '0',
                    'l': '1',
                    'k': '2',
                    'j': '3',
                    'h': '4'
                    },{
                    '/': '0',
                    '.': '1',
                    ',': '2',
                    'm': '3',
                    'n': '4'}]
        return (chord_mapping, string_start, note_mapping)

    # Method returning dictionaries for on screen coordinates of notes
    @staticmethod
    def key_to_key_mapping():
        # Chord represented as if individual notes were pressed
        chord_mapping = {
            '1': ['g', 'c', 'i', 'k', '/'],
            '2': ['d', 'z', 'y', 'h', ','],
            '3': ['s', 'c', 'p', 'l', '/'],
            '4': ['b', 'i', 'j', ','],
            '5': ['t', 'd', 'c', 'o', ';', '/'],
            '6': ['r', 's', 'x', 'i', 'l', '.'],
            '7': ['w', 'd', 'b', 'p', ';', 'm'],

            'q': ['/', 'k', 'i', 'c', 'g'],
            'w': [',', 'h', 'y', 'z', 'd'],
            'e': ['/', 'l', 'p', 'c', 's'],
            'r': [',', 'j', 'i', 'b'],
            't': ['/', ';', 'o', 'c', 'd', 't'],
            'y': ['.', 'l', 'i', 'x', 's', 'r'],
            'u': ['m', ';', 'p', 'b', 'd', 'w'],

            'a': ['g', 'c', 'i', 'l', '/'],
            's': ['d', 'z', 'y', 'j', ','],
            'd': ['f', 'x', 'u', 'k', '.'],
            'f': ['b', 'i', 'j', '.'],
            'g': ['t', 'd', 'c', 'p', ';', '/'],
            'h': ['r', 's', 'x', 'o', 'l', '.'],
            'j': ['r', 's', 'x', 'p', ';', '/'],

            'z': ['/', 'l', 'i', 'c', 'g'],
            'x': [',', 'j', 'y', 'z', 'd'],
            'c': ['.', 'k', 'u', 'x', 'f'],
            'v': ['.', 'j', 'i', 'b'],
            'b': ['/', ';', 'p', 'c', 'd', 't'],
            'n': ['.', 'l', 'o', 'x', 's', 'r'],
            'm': ['/', ';', 'p', 'x', 's', 'r']}
        # Coordinates on screen for notes representing the entire string
        line_mapping = {
                't': (227, 425),
                'g': (227, 458),
                'b': (227, 490),
                'p': (227, 522),
                ';': (227, 556),
                '/': (227, 587)}
        # Coordinates on screen for individual notes
        note_mapping = {
                'r': (989, 425),
                'e': (899, 425),
                'w': (809, 425),
                'q': (724, 425),

                'f': (989, 458),
                'd': (899, 458),
                's': (809, 458),
                'a': (724, 458),

                'v': (989, 489),
                'c': (899, 489),
                'x': (809, 489),
                'z': (724, 489),

                'o': (989, 522),
                'i': (899, 522),
                'u': (809, 522),
                'y': (724, 522),

                'l': (989, 556),
                'k': (899, 556),
                'j': (809, 556),
                'h': (724, 556),

                '.': (989, 587),
                ',': (899, 587),
                'm': (809, 587),
                'n': (724, 587)}
        return (chord_mapping, line_mapping, note_mapping)

    def load_images(self):
        self.images = {}

        # Cover all previous surfaces
        cover = pygame.Surface((1280, 720))
        cover.fill(Color("#ffffff"))
        self.images['background'] = GameObject(cover, (0, 0))

        # Cover part of the screen to swap between chord/note
        swap_cover = pygame.Surface((900, 650))
        swap_cover.fill(Color("#ffffff"))
        self.images['swap cover'] = GameObject(swap_cover, (180, 20))

        # Create guitar
        guitar = pygame.image.load("resources/guitar_screen/GuitarStringsRev.png")
        guitar = pygame.transform.scale(guitar, (833, 237))
        self.images['guitar'] = GameObject(guitar, (234, 400))

        # Create guitar cover
        guitar_cover = pygame.Surface((833, 237))
        guitar_cover.fill(Color("#ffffff"))
        self.images['guitar cover'] = GameObject(guitar_cover, (234, 400))

        # Create the return button
        quit_surf = pygame.image.load("resources/main_menu/Quit_Button_new.png")
        quit_surf = pygame.transform.scale(quit_surf, (100, 115))
        self.images['quit'] = GameObject(quit_surf, (60, 60))

        # Return button but pressed
        quit_surf_pressed = pygame.image.load("resources/main_menu/Quit_Button_Pressed_new.png")
        quit_surf_pressed = pygame.transform.scale(quit_surf_pressed, (100, 115))
        self.images['quit pressed'] = GameObject(quit_surf_pressed, (60, 60))

        # Cover for return button
        quit_cover = pygame.Surface((100, 115))
        quit_cover.fill(Color("#ffffff"))
        self.images['quit cover'] = GameObject(quit_cover, (60, 60))

        # Create the chord switch
        chord_button = pygame.image.load("resources/guitar_screen/Chords_new.png")
        chord_button = pygame.transform.scale(chord_button, (336, 108))
        self.images['chord button'] = GameObject(chord_button, (472, 20))

        # Create the chord explenation
        chord_exp = pygame.image.load("resources/guitar_screen/Chords_key_new2.png")
        chord_exp = pygame.transform.scale(chord_exp, (426, 173))
        self.images['chord exp'] = GameObject(chord_exp, (427, 138))

        # Cover for chord text
        guitar_cover = pygame.Surface((70, 50))
        guitar_cover.fill(Color("#ffffff"))
        self.images['chord text cover'] = GameObject(guitar_cover, (1087, 500))

        # Create the note switch
        note_button = pygame.image.load("resources/guitar_screen/Notes_new.png")
        note_button = pygame.transform.scale(note_button, (336, 108))
        self.images['notes button'] = GameObject(note_button, (472, 20))

        # Create the note explenation
        note_exp = pygame.image.load("resources/guitar_screen/Notes_key_new.png")
        note_exp = pygame.transform.scale(note_exp, (530, 141))
        self.images['notes exp'] = GameObject(note_exp, (375, 150))

        # Create on screen text prompt for chord played
        self.chord_font = pygame.font.Font('freesansbold.ttf', 40)
        chord_text = self.chord_font.render(' ', True, (0, 0, 0))
        self.images['chord text'] = GameObject(chord_text, (1087, 500))
