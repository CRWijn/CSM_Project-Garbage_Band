import os
import sys
import time
import pygame
import mod_error
import mod_main_menu
import mod_credits
import mod_drums
import mod_guitar
import mod_piano
import mod_settings

class Game:
    def __init__(self):
        # Change Directory to one above this one
        os.chdir(os.path.dirname(os.getcwd()))

        #Initialize pygame and some key modules
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.init()

        #Icon of the program (displayed in the top left when runned)
        icon = pygame.image.load("resources/GarbageBandLogo.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("GarbageBand V1.4")#Program title

        #Creating the window with width 1280 and height 720 with a white background
        self.screen = pygame.display.set_mode((1280, 720))
        self.screen.fill((255, 255, 255))

        # Check the settings file
        self.check_settings()

        #Display logo function call
        Game.display_logo(self.screen)

        #Code transfer handling
        try:
            mode = 'main_menu'
            while True:
                mode = Game.mode(self.screen, mode)
                # If quit mode is returned then the program should exit
                if mode == 'quit':
                    pygame.quit()
                    break
        except (ValueError, IndexError, NameError, RuntimeError) as error:  # If an error occurs
            mod_error.handle_error(error)  # Go to the error handling function
        finally:  # For both if an error occurred and the program ran without error
            sys.exit()  # Exit the code

    @staticmethod
    def display_logo(screen):
        #Load the logo and display it for 2 seconds
        logo = pygame.image.load("resources/logo_transparent.png")#Load logo image
        logo = pygame.transform.scale(logo, (400, 400))#Scale it
        logo_rect = logo.get_rect()
        rect = logo_rect.move((460, 160))#Move it
        screen.blit(logo, rect)#Place it on the screen
        pygame.display.update()#Update the display
        time.sleep(2)

    @staticmethod
    def mode(screen, mode):
        if mode == 'main_menu':#Main menu call
            mode = mod_main_menu.MainMenu(screen)
        elif mode == 'piano':#Piano module call
            mode = mod_piano.PianoClass(screen)
        elif mode == 'guitar':#Guitar module call
            mode = mod_guitar.GuitarClass(screen)
        elif mode == 'drums':#Drums module call
            mode = mod_drums.DrumsClass(screen)
        elif mode == 'settings':#Settings module call
            mode = mod_settings.Settings(screen)
        elif mode == 'credits':#Credits module call
            mode = mod_credits.Credits(screen)
        else:
            pygame.quit()
            raise NameError("This module does not exist")  # Error handle
        return mode.mode

    # Check if settings.txt file exists, if not then create a new one
    @staticmethod
    def check_settings():
        # Try opening the file
        try:
            with open("settings.txt", "r", encoding="utf8") as file:
                pass
        except FileNotFoundError: # If an error occurs it creates a settings file
            with open("settings.txt", "x", encoding="utf8") as file:
                file.write("volume: 1.0\nbpm: 100")

if __name__ == '__main__':
    Game()
