import pygame
from obj_game_object import GameObject

class Metronome:
    def __init__(self, vol, settings = False):
        # Properties of the metronome such as icon placement
        self.pos_x = 1120  # X location
        self.pos_y = 60  # Y location
        self.width = 100  # Icon width
        self.height = 100  # Icon height
        self.count = 0  # Sound count initialisation
        self.switch = False  # Always starts as off
        self.metronome_tick = pygame.USEREVENT + 1  # Create the sound event
        # Load the metronome images
        self.load_images()
        # Load the metronome sounds and create the metronome chnnel
        self.sounds(vol)
        # Set the timer between the metronome sounds
        if settings:
            self.overwrite_bpm(Metronome.get_bpm())
        else:
            pygame.time.set_timer(self.metronome_tick, Metronome.get_bpm())

    # Update the state of the metronome
    def update(self):
        if self.switch: # If it was on
            self.switch = False # Turn it off
        elif not self.switch: # If it was off
            self.switch = True # Turn it on
            self.count = 0 # Set the sound count to 0

    # Refresh the metronome icon on the screen
    def refresh(self, screen):
        if self.switch: # If it's on
            screen.blit(self.switch_on.surf, self.switch_on.pos) # Place the on icon
        elif not self.switch: # If it's off
            screen.blit(self.switch_off.surf, self.switch_off.pos) # Place the off icon

    # Play the sounds of the metronome
    def play(self):
        if self.switch: # Can only play sound when it is on
            if self.count == 0: # If it's the first beat
                self.met_chan.play(self.click) # Play a click in the metronome channel
                self.count += 1 # Change the sound count
            else: # If it is not the first beat
                self.met_chan.play(self.clack) # Play a clack in the metronome channel
                if self.count == 3: # If it's the fourth beat then the next beat should be a click
                    self.count = 0 # Reset the count
                else:
                    self.count += 1 # Otherwise increase it by one

    # Get the beats per minute
    @staticmethod
    def get_bpm():
        level = 100
        with open("settings.txt", 'r', encoding="utf8") as file:
            for line in file: # For every line in the settings
                line = line.strip() # Remove \n's
                line = line.split(": ") # Split the data into elements on the left and right of the colon
                if line[0] == "bpm": # If the data is the bpm data
                    level = int(line[1])
        return int(1000 * round(60 / level, 3)) # Return the bpm

    # Load images used for the metronome
    def load_images(self):
        # Load the swithched on state of the metronome icon
        switch_on = pygame.image.load("resources/metronome/metronome_on_new.png")
        switch_on = pygame.transform.scale(switch_on, (self.width, self.height))
        self.switch_on = GameObject(switch_on, (self.pos_x, self.pos_y))
        # Load the switched off state of the metronome icon
        switch_off = pygame.image.load("resources/metronome/metronome_off_new.png")
        switch_off = pygame.transform.scale(switch_off, (self.width, self.height))
        self.switch_off = GameObject(switch_off, (self.pos_x, self.pos_y))

    # Load the sounds for the metronome and create the channel the metronome uses
    def sounds(self, vol):
        self.met_chan = pygame.mixer.Channel(pygame.mixer.get_num_channels() - 1) # Channel creation with the largest channel id
        self.met_chan.set_volume(vol) # Set the metronome volume
        self.click = pygame.mixer.Sound("resources/metronome/click.wav") # Load the click sound
        self.clack = pygame.mixer.Sound("resources/metronome/clack.wav") # Load the clack sound

    # Overwrite metronome bpm
    def overwrite_bpm(self, bpm):
        pygame.time.set_timer(self.metronome_tick, bpm, True)

    # Overwrite volume
    def overwrite_vol(self, vol):
        self.met_chan.set_volume(vol)
