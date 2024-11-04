import math
import pygame
import constantes as cons
from path_a_star import a_star_search
from arbolIA import Selector, Sequence, Condition, Action

class Character:
    def __init__(self, x, y, salud, animacion_mob, character_type, boss, size):
        self.character_type = character_type
        self.obstacle_tile = []
        self.boss = boss
        self.behavior_tree = None
        self.flip = False
        self.lista_animacion = animacion_mob[character_type]
        self.action = 0  # 0: animacion idle; 1: animacion run; 3: animacion ataque
        self.frame_index = 0
        self.salud = salud
        self.alive = True
        self.score = 0
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.last_attack = pygame.time.get_ticks()
        self.aturdido = False
        self.update_time = pygame.time.get_ticks()
        self.running = False
        self.image = self.lista_animacion[self.action][self.frame_index]
        self.forma = pygame.Rect(x, y, cons.CHARACTER_WIDTH * size, cons.CHARACTER_HIGH * size)
        self.forma.center = (x, y)
        self.attack_cooldown = 1000
        self.path = []
        self.grif = None

    def setup_behavior_tree(self, player):
        root = Selector()

        follow_sequence = Sequence()
        follow_condition = Condition(lambda: self.distance_to(player) < cons.FOLLOW_RANGE)
        follow_action = Action(lambda: self.follow_player(player))
        follow_sequence.add_child(follow_condition)
        follow_sequence.add_child(follow_action)

        attack_sequence = Sequence()
        attack_condition = Condition(lambda: self.distance_to(player) < cons.ATTACK_RANGE)
        attack_action = Action(lambda: self.attack_player(player))
        attack_sequence.add_child(attack_condition)
        attack_sequence.add_child(attack_action)

        root.add_child(attack_sequence)
        root.add_child(follow_sequence)

        self.behavior_tree = root

    def line_of_sight(self, start, end, grid):
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if grid[int(y0)][int(x0)] == 1:  # Check for obstacles
                return False
            if (x0, y0) == (x1, y1):
                return True
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def distance_to(self, player):
        return math.sqrt((self.forma.centerx - player.forma.centerx) ** 2 + (self.forma.centery - player.forma.centery) ** 2)

    def follow_player(self, player):
        if not self.path:
            start = (self.forma.centerx // cons.TILE_SIZE, self.forma.centery // cons.TILE_SIZE)
            goal = (player.forma.centerx // cons.TILE_SIZE, player.forma.centery // cons.TILE_SIZE)
            self.path = a_star_search(start, goal, self.grid)

        if self.path:
            next_move = self.path.pop(0)
            delta_x = (next_move[0] * cons.TILE_SIZE) - self.forma.centerx
            delta_y = (next_move[1] * cons.TILE_SIZE) - self.forma.centery
            self.movement(delta_x, delta_y, self.obstacle_tile)
        return True


    def attack_player(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack > self.attack_cooldown:
            player.salud -= 10
            self.last_attack = current_time
        return True

    def inteligencia_artificial(self, player, obstacles_tiles, screen_scroll, fireball_image):
        self.obstacle_tile = obstacles_tiles
        self.grid = [[0 for _ in range(cons.GRID_WIDTH)] for _ in range(cons.GRID_HEIGHT)]

        for obstacle in obstacles_tiles:
            grid_x = int(obstacle[1].x // cons.TILE_SIZE)
            grid_y = int(obstacle[1].y // cons.TILE_SIZE)
            self.grid[grid_y][grid_x] = 1

        self.forma.x += screen_scroll[0]
        self.forma.y += screen_scroll[1]

        player_pos = (player.forma.x // cons.TILE_SIZE, player.forma.y // cons.TILE_SIZE)
        enemy_pos = (self.forma.x // cons.TILE_SIZE, self.forma.y // cons.TILE_SIZE)

        if self.behavior_tree is None:
            self.setup_behavior_tree(player)

        if self.alive and not self.aturdido:
            if self.line_of_sight(enemy_pos, player_pos, self.grid):
                self.behavior_tree.execute()

        return None

    def movement(self, delta_x, delta_y, obstacle_tiles, exit_tile=None):
        screen_scroll = [0, 0]
        self.running = False
        nivel_completado = False

        if delta_x != 0 or delta_y != 0:
            self.running = True

        if delta_x != 0 and delta_y != 0:
            delta_x = delta_x * (math.sqrt(2) / 2)
            delta_y = delta_y * (math.sqrt(2) / 2)

        if delta_x < 0:
            self.flip = True
        if delta_x > 0:
            self.flip = False

        self.forma.x += delta_x
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.forma):
                if delta_x > 0:
                    self.forma.right = obstacle[1].left
                if delta_x < 0:
                    self.forma.left = obstacle[1].right

        self.forma.y += delta_y
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.forma):
                if delta_y > 0:
                    self.forma.bottom = obstacle[1].top
                if delta_y < 0:
                    self.forma.top = obstacle[1].bottom

        if self.character_type == 0:
            if exit_tile and exit_tile[1].colliderect(self.forma):
                exit_dist = math.sqrt(((self.forma.centerx - exit_tile[1].centerx) ** 2) + ((self.forma.centery - exit_tile[1].centery) ** 2))
                if exit_dist < 20:
                    nivel_completado = True

            if self.forma.right > (cons.ANCHO_VENTANA - cons.SCROLL_THRESH):
                screen_scroll[0] = (cons.ANCHO_VENTANA - cons.SCROLL_THRESH) - self.forma.right
                self.forma.right = cons.ANCHO_VENTANA - cons.SCROLL_THRESH
            if self.forma.left < cons.SCROLL_THRESH:
                screen_scroll[0] = (cons.SCROLL_THRESH) - self.forma.left
                self.forma.left = cons.SCROLL_THRESH

            if self.forma.bottom > (cons.ALTO_VENTANA - cons.SCROLL_THRESH):
                screen_scroll[1] = (cons.ALTO_VENTANA - cons.SCROLL_THRESH) - self.forma.bottom
                self.forma.bottom = cons.ALTO_VENTANA - cons.SCROLL_THRESH
            if self.forma.top < cons.SCROLL_THRESH:
                screen_scroll[1] = (cons.SCROLL_THRESH) - self.forma.top
                self.forma.top = cons.SCROLL_THRESH

        return screen_scroll, nivel_completado

    def update_animation(self):
        if self.salud <= 0:
            self.salud = 0
            self.alive = False

        hit_cooldown = 1000
        if self.character_type == 0 and self.hit and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
            self.hit = False

        if self.running:
            self.update_action(1)
        else:
            self.update_action(0)

        cooldown_animacion = 125
        self.image = self.lista_animacion[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.lista_animacion[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, ventana):
        imagen_flip = pygame.transform.flip(self.image, self.flip, False)
        if self.character_type in [1, 2, 4, 6]:
            ventana.blit(imagen_flip, (self.forma.x, self.forma.y - cons.SCALE_CHARACTER * cons.OFFSET))
        else:
            ventana.blit(imagen_flip, (self.forma.x, self.forma.y))









            """Algoritmo Comportamiento"""
    #     self.character_type = character_type
    #     self.obstacle_tile = []
    #     self.boss = boss
    #     self.behavior_tree = None
    #     self.flip = False
    #     self.lista_animacion = animacion_mob[character_type]
    #     self.action = 0  # 0: animacion idle; 1: animacion run; 3: animacion ataque
    #     self.frame_index = 0
    #     self.salud = salud
    #     self.alive = True
    #     self.score = 0
    #     self.hit = False
    #     self.last_hit = pygame.time.get_ticks()
    #     self.last_attack = pygame.time.get_ticks()
    #     self.aturdido = False
    #     self.update_time = pygame.time.get_ticks()
    #     self.running = False
    #     self.image = self.lista_animacion[self.action][self.frame_index]
    #     self.forma = pygame.Rect(x, y, cons.CHARACTER_WIDTH * size, cons.CHARACTER_HIGH * size)
    #     self.forma.center = (x, y)
    #     self.attack_cooldown = 1000
    #
    # def setup_behavior_tree(self, player):
    #     root = Selector()
    #
    #     follow_sequence = Sequence()
    #     follow_condition = Condition(lambda: self.distance_to(player) < cons.FOLLOW_RANGE)
    #     follow_action = Action(lambda: self.follow_player(player))
    #     follow_sequence.add_child(follow_condition)
    #     follow_sequence.add_child(follow_action)
    #
    #     attack_sequence = Sequence()
    #     attack_condition = Condition(lambda: self.distance_to(player) < cons.ATTACK_RANGE)
    #     attack_action = Action(lambda: self.attack_player(player))
    #     attack_sequence.add_child(attack_condition)
    #     attack_sequence.add_child(attack_action)
    #
    #     root.add_child(attack_sequence)
    #     root.add_child(follow_sequence)
    #
    #     self.behavior_tree = root
    #
    # def distance_to(self, player):
    #     return math.sqrt((self.forma.centerx - player.forma.centerx) ** 2 + (self.forma.centery - player.forma.centery) ** 2)
    #
    # def follow_player(self, player):
    #     delta_x = 0
    #     delta_y = 0
    #
    #     if self.forma.centerx > player.forma.centerx:
    #         delta_x = -cons.ENEMY_SPEED
    #     elif self.forma.centerx < player.forma.centerx:
    #         delta_x = cons.ENEMY_SPEED
    #
    #     if self.forma.centery > player.forma.centery:
    #         delta_y = -cons.ENEMY_SPEED
    #     elif self.forma.centery < player.forma.centery:
    #         delta_y = cons.ENEMY_SPEED
    #
    #     self.movement(delta_x, delta_y, self.obstacle_tile)
    #     return True
    #
    # def attack_player(self, player):
    #     current_time = pygame.time.get_ticks()
    #     if current_time - self.last_attack > self.attack_cooldown:
    #         player.salud -= 10
    #         self.last_attack = current_time
    #     return True
    #
    # def inteligencia_artificial(self, player, obstacles_tiles, screen_scroll, fireball_image):
    #     self.obstacle_tile = obstacles_tiles
    #     self.forma.x += screen_scroll[0]
    #     self.forma.y += screen_scroll[1]
    #
    #     if self.behavior_tree is None:
    #         self.setup_behavior_tree(player)
    #
    #     if self.alive and not self.aturdido:
    #         self.behavior_tree.execute()
    #
    #     return None
    #
    # def movement(self, delta_x, delta_y, obstacle_tiles, exit_tile=None):
    #     screen_scroll = [0, 0]
    #     self.running = False
    #     nivel_completado = False
    #
    #     if delta_x != 0 or delta_y != 0:
    #         self.running = True
    #
    #     if delta_x != 0 and delta_y != 0:
    #         delta_x = delta_x * (math.sqrt(2) / 2)
    #         delta_y = delta_y * (math.sqrt(2) / 2)
    #
    #     if delta_x < 0:
    #         self.flip = True
    #     if delta_x > 0:
    #         self.flip = False
    #
    #     self.forma.x += delta_x
    #     for obstacle in obstacle_tiles:
    #         if obstacle[1].colliderect(self.forma):
    #             if delta_x > 0:
    #                 self.forma.right = obstacle[1].left
    #             if delta_x < 0:
    #                 self.forma.left = obstacle[1].right
    #
    #     self.forma.y += delta_y
    #     for obstacle in obstacle_tiles:
    #         if obstacle[1].colliderect(self.forma):
    #             if delta_y > 0:
    #                 self.forma.bottom = obstacle[1].top
    #             if delta_y < 0:
    #                 self.forma.top = obstacle[1].bottom
    #
    #     if self.character_type == 0:
    #         if exit_tile and exit_tile[1].colliderect(self.forma):
    #             exit_dist = math.sqrt(((self.forma.centerx - exit_tile[1].centerx) ** 2) + ((self.forma.centery - exit_tile[1].centery) ** 2))
    #             if exit_dist < 20:
    #                 nivel_completado = True
    #
    #         if self.forma.right > (cons.ANCHO_VENTANA - cons.SCROLL_THRESH):
    #             screen_scroll[0] = (cons.ANCHO_VENTANA - cons.SCROLL_THRESH) - self.forma.right
    #             self.forma.right = cons.ANCHO_VENTANA - cons.SCROLL_THRESH
    #         if self.forma.left < cons.SCROLL_THRESH:
    #             screen_scroll[0] = (cons.SCROLL_THRESH) - self.forma.left
    #             self.forma.left = cons.SCROLL_THRESH
    #
    #         if self.forma.bottom > (cons.ALTO_VENTANA - cons.SCROLL_THRESH):
    #             screen_scroll[1] = (cons.ALTO_VENTANA - cons.SCROLL_THRESH) - self.forma.bottom
    #             self.forma.bottom = cons.ALTO_VENTANA - cons.SCROLL_THRESH
    #         if self.forma.top < cons.SCROLL_THRESH:
    #             screen_scroll[1] = (cons.SCROLL_THRESH) - self.forma.top
    #             self.forma.top = cons.SCROLL_THRESH
    #
    #     return screen_scroll, nivel_completado
    #
    # def update_animation(self):
    #     if self.salud <= 0:
    #         self.salud = 0
    #         self.alive = False
    #
    #     hit_cooldown = 1000
    #     if self.character_type == 0 and self.hit and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
    #         self.hit = False
    #
    #     if self.running:
    #         self.update_action(1)
    #     else:
    #         self.update_action(0)
    #
    #     cooldown_animacion = 125
    #     self.image = self.lista_animacion[self.action][self.frame_index]
    #
    #     if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
    #         self.frame_index += 1
    #         self.update_time = pygame.time.get_ticks()
    #
    #     if self.frame_index >= len(self.lista_animacion[self.action]):
    #         self.frame_index = 0
    #
    # def update_action(self, new_action):
    #     if new_action != self.action:
    #         self.action = new_action
    #         self.frame_index = 0
    #         self.update_time = pygame.time.get_ticks()
    #
    # def draw(self, ventana):
    #     imagen_flip = pygame.transform.flip(self.image, self.flip, False)
    #     if self.character_type in [1, 2, 4, 6]:
    #         ventana.blit(imagen_flip, (self.forma.x, self.forma.y - cons.SCALE_CHARACTER * cons.OFFSET))
    #     else:
    #         ventana.blit(imagen_flip, (self.forma.x, self.forma.y))











    """ORIGINAL"""
    # def __init__(self, x, y,salud, animacion_mob, character_type,boss,size):
    #     self.character_type = character_type
    #     self.obstacle_tile = []
    #     self.boss = boss
    #     self.behavior = None
    #     self.flip = False
    #     self.lista_animacion = animacion_mob[character_type]
    #     self.action = 0 # 0: animacion idle; 1: animacion run; 3:animacion ataque
    #     #Imagen de la animacion
    #     self.frame_index = 0
    #     self.salud = salud
    #     self.alive = True
    #     self.score = 0
    #     self.hit = False
    #     self.last_hit = pygame.time.get_ticks()
    #     self.last_attack = pygame.time.get_ticks()
    #     self.aturdido = False
    #
    #
    #     #Tiempo actual desde que se inicia pygame en milisegundos
    #     self.update_time = pygame.time.get_ticks()
    #     self.running = False
    #     self.image = self.lista_animacion[self.action][self.frame_index]
    #     self.forma = pygame.Rect(x, y, cons.CHARACTER_WIDTH * size, cons.CHARACTER_HIGH * size)
    #     self.forma.center = (x,y)
    #
    #
    # # Implementar diferentes niveles de IA a los enemigos
    # def inteligencia_artificial(self,player,obstacles_tiles,screen_scroll,fireball_image):
    #     self.obstacle_tile = obstacles_tiles
    #     clipped_line = ()
    #     stun_cooldown = 100
    #     ia_dx = 0
    #     ia_dy = 0
    #     fireball = None
    #
    #
    #     #reposicionar basado en el desplazamiento de la ventana
    #     self.forma.x += screen_scroll[0]
    #     self.forma.y += screen_scroll[1]
    #
    #
    #     #Crear linea de vision
    #     line_sight = ((self.forma.centerx,self.forma.centery),  (player.forma.centerx, player.forma.centery))
    #     for obstacle in obstacles_tiles:
    #         if obstacle[1].clipline(line_sight):
    #             clipped_line = obstacle[1].clipline(line_sight)
    #
    #     #Verificar la distancia entre el enemigo y el jugador
    #     dist = math.sqrt(((self.forma.centerx - player.forma.centerx)**2) + ((self.forma.centery - player.forma.centery)**2))
    #
    #     if not clipped_line and dist > cons.RANGE:
    #         if self.forma.centerx > player.forma.centerx:
    #             ia_dx = -cons.ENEMY_SPEED
    #         if self.forma.centerx < player.forma.centerx:
    #             ia_dx = cons.ENEMY_SPEED
    #         if self.forma.centery > player.forma.centery:
    #             ia_dy = -cons.ENEMY_SPEED
    #         if self.forma.centerx < player.forma.centerx:
    #             ia_dy = cons.ENEMY_SPEED
    #
    #     if self.alive:
    #         if not self.aturdido:
    #             self.movement(ia_dx,ia_dy,obstacles_tiles)
    #             if dist < cons.ATTACK_RANGE and player.hit == False:
    #                 player.salud -= 10
    #                 player.hit = True
    #                 player.last_hit = pygame.time.get_ticks()
    #             #lanzamiento de bolas de fuego jefe final
    #             fireball_cooldown = 700
    #             if self.boss:
    #                 if dist < 500:
    #                     if pygame.time.get_ticks() - self.last_attack > fireball_cooldown:
    #                         fireball = Weapons.Fireball(fireball_image,self.forma.centerx,self.forma.centery, player.forma.centerx,player.forma.centery)
    #                         self.last_attack = pygame.time.get_ticks()
    #
    #         #Verificar si fue golpeado
    #         if self.hit == True:
    #             self.hit = False
    #             self.last_hit = pygame.time.get_ticks()
    #             self.aturdido = True
    #             self.running = False
    #             self.update_action(0)
    #
    #         if (pygame.time.get_ticks() - self.last_hit > stun_cooldown):
    #             self.aturdido = False
    #
    #
    #     return fireball
    #
    # def movement(self, delta_x, delta_y,obstacle_tiles,exit_tile=None):
    #     screen_scroll = [0, 0]
    #     self.running = False
    #     nivel_completado = False
    #
    #     key = pygame.key.get_pressed()
    #
    #
    #     if delta_x != 0 or delta_y != 0:
    #         self.running = True
    #
    #     #Emparejando la velocidad de los movimientos diagonales del jugador
    #     if delta_x != 0 and delta_y != 0:
    #         delta_x = delta_x * (math.sqrt(2)/2)
    #         delta_y = delta_y * (math.sqrt(2)/2)
    #
    #     #cambiar los sprites de direccion basado en el movimiento
    #     if delta_x < 0:
    #         self.flip = True
    #     if delta_x > 0:
    #         self.flip = False
    #
    #
    #     #Verificar por coliciones en el mapa
    #     self.forma.x = self.forma.x + delta_x
    #     for obstacle in obstacle_tiles:
    #         if obstacle[1].colliderect(self.forma):
    #             if delta_x > 0:
    #                 self.forma.right = obstacle[1].left
    #             if delta_x < 0:
    #                 self.forma.left = obstacle[1].right
    #
    #     self.forma.y = self.forma.y + delta_y
    #     for obstacle in obstacle_tiles:
    #         if obstacle[1].colliderect(self.forma):
    #             if delta_y > 0:
    #                 self.forma.bottom = obstacle[1].top
    #             if delta_y < 0:
    #                 self.forma.top = obstacle[1].bottom
    #     #camara solo aplica para el jugador
    #     if self.character_type == 0:
    #         #Verificar por colision entre el jugador y la salida
    #         if exit_tile[1].colliderect(self.forma):
    #             exit_dist = math.sqrt(((self.forma.centerx - exit_tile[1].centerx) ** 2) + ((self.forma.centery - exit_tile[1].centery) ** 2))
    #             if exit_dist < 20:
    #                 nivel_completado = True
    #
    #         #actualizar el scroll basado en la posicion del jugador
    #         # mover camara hacia izquierda y derecha
    #         if self.forma.right > (cons.ANCHO_VENTANA - cons.SCROLL_THRESH):
    #             screen_scroll[0] = (cons.ANCHO_VENTANA - cons.SCROLL_THRESH) - self.forma.right
    #             self.forma.right = cons.ANCHO_VENTANA - cons.SCROLL_THRESH
    #         if self.forma.left < cons.SCROLL_THRESH:
    #             screen_scroll[0] = (cons.SCROLL_THRESH) - self.forma.left
    #             self.forma.left = cons.SCROLL_THRESH
    #
    #         # mover camara hacia arriba y abajo
    #         if self.forma.bottom > (cons.ALTO_VENTANA - cons.SCROLL_THRESH):
    #             screen_scroll[1] = (cons.ALTO_VENTANA - cons.SCROLL_THRESH) - self.forma.bottom
    #             self.forma.bottom = cons.ALTO_VENTANA - cons.SCROLL_THRESH
    #         if self.forma.top < cons.SCROLL_THRESH:
    #             screen_scroll[1] = (cons.SCROLL_THRESH) - self.forma.top
    #             self.forma.top = cons.SCROLL_THRESH
    #     return screen_scroll, nivel_completado
    #
    # #Personaje Inactivo
    # def update_animation(self):
    #
    #     #Verificar si el enemigo ha muerto
    #     if self.salud <= 0:
    #         self.salud = 0
    #         self.alive = False
    #
    #     #
    #     hit_cooldown = 1000
    #     if self.character_type == 0:
    #         if self.hit == True and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
    #             self.hit = False
    #
    #     if self.running == True:
    #         self.update_action(1)
    #     else:
    #         self.update_action(0)
    #
    #     cooldown_animacion = 125
    #     self.image = self.lista_animacion[self.action][self.frame_index]
    #
    #     if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
    #         self.frame_index += 1
    #         self.update_time = pygame.time.get_ticks()
    #
    #     if self.frame_index >= len(self.lista_animacion[self.action]):
    #         self.frame_index = 0
    #
    # def update_action(self,new_action):
    #     if new_action != self.action:
    #         self.action = new_action
    #         self.frame_index = 0
    #         self.update_time = pygame.time.get_ticks()
    #
    #
    # def draw(self, ventana):
    #     imagen_flip = pygame.transform.flip(self.image, self.flip, False)
    #
    #     if self.character_type == 1 or self.character_type == 2 or self.character_type == 4 or self.character_type == 6:
    #         ventana.blit(imagen_flip, (self.forma.x, self.forma.y - cons.SCALE_CHARACTER * cons.OFFSET))
    #     else:
    #         ventana.blit(imagen_flip, (self.forma.x, self.forma.y))
    #
    #
