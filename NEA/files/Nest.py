import pygame
import random
import numpy as np
from files.pygame_background import *
pygame.init()

class SpiderNest:
    def __init__(self):
        self.radius = 10
        self.width = 0
        self.color = (255, 255, 255)  # Dark gray for spider nest

    def draw(self, screen, position):
        pygame.draw.circle(screen, self.color, position, self.radius, self.width)
        self.rect = pygame.Rect(
            position[0] - self.radius,
            position[1] - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Nest():
    def __init__(self):
        self.radius = 10
        self.width = 0
        self.color = (92,64,51)

    def draw(self, screen, position):
        pygame.draw.circle(screen, self.color, position, self.radius, self.width)

        self.rect = pygame.Rect(
            position[0] - self.radius,  # x-coordinate
            position[1] - self.radius,  # y-coordinate
            self.radius * 2,            # width
            self.radius * 2             # height
        )
