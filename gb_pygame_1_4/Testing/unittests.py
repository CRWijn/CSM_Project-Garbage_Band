import sys
# Set import path to directory above this one
sys.path.append("..")
import os
import unittest
import pygame
import mod_piano
import mod_drums
import mod_main_menu
import mod_guitar
import mod_bpmslider
import mod_metronome
import obj_game_object
import mod_volumeslider

class TestGB(unittest.TestCase):
    # Test if PianoKey Class returns the expected location and type with the given key
    def test_piano_key(self):
        piano_key = mod_piano.PianoKey('q')
        self.assertEqual('white_key_both', piano_key.typ)
        self.assertEqual(396, piano_key.pos_x)
        self.assertEqual(164, piano_key.pos_y)
        piano_key = mod_piano.PianoKey('s')
        self.assertEqual('black_key', piano_key.typ)
        self.assertEqual(434, piano_key.pos_x)
        self.assertEqual(442, piano_key.pos_y)

    # Test find button method of piano class if it returns the expected values
    def test_piano_class_find_button(self):
        self.assertEqual('1', mod_piano.PianoClass.find_button((360, 70)))
        self.assertEqual('2', mod_piano.PianoClass.find_button((458, 70)))
        self.assertEqual('3', mod_piano.PianoClass.find_button((556, 70)))
        self.assertEqual('4', mod_piano.PianoClass.find_button((654, 70)))
        self.assertEqual('5', mod_piano.PianoClass.find_button((752, 70)))
        self.assertEqual('6', mod_piano.PianoClass.find_button((850, 70)))
        self.assertEqual('quit', mod_piano.PianoClass.find_button((60, 60)))
        self.assertEqual('metronome', mod_piano.PianoClass.find_button((1120, 60)))

    # Test make piano class channel dictionary
    def test_piano_class_make_channels(self):
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)
        key_chan = {}
        for i in range(9):
            key_chan["Channel " + str(i)] = None
        self.assertEqual(key_chan, mod_piano.PianoClass.make_channels()[0])

    # Test get key note mapping method of PianoClass
    def test_piano_class_get_key_note_mapping(self):
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
        ans = (key_note_mapping_lower_uh, key_note_mapping_uh, key_note_mapping_lower_lh, key_note_mapping_lh)
        self.assertEqual(ans, mod_piano.PianoClass.get_key_note_mapping())

    # Test if DrumsKey Class returns the expected location and type with the given key
    def test_drums_key(self):
        self.assertEqual('crash', mod_drums.DrumsKey(pygame.K_UP).typ)
        self.assertEqual(297, mod_drums.DrumsKey(pygame.K_UP).pos_x)
        self.assertEqual(106, mod_drums.DrumsKey(pygame.K_UP).pos_y)

    # Test DrumsClass get_key_mapping method
    def test_drums_class_get_key_mapping(self):
        ans = {
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
        self.assertEqual(ans, mod_drums.DrumsClass.get_key_mapping())

    # Test make drums class channel dictionary
    def test_drums_class_make_channels(self):
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)
        key_chan = {}
        for i in range(9):
            key_chan["Channel " + str(i)] = None
        self.assertEqual(key_chan, mod_drums.DrumsClass.make_channels()[0])

    # Test Main menu find button
    def test_main_class_find_button(self):
        self.assertEqual('piano', mod_main_menu.MainMenu.find_button((51, 316)))
        self.assertEqual('guitar', mod_main_menu.MainMenu.find_button((461, 316)))
        self.assertEqual('drums', mod_main_menu.MainMenu.find_button((871, 316)))
        self.assertEqual('settings', mod_main_menu.MainMenu.find_button((1121, 61)))
        self.assertEqual('quit', mod_main_menu.MainMenu.find_button((61, 61)))
        self.assertEqual(None, mod_main_menu.MainMenu.find_button((0, 0)))

    # Test guitar class guitar note coords
    def test_guitar_class_guitar_note_coords(self):
        self.assertEqual(['note', (809, 458), 's'], mod_guitar.GuitarClass.guitar_note_coords('s'))
        self.assertEqual(['line', (227, 425), 't'], mod_guitar.GuitarClass.guitar_note_coords('t'))

    # Test guitar class make channels
    def test_guitar_class_make_channels(self):
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(5)
        key_chan = {}
        for i in range(4):
            key_chan["Channel " + str(i)] = None
        self.assertEqual(key_chan, mod_guitar.GuitarClass.make_channels()[0])

    # Test bpm slider get_pmb method
    def test_bpm_slider_get_bpm(self):
        # Set to base values
        with open("settings.txt", 'w', encoding="utf8") as file:
            file.write("volume: 1.0\nbpm: 100")
        self.assertEqual(100, mod_bpmslider.BPMSlider.get_bpm())

    #Test bpm slider update mmethod
    def test_bpm_slider_update(self):
        # Set to base values
        with open("settings.txt", 'w', encoding="utf8") as file:
            file.write("volume: 1.0\nbpm: 100")
        bpm = mod_bpmslider.BPMSlider()
        bpm.update()
        self.assertEqual((680, 104), bpm.bpm_value.pos)

    # Test metronome module
    def test_metronome(self):
        # Define metronome object
        met = mod_metronome.Metronome(1.0)
        # Test update method
        met.update()
        self.assertEqual((True, 0), (met.switch, met.count))
        met.update()
        self.assertEqual((False, 0), (met.switch, met.count))

    # Test metronome play method
    def test_metronome_play(self):
        met = mod_metronome.Metronome(1.0)
        met.update()
        met.play()
        self.assertEqual(1, met.count)
        met.play()
        self.assertEqual(2, met.count)
        met.play()
        self.assertEqual(3, met.count)
        met.play()
        self.assertEqual(0, met.count)

    # Test metronome getbpm method
    def test_metronome_getbpm(self):
        # Set to base values
        with open("settings.txt", 'w', encoding="utf8") as file:
            file.write("volume: 1.0\nbpm: 100")
        self.assertEqual(600, mod_metronome.Metronome.get_bpm())
        # Twice as high bpm
        with open("settings.txt", 'w', encoding="utf8") as file:
            file.write("volume: 1.0\nbpm: 200")
        self.assertEqual(300, mod_metronome.Metronome.get_bpm())

    # Test volume slider get vol
    def test_volume_slider_get_vol(self):
        # Set to base values
        with open("settings.txt", 'w', encoding="utf8") as file:
            file.write("volume: 1.0\nbpm: 100")
        self.assertEqual(1.0, mod_volumeslider.VolumeSlider.get_vol())


if __name__ == '__main__':
    # Set path to 2 folders above this one
    os.chdir(os.path.dirname(os.getcwd()))
    os.chdir(os.path.dirname(os.getcwd()))
    # Pygame inits
    pygame.mixer.pre_init()
    pygame.mixer.init()
    pygame.font.init()
    pygame.init()
    # Run the tests
    unittest.main()
