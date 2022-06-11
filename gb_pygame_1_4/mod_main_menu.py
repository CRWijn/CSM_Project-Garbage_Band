import pygame
from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP
)
from obj_game_object import GameObject


class MainMenu:
    def __init__(self, screen):
        # Load all images for the main menu
        self.load_images()

        #The default state of the main menu (no pressed keys)
        default = [self.images[key] for key in self.images if '_pressed' not in key]

        # Start the main menu loop
        self.mode = self.menu_loop(screen, default)

    def menu_loop(self, screen, default):
        # A list of surfaces that need to appear on the screen
        blits = default.copy()

        # Game loop
        while True:
            # Checking all events that happened in this iteration
            for event in pygame.event.get():
                if event.type == QUIT: # If the red X was pressed in the top right
                    return 'quit' # Send back a quit call
                elif event.type == MOUSEBUTTONDOWN and event.button == 1: # If the left mouse button is pressed down
                    hover = MainMenu.find_button(event.pos) # Check if the press is on a button
                    if hover is not None: # If it IS on a button
                        self.press_button(blits, hover)
                elif event.type == MOUSEBUTTONUP and event.button == 1: # If the left mouse button is un-pressed
                    pressed = MainMenu.find_button(event.pos) # Check if the mouse location was on a button
                    if pressed == hover and pressed is not None: # If the un-press is over the same button that was pressed
                        return pressed # Send back a call to the specific button
                    else:
                        blits = default.copy() # Otherwise set all the buttons back to their default state

            # Placing each object onto the screen every single frame
            for obj in blits:
                screen.blit(obj.surf, obj.pos)

            #Update the display
            pygame.display.update()


    def press_button(self, blits, button):
        index = blits.index(self.images[button + "_button"]) # Get the index of the button that needs to be pressed
        blits[index] = self.images[button + "_button_pressed"] # Insert the pressed button image

    @staticmethod
    def find_button(pos):
        # Using the mouse location as pos, the press or un-press location can be found
        if 50 < pos[0] < 386 and 315 < pos[1] < 433:
            return 'piano'
        elif 460 < pos[0] < 796 and 315 < pos[1] < 433:
            return 'guitar'
        elif 870 < pos[0] < 1206 and 315 < pos[1] < 433:
            return 'drums'
        elif 1120 < pos[0] < 1220 and 60 < pos[1] < 160:
            return 'settings'
        elif 60 < pos[0] < 160 and 60 < pos[1] < 160:
            return 'quit'
        else:
            return None # If no buttons were pressed send back a None

    def load_images(self):
        self.images = {} # Image dictionary

        # Background
        cover = pygame.Surface((1280, 720))
        cover.fill((255, 255, 255))
        self.images['cover'] = GameObject(cover, (0, 0))

        # Load the "GarbageBand" image
        text_band_surf = pygame.image.load("resources/main_menu/GB_Text_new.png")
        text_band_surf = pygame.transform.scale(text_band_surf, (789, 193))
        self.images['text_Band'] = GameObject(text_band_surf, (246, 450))

        # Load the piano button image
        piano_button_surf = pygame.image.load("resources/main_menu/Piano_Button_new.png")
        piano_button_surf = pygame.transform.scale(piano_button_surf, (336, 118))
        self.images['piano_button'] = GameObject(piano_button_surf, (50, 315))

        # Load the guitar button image
        guitar_button_surf = pygame.image.load("resources/main_menu/Guitar_Button_new.png")
        guitar_button_surf = pygame.transform.scale(guitar_button_surf, (336, 118))
        self.images['guitar_button'] = GameObject(guitar_button_surf, (460, 315))

        # Load the drums button image
        drums_button_surf = pygame.image.load("resources/main_menu/Drums_Button_new.png")
        drums_button_surf = pygame.transform.scale(drums_button_surf, (336, 118))
        self.images['drums_button'] = GameObject(drums_button_surf, (870, 315))

        # Load the logo image
        logo_surf = pygame.image.load("resources/logo_transparent.png")
        logo_surf = pygame.transform.scale(logo_surf, (250, 262))
        self.images['logo'] = GameObject(logo_surf, (515, 40))

        # Load the return button image
        quit_surf = pygame.image.load("resources/main_menu/Quit_Button_new.png")
        quit_surf = pygame.transform.scale(quit_surf, (100, 115))
        self.images['quit_button'] = GameObject(quit_surf, (60, 60))

        # Load the settings button image
        sett_button_surf = pygame.image.load("resources/main_menu/Settings_new.png")
        sett_button_surf = pygame.transform.scale(sett_button_surf, (100, 100))
        self.images['settings_button'] = GameObject(sett_button_surf, (1120, 60))

        # Load the pressed piano button image
        piano_pressed = pygame.image.load("resources/main_menu/Piano_Button_Pressed_new.png")
        piano_pressed = pygame.transform.scale(piano_pressed, (336, 118))
        self.images['piano_button_pressed'] = GameObject(piano_pressed, (50, 315))

        # Load the pressed guitar button image
        guitar_pressed = pygame.image.load("resources/main_menu/Guitar_Button_Pressed_new.png")
        guitar_pressed = pygame.transform.scale(guitar_pressed, (336, 118))
        self.images['guitar_button_pressed'] = GameObject(guitar_pressed, (460, 315))

        # Load the pressed drums button image
        drums_pressed = pygame.image.load("resources/main_menu/Drums_Button_Pressed_new.png")
        drums_pressed = pygame.transform.scale(drums_pressed, (336, 118))
        self.images['drums_button_pressed'] = GameObject(drums_pressed, (870, 315))

        # Load the pressed settings button image
        settings_pressed = pygame.image.load("resources/main_menu/Settings_Pressed_new.png")
        settings_pressed = pygame.transform.scale(settings_pressed, (100, 100))
        self.images['settings_button_pressed'] = GameObject(settings_pressed, (1120, 60))

        # Load the pressed quit button image
        quit_pressed = pygame.image.load("resources/main_menu/Quit_Button_Pressed_new.png")
        quit_pressed = pygame.transform.scale(quit_pressed, (100, 115))
        self.images['quit_button_pressed'] = GameObject(quit_pressed, (60, 60))
