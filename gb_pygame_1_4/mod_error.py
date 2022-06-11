import pygame
from pygame import QUIT

def handle_error(message):
    icon = pygame.image.load("resources/GarbageBandLogo.png") # Load the icon
    pygame.display.set_icon(icon) # Set the icon to the loaded icon
    pygame.display.set_caption("An error Occurred") # Window title
    err_font = pygame.font.SysFont("freesansbold", 40) # error occurred font
    err_msg_font = pygame.font.SysFont("consolas", 20) # error message font
    err_occ = err_font.render("AN ERROR HAS OCCURRED:", True, (0, 0, 0)) # Render the "AN ERROR HAS OCCURRED text
    err_occ_width = err_occ.get_rect().width # Get the width of the text
    err_msg = err_msg_font.render(str(message), True, (0, 0, 0)) # Render the error message text
    err_msg_width = err_msg.get_rect().width # Get the error message width
    scr_width = err_msg_width + 10 if err_msg_width > err_occ_width else err_occ_width + 10 # Set the screen width based on the error message
    screen = pygame.display.set_mode((scr_width, 100)) # Create the window with the above specified screen width
    screen.fill((255, 255, 255)) # Fill in the screen with white
    screen.blit(err_occ, ((scr_width-err_occ_width)//2, 10)) # Place the error has occurred text
    screen.blit(err_msg, ((scr_width-err_msg_width)//2, 50)) # Place the error message text
    pygame.display.update() # Update the display
    # This loop's sole function is to display the text until the user presses the x button
    while True:
        for event in pygame.event.get():
            # If the X in the top right is close the window and return
            if event.type == QUIT:
                pygame.quit()
                return
