import math
import random
import pygame
from arbolIA import Sequence, Selector, Action, Condition
import constantes as cons
from Weapons import  Fireball


class EnemyBehavior:
    def __init__(self, enemy, player):
        self.enemy = enemy
        self.player = player
        self.behavior_tree = self.create_behavior_tree()
        self.patrol_point = None
        self.last_position_change = pygame.time.get_ticks()
        self.dodge_direction = 1
        self.last_dodge = pygame.time.get_ticks()

    def create_behavior_tree(self):
        return Selector(children=[
            Sequence(children=[
                Condition(self.is_low_health),
                Selector(children=[
                    Sequence(children=[
                        Condition(self.is_player_attacking),
                        Action(self.dodge_attack)
                    ]),
                    Action(self.retreat)
                ])
            ]),
            Sequence(children=[
                Condition(self.is_in_attack_range),
                Selector(children=[
                    Sequence(children=[
                        Condition(self.has_attack_advantage),
                        Action(self.attack_player)
                    ]),
                    Action(self.strategic_reposition)
                ])
            ]),
            Sequence(children=[
                Condition(self.can_see_player),
                Selector(children=[
                    Sequence(children=[
                        Condition(self.is_player_vulnerable),
                        Action(self.aggressive_chase)
                    ]),
                    Action(self.tactical_chase)
                ])
            ]),
            Action(self.patrol_area)
        ])

    def update(self):
        return self.behavior_tree.run()

    def calculate_distance_to_player(self):
        return math.sqrt(
            ((self.enemy.forma.centerx - self.player.forma.centerx) ** 2) +
            ((self.enemy.forma.centery - self.player.forma.centery) ** 2)
        )

    def is_low_health(self):
        return self.enemy.salud < 90

    def is_player_attacking(self):
        return self.calculate_distance_to_player() < cons.ATTACK_RANGE * 1.5

    def dodge_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dodge > 1000:
            dx = cons.ENEMY_SPEED * 1.5 * self.dodge_direction
            self.enemy.movement(dx, 0, self.enemy.obstacle_tile)
            self.dodge_direction *= -1
            self.last_dodge = current_time
            return "success"
        return "running"

    def retreat(self):
        dx = cons.ENEMY_SPEED if self.enemy.forma.centerx < self.player.forma.centerx else -cons.ENEMY_SPEED
        dy = cons.ENEMY_SPEED if self.enemy.forma.centery < self.player.forma.centery else -cons.ENEMY_SPEED
        self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        return "running"

    def has_attack_advantage(self):
        return (self.player.hit or
                self.calculate_distance_to_player() < cons.ATTACK_RANGE * 0.7 or
                self.player.salud < 30)

    def strategic_reposition(self):
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle) * cons.ENEMY_SPEED
        dy = math.sin(angle) * cons.ENEMY_SPEED
        self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        return "running"

    def is_player_vulnerable(self):
        return self.player.hit or self.player.salud < 50

    def aggressive_chase(self):
        speed_multiplier = 1.3
        dx = dy = 0

        if self.enemy.forma.centerx > self.player.forma.centerx:
            dx = -cons.ENEMY_SPEED * speed_multiplier
        elif self.enemy.forma.centerx < self.player.forma.centerx:
            dx = cons.ENEMY_SPEED * speed_multiplier

        if self.enemy.forma.centery > self.player.forma.centery:
            dy = -cons.ENEMY_SPEED * speed_multiplier
        elif self.enemy.forma.centery < self.player.forma.centery:
            dy = cons.ENEMY_SPEED * speed_multiplier

        self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        return "running"

    def tactical_chase(self):
        dx = dy = 0

        if self.enemy.forma.centerx > self.player.forma.centerx:
            dx = -cons.ENEMY_SPEED
        elif self.enemy.forma.centerx < self.player.forma.centerx:
            dx = cons.ENEMY_SPEED

        if self.enemy.forma.centery > self.player.forma.centery:
            dy = -cons.ENEMY_SPEED
        elif self.enemy.forma.centery < self.player.forma.centery:
            dy = cons.ENEMY_SPEED

        if random.random() < 0.1:
            dx += random.uniform(-0.5, 0.5) * cons.ENEMY_SPEED
            dy += random.uniform(-0.5, 0.5) * cons.ENEMY_SPEED

        self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        return "running"

    def patrol_area(self):
        current_time = pygame.time.get_ticks()

        if self.patrol_point is None or current_time - self.last_position_change > 3000:
            self.patrol_point = (
                self.enemy.forma.centerx + random.randint(-200, 200),
                self.enemy.forma.centery + random.randint(-200, 200)
            )
            self.last_position_change = current_time

        dx = dy = 0
        if self.enemy.forma.centerx < self.patrol_point[0]:
            dx = cons.ENEMY_SPEED * 0.5
        elif self.enemy.forma.centerx > self.patrol_point[0]:
            dx = -cons.ENEMY_SPEED * 0.5

        if self.enemy.forma.centery < self.patrol_point[1]:
            dy = cons.ENEMY_SPEED * 0.5
        elif self.enemy.forma.centery > self.patrol_point[1]:
            dy = -cons.ENEMY_SPEED * 0.5

        self.enemy.movement(dx, dy, self.enemy.obstacle_tile)
        return "running"

    def is_in_attack_range(self):
        return self.calculate_distance_to_player() < cons.ATTACK_RANGE

    def can_see_player(self):
        return self.calculate_distance_to_player() < cons.RANGE and not self.enemy.aturdido

    def attack_player(self):
        if self.player.hit or not self.player.alive:
            return "failure"

        self.player.salud -= 10
        self.player.hit = True
        self.player.last_hit = pygame.time.get_ticks()
        return "success"

class BossBehavior(EnemyBehavior):
    def __init__(self, enemy, player, fireball_image):
        self.fireball_image = fireball_image
        self.attack_pattern = 0
        self.last_pattern_change = pygame.time.get_ticks()
        self.fireballs = pygame.sprite.Group()

        super().__init__(enemy, player)

    def create_behavior_tree(self):
        return Selector([
            Sequence([
                Condition(self.is_low_health),
                Action(self.rage_mode)
            ]),
            Sequence([
                Condition(self.can_shoot_fireball),
                Action(self.shoot_fireball_pattern)
            ]),
            super().create_behavior_tree()
        ])

    def can_shoot_fireball(self):
        fireball_cooldown = 700 if not self.is_low_health() else 500
        distance = self.calculate_distance_to_player()
        time_since_attack = pygame.time.get_ticks() - self.enemy.last_attack

        return (distance < 500 and
                time_since_attack > fireball_cooldown and
                not self.enemy.aturdido)

    def shoot_fireball_pattern(self):

        for angle in range(0, 360, 45):  # Shoot fireballs in 8 directions
            target_x = self.enemy.forma.centerx + math.cos(math.radians(angle)) * 100
            target_y = self.enemy.forma.centery + math.sin(math.radians(angle)) * 100
            fireball = Fireball(self.fireball_image, self.enemy.forma.centerx, self.enemy.forma.centery, target_x, target_y)
            self.fireballs.add(fireball)
        return "success"

    def _create_fireball(self, angle_offset):

        dx = self.player.forma.centerx - self.enemy.forma.centerx
        dy = self.player.forma.centery - self.enemy.forma.centery
        base_angle = math.atan2(dy, dx)

        final_angle = base_angle + math.radians(angle_offset)

        target_x = self.enemy.forma.centerx + math.cos(final_angle) * 500
        target_y = self.enemy.forma.centery + math.sin(final_angle) * 500

        fireball = Fireball(
            self.fireball_image,
            self.enemy.forma.centerx,
            self.enemy.forma.centery,
            target_x,
            target_y
        )

        self.enemy.last_attack = pygame.time.get_ticks()
        return fireball

    def update(self):
        self.fireballs.update((0,0),self.player)
        return self.behavior_tree.run()

    def draw(self, surface):
        self.fireballs.draw(surface)

    def rage_mode(self):
        if self.is_low_health():
            fireballs = self.shoot_fireball_pattern()
            self.aggressive_chase()
            return fireballs
        return "failure"