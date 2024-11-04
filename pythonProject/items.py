import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self,x, y, item_type, animation_list, sim_moneda = False):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type # 0: gema, 1: pocion de salud
        self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.sim_moneda = sim_moneda

    def update(self,screen_scroll, player,coin_fx,heal_fx):
        #reposicionar basado en el movimiento de la pantalla
        #Mantener solo la moneda superior fija
        if not self.sim_moneda:
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]


        #Verificar si se ha recolectado un item por el jugador
        if self.rect.colliderect(player.forma):
            #Moneda recolectada
            if self.item_type == 0:
                player.score += 1
                coin_fx.play()
            elif self.item_type == 1:
                player.salud += 10
                heal_fx.play()
                if player.salud > 100:
                    player.salud = 100
            self.kill()

        cooldown_animation = 100

        self.image = self.animation_list[self.frame_index]

        if pygame.time.get_ticks() - self.update_time > cooldown_animation:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self, ventana):
        ventana.blit(self.image, self.rect)