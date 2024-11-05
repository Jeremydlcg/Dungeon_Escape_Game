import math
import pygame
import constantes as cons
from Weapons import Fireball

class Node:
    def __init__(self, position, g_cost=0, h_cost=0, parent=None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent

class BehaviorNode:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Selector(BehaviorNode):
    def update(self):
        for child in self.children:
            result = child.update()
            if result is not None:
                return result
        return None

class Sequence(BehaviorNode):
    def update(self):
        for child in self.children:
            result = child.update()
            if result is None:
                return None
        return True

class Action(BehaviorNode):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def update(self):
        return self.action()

class EnemyBehavior:
    def __init__(self, enemy, player):
        self.enemy = enemy
        self.player = player
        # Inicializar variables para pathfinding
        self.path = None
        self.path_update_time = pygame.time.get_ticks()
        self.PATH_UPDATE_DELAY = 500
        self.GRID_SIZE = 40
        # Inicializar árbol de comportamiento
        self.setup_behavior_tree()

    def setup_behavior_tree(self):
        self.root = Selector()
        
        # Secuencia de ataque
        attack_sequence = Sequence()
        attack_sequence.add_child(Action(self.check_attack_range))
        attack_sequence.add_child(Action(self.attack_player))
        
        # Secuencia de persecución
        chase_sequence = Sequence()
        chase_sequence.add_child(Action(self.check_chase_range))
        chase_sequence.add_child(Action(self.chase_player))
        
        self.root.add_child(attack_sequence)
        self.root.add_child(chase_sequence)

    def update(self):
        return self.root.update()

    def check_attack_range(self):
        dist = self.get_distance_to_player()
        return True if dist < cons.ATTACK_RANGE else None

    def check_chase_range(self):
        dist = self.get_distance_to_player()
        return True if dist < cons.RANGE else None

    def attack_player(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy.last_attack > self.enemy.attack_cooldown:
            # Activar animación de ataque
            self.enemy.update_action(2)  # 2 es el índice para la animación de ataque
            self.player.salud -= 10
            self.player.hit = True
            self.player.last_hit = current_time
            self.enemy.last_attack = current_time
        return True

    def chase_player(self):
        dx = self.player.forma.centerx - self.enemy.forma.centerx
        dy = self.player.forma.centery - self.enemy.forma.centery
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx = (dx / dist) * cons.ENEMY_SPEED
            dy = (dy / dist) * cons.ENEMY_SPEED
            
            # Actualizar dirección del sprite
            self.enemy.flip = dx < 0
            # Activar animación de correr
            self.enemy.running = True
            
            if self.enemy.obstacle_tile:
                self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        else:
            self.enemy.running = False
        return True
    def get_distance_to_player(self):
        return math.sqrt((self.enemy.forma.centerx - self.player.forma.centerx) ** 2 + 
                        (self.enemy.forma.centery - self.player.forma.centery) ** 2)

    def find_path(self):
        # Si el jugador está muy cerca, no calcular camino
        if self.get_distance_to_player() < cons.ATTACK_RANGE * 2:
            return None

        # Simplificar la búsqueda usando una cuadrícula más grande
        GRID_SIZE = 40  # Aumentar el tamaño de la cuadrícula
        
        start = (self.enemy.forma.centerx // GRID_SIZE, 
                self.enemy.forma.centery // GRID_SIZE)
        end = (self.player.forma.centerx // GRID_SIZE, 
               self.player.forma.centery // GRID_SIZE)
        
        if start == end:
            return None

        open_list = []
        closed_set = set()  # Usar set para búsqueda más rápida
        
        start_node = Node(start)
        open_list.append(start_node)
        
        while open_list and len(open_list) < 100:  # Limitar la búsqueda
            current_node = min(open_list, key=lambda x: x.f_cost)
            
            if current_node.position == end:
                path = []
                while current_node:
                    path.append((current_node.position[0] * GRID_SIZE, 
                               current_node.position[1] * GRID_SIZE))
                    current_node = current_node.parent
                return path[::-1]
            
            open_list.remove(current_node)
            closed_set.add(current_node.position)
            
            # Reducir las direcciones de movimiento
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = (current_node.position[0] + dx, 
                          current_node.position[1] + dy)
                
                if new_pos in closed_set:
                    continue
                
                if not self.is_valid_grid_position(new_pos, GRID_SIZE):
                    continue
                
                new_node = Node(new_pos)
                new_node.g_cost = current_node.g_cost + 1
                new_node.h_cost = abs(end[0] - new_pos[0]) + abs(end[1] - new_pos[1])
                new_node.f_cost = new_node.g_cost + new_node.h_cost
                new_node.parent = current_node
                
                if new_node not in open_list:
                    open_list.append(new_node)
                
        return None

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def is_valid_grid_position(self, pos, grid_size):
        world_pos = (pos[0] * grid_size, pos[1] * grid_size)
        
        if not (0 <= world_pos[0] < cons.ANCHO_VENTANA and 
                0 <= world_pos[1] < cons.ALTO_VENTANA):
            return False
            
        test_rect = pygame.Rect(world_pos[0] - grid_size//2, 
                              world_pos[1] - grid_size//2, 
                              grid_size, grid_size)
        
        for obstacle in self.enemy.obstacle_tile:
            if obstacle[1].colliderect(test_rect):
                return False
        return True

class BossBehavior(EnemyBehavior):
    def __init__(self, enemy, player, fireball_image):
        super().__init__(enemy, player)
        self.fireball_image = fireball_image
        self.attack_cooldown = 2000  # Cooldown para ataques cuerpo a cuerpo
        self.fireball_cooldown = 1500  # Cooldown para bolas de fuego
        self.last_fireball = pygame.time.get_ticks()
        self.setup_behavior_tree()


    def setup_behavior_tree(self):
        self.root = Selector()
        
        # Secuencia de ataque a distancia
        ranged_attack = Sequence()
        ranged_attack.add_child(Action(self.check_fireball_range))
        ranged_attack.add_child(Action(self.shoot_fireball))
        
        # Secuencia de ataque cuerpo a cuerpo
        melee_attack = Sequence()
        melee_attack.add_child(Action(self.check_attack_range))
        melee_attack.add_child(Action(self.attack_player))
        
        # Secuencia de persecución
        chase_sequence = Sequence()
        chase_sequence.add_child(Action(self.check_chase_range))
        chase_sequence.add_child(Action(self.chase_player))
        
        self.root.add_child(ranged_attack)
        self.root.add_child(melee_attack)
        self.root.add_child(chase_sequence)

    def check_fireball_range(self):
        dist = self.get_distance_to_player()
        current_time = pygame.time.get_ticks()
        if dist < 400 and current_time - self.last_fireball >= self.fireball_cooldown:
            return True
        return None

    def shoot_fireball(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fireball >= self.fireball_cooldown:
            # Calcular posición inicial y objetivo
            start_x = self.enemy.forma.centerx
            start_y = self.enemy.forma.centery
            target_x = self.player.forma.centerx
            target_y = self.player.forma.centery
            
            # Crear bola de fuego
            fireball = Fireball(
                self.fireball_image,
                start_x,
                start_y,
                target_x,
                target_y
            )
            
            self.last_fireball = current_time
            self.enemy.update_action(2)  # Animación de ataque
            return fireball
        return None
    
    def attack_player(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy.last_attack > self.attack_cooldown:
            # Activar animación de ataque
            self.enemy.update_action(2)  # 2 es el índice para la animación de ataque
            self.player.salud -= 25
            self.player.hit = True
            self.player.last_hit = current_time
            self.enemy.last_attack = current_time
        return True

    def check_attack_range(self):
        dist = self.get_distance_to_player()
        return True if dist < 60 else None  # Rango de ataque cuerpo a cuerpo más grande

    def check_chase_range(self):
        dist = self.get_distance_to_player()
        return True if dist < 500 else None  # Rango de persecución más grande