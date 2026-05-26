import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import sys

def pygame_events(space, myenv, change_target):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if change_target == True and event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            myenv.change_target_point(x, 800-y)


def pygame_events_chat(space, myenv, change_target, chat=None):
    """Extended event handler that also routes keyboard events to the chat panel."""
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Let the chat panel consume keyboard input first
        if chat is not None:
            consumed = chat.handle_event(event)
            if consumed:
                continue   # don't process further

        if change_target and event.type == pygame.MOUSEBUTTONUP:
            # Only respond to clicks inside the sim area (left 800px)
            x, y = pygame.mouse.get_pos()
            if x < 800:
                myenv.change_target_point(x, 800-y)
