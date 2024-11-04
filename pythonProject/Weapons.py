import pygame
import math
import constantes as cons
import random

class Weapons:
    def __init__(self, image,arrow_image):
        self.original_image = image
        self.angle = 0
        self.imagen = pygame.transform.rotate(self.original_image, self.angle)
        self.forma = self.imagen.get_rect()
        self.arrow_image = arrow_image
        self.fuego = False
        self.last_shot = pygame.time.get_ticks()


    def update_weapon(self, personaje):
        shoot_cooldown = 300
        arrow = None
        self.forma.center = personaje.forma.center

        pos  = pygame.mouse.get_pos()
        x_dist = pos[0] - self.forma.centerx
        y_dist = -(pos[1] - self.forma.centery)
        self.angle = math.degrees(math.atan2(y_dist, x_dist))

        #obtener el click del mouse
        if pygame.mouse.get_pressed()[0] and self.fuego == False and (pygame.time.get_ticks()- self.last_shot) >= shoot_cooldown:
            arrow = Flecha(self.arrow_image, self.forma.centerx,self.forma.centery,self.angle )
            self.fuego = True
            self.last_shot = pygame.time.get_ticks()

        #resetear click del mouse
        if pygame.mouse.get_pressed()[0] == False:
            self.fuego = False

        return arrow

    def draw(self, surface):
        self.imagen = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.imagen, ((self.forma.centerx - int(self.imagen.get_width()/2)),self.forma.centery - int(self.imagen.get_height()/2)))

class Flecha(pygame.sprite.Sprite):
    def __init__(self,image,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.imagen = pygame.transform.rotate(self.original_image, self.angle)
        self.forma = self.imagen.get_rect()
        self.forma.center = (x,y)
        #calcular la velocidad vertical y horizontal basada en el angulo
        self.dx = math.cos(math.radians(self.angle)) * cons.ARROW_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * cons.ARROW_SPEED)

    def update(self,screen_scroll,obstacle_tiles, enemy_list):
        self.forma.x += screen_scroll[0]
        self.forma.y += screen_scroll[1]

        damage = 0
        damage_pos = None

        self.forma.x += self.dx
        self.forma.y += self.dy

        #Verificar si la flecha ha salido de la pantalla
        if self.forma.right < 0 or self.forma.left > cons.ANCHO_VENTANA or self.forma.bottom < 0 or self.forma.top > cons.ALTO_VENTANA:
            self.kill()

        #Verificar si hay colision entre las flechas y los muros
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.forma):
                self.kill()

        #Gestionar las colisiones entre la flecha y los enemigos
        for enemy in enemy_list:
            if enemy.forma.colliderect(self.forma) and enemy.alive:
                damage = 10 + random.randint(-5,5)
                damage_pos = enemy.forma
                enemy.salud -= damage
                enemy.hit = True
                self.kill()
                break
        return damage,damage_pos

    def draw(self,surface):
        surface.blit(self.imagen, ((self.forma.centerx - int(self.imagen.get_width()/2)),self.forma.centery - int(self.imagen.get_height()/2)))

class Fireball(pygame.sprite.Sprite):
    def __init__(self,image,x,y,target_x,target_y):
        pygame.sprite.Sprite.__init__(self)
        x_dist = target_x - x
        y_dist = -(target_y - y)
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        self.original_image = image
        self.imagen = pygame.transform.rotate(self.original_image, self.angle)
        self.forma = self.imagen.get_rect()
        self.forma.center = (x,y)
        #calcular la velocidad vertical y horizontal basada en el angulo
        self.dx = math.cos(math.radians(self.angle)) * cons.FIREBALL_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * cons.FIREBALL_SPEED)

    def update(self,screen_scroll, player):

        self.forma.x += screen_scroll[0]
        self.forma.y += screen_scroll[1]

        self.forma.x += self.dx
        self.forma.y += self.dy

        #Verificar si el proyectil ha salido de la pantalla
        if self.forma.right < 0 or self.forma.left > cons.ANCHO_VENTANA or self.forma.bottom < 0 or self.forma.top > cons.ALTO_VENTANA:
            self.kill()

        if player.forma.colliderect(self.forma) and player.hit == False:
            player.hit = True
            player.last_shot = pygame.time.get_ticks()
            player.salud -= 20
            self.kill()


        #Gestionar las colisiones entre la flecha y los enemigos
    def draw(self,surface):
        surface.blit(self.imagen, ((self.forma.centerx - int(self.imagen.get_width()/2)),self.forma.centery - int(self.imagen.get_height()/2)))



