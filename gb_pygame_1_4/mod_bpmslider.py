import pygame
from obj_game_object import GameObject

# Class to handle all events related to the metronome BPM
class BPMSlider():
    def __init__(self):
        bpm = self.get_bpm()
        self.typing = False
        # Static bar properties
        self.barx = 180
        self.bary = 110
        self.barxmax = self.barx + 190
        # Load the bar image onto the surface
        barimg = pygame.image.load("resources/settings_screen/Slider_bar.png")
        self.bars = GameObject(barimg, (self.barx, self.bary + 6))
        # Slider generation and properties
        self.slider = pygame.Surface((10, 20))
        self.slider.fill((0, 0, 0))
        self.sliderx = self.barx + round(190 * (bpm - 35) / 215)
        self.slider_rect = self.slider.get_rect()
        self.slider_rect = self.slider_rect.move((self.sliderx, self.bary))
        # Load text representing current bpm
        # Consists of two strings: 'Metronome BPM:' and the actual BPM value
        # Defined seperately as BPM value can be changed
        bpm_textx = self.barx + 220
        self.bpmx = self.barx + 500
        self.bpmy = self.bary - 6
        # Create the font
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        # Render the metronome bpm text
        bpm_text = self.font.render('Metronome BPM:', True, (0, 0, 0))
        self.bpm_text = GameObject(bpm_text, (bpm_textx, self.bpmy))
        # Render the bpm value text
        bpm_value = self.font.render(str(bpm), True, (0, 0, 0))
        self.bpm_value = GameObject(bpm_value, (self.bpmx, self.bpmy))
        # Load the textbox border
        txtboxout = pygame.Surface((68, 34))
        txtboxout.fill((0, 0, 0))
        self.txtboxout = GameObject(txtboxout, (675, 102))
        # Fill the inner text box
        txtboxin = pygame.Surface((64, 30))
        txtboxin.fill((255, 255, 255))
        self.txtboxin = GameObject(txtboxin, (677, 104))

    # Method in case the slider is shifted, the value should update
    def update(self, bpm = None):
        # BPM as an argument will show if the text should be overwritten
        if bpm is None:
            # Render the text input from the user
            bpm_value = self.font.render(str(round(((self.slider_rect.x - self.barx) * 215 / 190) + 35)), True, (0, 0, 0))
            self.bpm_value = GameObject(bpm_value, (self.bpmx, self.bpmy))
        else:
            # Render the text based on the position of the slider
            bpm_value = self.font.render(str(bpm), True, (0, 0, 0))
            self.bpm_value = GameObject(bpm_value, (self.bpmx, self.bpmy))

    #Refresh the volume slider properties
    def refresh(self, screen):
        # Blit each bpm slider property on the screen in this order
        screen.blit(self.bars.surf, self.bars.pos) # Slider bar
        screen.blit(self.slider, self.slider_rect) # Slider
        if self.typing:
            # If the user is typing blit the text box frame
            screen.blit(self.txtboxout.surf, self.txtboxout.pos)
            screen.blit(self.txtboxin.surf, self.txtboxin.pos)
        screen.blit(self.bpm_text.surf, self.bpm_text.pos) # Text 'Metronome BPM:'
        screen.blit(self.bpm_value.surf, self.bpm_value.pos) # BPM text value

    # Reads settings.txt file for the current BPM
    @staticmethod
    def get_bpm():
        # Open the settings file and filter the line with bpm
        level = 100
        with open("settings.txt", 'r', encoding="utf8") as file:
            for line in file:
                line = line.strip().split(": ")
                if line[0] == "bpm":
                    level = int(line[1])
                    break
        return level # Integer value of the bpm
