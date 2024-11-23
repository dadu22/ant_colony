import pygame


pygame.init()


class Pheromones(pygame.sprite.Sprite):
    def __init__(self, x, y, lifespan,intensity):
        super().__init__()
        self.x = x
        self.y = y
        self.lifespan = lifespan
        self.intensity = intensity
        self.base_size = (2, 2)
        self.image = pygame.Surface(self.base_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.color = (84, 149, 232, 255)

    def update(self):
        if self.lifespan != 0:
            self.lifespan -= 10

        self.intensity -=1
        if self.intensity ==0 :
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(self.image, self.color, (1, 1), 6)
        self.rect.center = (self.x, self.y)
        screen.blit(self.image, self.rect)    
