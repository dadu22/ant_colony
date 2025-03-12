import pygame


pygame.init()

pheremone_image = pygame.Surface((2, 2), pygame.SRCALPHA).convert_alpha()

class Pheromones(pygame.sprite.Sprite):

    _id_counter = 1

    def __init__(self, x, y, lifespan,intensity):
        super().__init__()
        self.x = x
        self.y = y
        self.lifespan = lifespan
        self.intensity = intensity
        self.rect = pheremone_image.get_rect()
        self.color = (84, 149, 232)
        self.id = Pheromones._id_counter
        Pheromones._id_counter += 1

    def update(self):
        if self.lifespan != 0 and self.color ==(84, 149, 232) :
            self.lifespan -= 1


        if self.intensity <0 :
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(pheremone_image, self.color, (1, 1), 6)
        self.rect.center = (self.x, self.y)
        screen.blit(pheremone_image, self.rect)  

    def kill_pheromones(self) :
        self.kill()
