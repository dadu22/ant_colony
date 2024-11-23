import pygame
import numpy as np
pygame.init()

HEIGHT = 720
WIDTH = 1280

main_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf',100)
text_surface = main_font.render("ant colony",True,'black')
text_rect = text_surface.get_rect(center = (WIDTH/2,(HEIGHT/2)-50))
begin_text = main_font.render("Click any button to begin",True,'black')
begin_text = pygame.transform.rotozoom(begin_text,0,0.5)
begin_text_rect = begin_text.get_rect(center = (WIDTH/2,HEIGHT-50))

brown = (151, 125, 94)

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))

clock = pygame.time.Clock()
main_surface = pygame.Surface((WIDTH,HEIGHT))
main_surface.fill(brown)
