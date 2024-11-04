import pygame

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.forma = self.image.get_rect()
        self.forma.topleft = (x, y)

    def draw(self,surface):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check for mouseover and clicked conditions
        if self.forma.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        surface.blit(self.image, self.forma)
        return action
