import pygame

class Quadtree:
    def __init__(self, boundary, capacity, depth=0, max_depth=6):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = depth
        self.max_depth = max_depth
        self.objects = []
        self.divided = False

    def subdivide(self):
        if self.depth >= self.max_depth or self.divided:
            return

        x, y, w, h = self.boundary
        half_w, half_h = w // 2, h // 2

        nw_rect = pygame.Rect(x, y, half_w, half_h)
        ne_rect = pygame.Rect(x + half_w, y, half_w, half_h)
        sw_rect = pygame.Rect(x, y + half_h, half_w, half_h)
        se_rect = pygame.Rect(x + half_w, y + half_h, half_w, half_h)

        self.nw = Quadtree(nw_rect, self.capacity, self.depth + 1, self.max_depth)
        self.ne = Quadtree(ne_rect, self.capacity, self.depth + 1, self.max_depth)
        self.sw = Quadtree(sw_rect, self.capacity, self.depth + 1, self.max_depth)
        self.se = Quadtree(se_rect, self.capacity, self.depth + 1, self.max_depth)
        self.divided = True

    def insert(self, obj):
        if not self.boundary.colliderect(obj.rect):
            return False

        if len(self.objects) < self.capacity or self.depth >= self.max_depth:
            self.objects.append(obj)
            return True
        else:
            if not self.divided:
                self.subdivide()

            if self.nw.insert(obj): return True
            if self.ne.insert(obj): return True
            if self.sw.insert(obj): return True
            if self.se.insert(obj): return True

        return False

    def query(self, range_rect):
        found = []

        if not self.boundary.colliderect(range_rect):
            return found

        for obj in self.objects:
            if range_rect.colliderect(obj.rect):
                found.append(obj)

        if self.divided:
            found.extend(self.nw.query(range_rect))
            found.extend(self.ne.query(range_rect))
            found.extend(self.sw.query(range_rect))
            found.extend(self.se.query(range_rect))

        return found

    def clear(self):
        self.objects = []
        if self.divided:
            self.nw.clear()
            self.ne.clear()
            self.sw.clear()
            self.se.clear()
            self.divided = False  

    def draw(self, screen):
        if self.depth <= self.max_depth:
            pygame.draw.rect(screen, (0, 255, 0), self.boundary, 1)

        if self.divided:
            self.nw.draw(screen)
            self.ne.draw(screen)
            self.sw.draw(screen)
            self.se.draw(screen)
