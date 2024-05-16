import pygame
from sys import exit
import random



height = 720
width = 1280
brown = (151, 125, 94)

pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("ant colony")
clock = pygame.time.Clock()
main_surface = pygame.Surface((width,height))
main_surface.fill(brown)
ant_big = pygame.image.load("graphics/ant/ant_2.png")
ant = pygame.transform.scale(ant_big,(100,80))
main_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf',100)
text_surface = main_font.render("ant colony",True,'black')

height_random = [random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),random.randrange(40,630),]
width_random = [random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),random.randrange(15,1175),]


def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        screen.blit(main_surface,(0,0))
        screen.blit(text_surface,((width/2)-250,50))
        for i in range(10):
            screen.blit(ant,(width_random[i],height_random[i]))


        pygame.display.update()
        clock.tick(60)

main_menu()