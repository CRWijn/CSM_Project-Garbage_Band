import pygame
from obj_game_object import GameObject

# Class to handle all events related to the volume
class VolumeSlider():
    def __init__(self):
        vol = self.get_vol()
        self.typing = False
        # Static bar properties
        self.barx = 180
        self.bary = 80
        self.barxmax = self.barx + 190
        # Load the bar image onto the surface
        barimg = pygame.image.load("resources/settings_screen/Slider_bar.png")
        self.bars = GameObject(barimg, (self.barx, self.bary + 6))
        # Slider creation
        self.slider = pygame.Surface((10, 20))
        self.slider.fill((0, 0, 0))
        self.sliderx = self.barx + 190 * vol
        slider_rect = self.slider.get_rect()
        self.slider_rect = slider_rect.move((self.sliderx, self.bary))
        # Load text representing current volume
        # Consists of two strings: 'Volume:' and the actual volume float value
        # Defined seperately as volume value can be changed
        self.volume_textx = self.barx + 220
        self.volumex = self.barx + 500
        self.volumey = self.bary - 6
        # Create the font
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        # Render the volume text
        volume_text = self.font.render('Volume:', True, (0, 0, 0))
        self.volume_text = GameObject(volume_text, (self.volume_textx, self.volumey))
        # Render the volume value text
        volume_value = self.font.render(str(round(100 * vol)), True, (0, 0, 0))
        self.volume_value = GameObject(volume_value, (self.volumex, self.volumey))
        # Load the textbox border
        txtboxout = pygame.Surface((68, 34))
        txtboxout.fill((0, 0, 0))
        self.txtboxout = GameObject(txtboxout, (675, 71))
        # Fill the inner text box
        txtboxin = pygame.Surface((64, 30))
        txtboxin.fill((255, 255, 255))
        self.txtboxin = GameObject(txtboxin, (677, 73))

    # Method in case the slider is shifted, the value should update
    def update(self, vol = None):
        # Vol argument is passed if the text should be based on input
        if vol is None:
            # Render and place inputted text
            volume_value = self.font.render(str(round((self.slider_rect.x - self.barx) / 1.9)), True, (0, 0, 0))
            self.volume_value = GameObject(volume_value, (self.volumex, self.volumey))
        else:
            # Render and place text based off of the sliders position
            volume_value = self.font.render(str(vol), True, (0, 0, 0))
            self.volume_value = GameObject(volume_value, (self.volumex, self.volumey))

    #Refresh the volume slider properties
    def refresh(self, screen):
        # Blit all the components of the volume slider in this order
        screen.blit(self.bars.surf, self.bars.pos) # The slider bar
        screen.blit(self.slider, self.slider_rect) # The slider
        if self.typing: # If the user is typing blit the textbox frame
            screen.blit(self.txtboxout.surf, self.txtboxout.pos)
            screen.blit(self.txtboxin.surf, self.txtboxin.pos)
        screen.blit(self.volume_text.surf, self.volume_text.pos) # The text 'Volume:'
        screen.blit(self.volume_value.surf, self.volume_value.pos) # The value of the volume

    # Reads settings.txt file for the current volume
    @staticmethod
    def get_vol():
        # Open the settings file and filter the line with volume:
        level = 1.0
        with open("settings.txt", 'r', encoding="utf8") as file:
            for line in file:
                line = line.strip().split(": ")
                if line[0] == "volume":
                    level = float(line[1])
                    break
        return level # Float value of volume
