import pygame
from pygame import mixer
import constantes as cons
from character import Character
from Weapons import Weapons
from items import Item
from world import World
from Button import Button
import csv

#Inicialinzando la libreria pygame
mixer.init()
pygame.init()

#Creacion de la ventana principal
ventana = pygame.display.set_mode((cons.ANCHO_VENTANA, cons.ALTO_VENTANA))

font = pygame.font.Font("assets/fonts/SIXTY.TTF", 20)

#definir niveles del juego
level = 3
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0,0]

def escalar_imagen(imagen, escala):
    w = imagen.get_width()
    h = imagen.get_height()
    nueva_imagen = pygame.transform.scale(imagen,(w*escala,h*escala))
    return nueva_imagen

animation_types=['idle','run','attack']

pygame.mixer.music.load("assets/audio/MainTheme.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0, 9000)
shot_fx = pygame.mixer.Sound('assets/audio/arrow_shot.mp3')
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound('assets/audio/arrow_hit.wav')
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound('assets/audio/coin.wav')
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound('assets/audio/heal.wav')
heal_fx.set_volume(0.5)
#boss music
boss_fx = pygame.mixer.Sound('assets/audio/boss.ogg')
boss_fx.set_volume(0.5)

#Cargar imagenes de los personajes e items
animacion_mob = []
tipos_mob = ["soldado","demon","hechizero","swampy","orc","skeleton","FlyinDemon"]

corazon_lleno = escalar_imagen(pygame.image.load("assets/images/items/heart_full.png"),cons.ITEM_SCALE)
corazon_mitad = escalar_imagen(pygame.image.load("assets/images/items/heart_half.png"),cons.ITEM_SCALE)
corazon_vacio = escalar_imagen(pygame.image.load("assets/images/items/heart_empty.png"),cons.ITEM_SCALE)

#cargar imagenes del boton
menu_background = pygame.image.load("assets/images/menu_background_resized.jpg")
start_image= escalar_imagen(pygame.image.load("assets/images/buttons/button_start.png"),cons.BUTTON_SCALE)
exit_image= escalar_imagen(pygame.image.load("assets/images/buttons/button_exit.png"),cons.BUTTON_SCALE)
resume_image= escalar_imagen(pygame.image.load("assets/images/buttons/button_resume.png"),cons.BUTTON_SCALE)
restart_image= escalar_imagen(pygame.image.load("assets/images/buttons/button_restart.png"),cons.BUTTON_SCALE)


#cargar imagenes de los objetos
#Objeto Gema
lista_gema = []
for x in range(4):
    img = escalar_imagen(pygame.image.load(f"assets/images/items/gemas/{x}.png").convert_alpha(),cons.GEM_SCALE)
    lista_gema.append(img)

#Objeto pocion
lista_pocion = []
for x in range(8):
    img = escalar_imagen(pygame.image.load(f"assets/images/items/pocion/{x}.png").convert_alpha(),cons.POTION_SCALE)
    lista_pocion.append(img)

item_images=[]
item_images.append(lista_gema)
item_images.append(lista_pocion)

#Cargar imagenes de los objetos
imagen_arco =escalar_imagen(pygame.image.load("assets//images//weapons//arco.png"),cons.WEAPON_SCALE)
imagen_flecha =escalar_imagen(pygame.image.load("assets//images//weapons//arrow.png"),cons.ARROW_SCALE)
imagen_bolaFuego = escalar_imagen(pygame.image.load("assets//images//weapons//projectile.png"),cons.FIREBALL_SCALE)

#Animacion Ataque

for mob in tipos_mob:
    charater_animation = []
    for animation in animation_types:
        lista_temporal=[]
        for i in range(4):
            img = pygame.image.load(f"assets//images//characters//{mob}//{animation}//{i}.png").convert_alpha()
            img = escalar_imagen(img, cons.SCALE_CHARACTER)
            lista_temporal.append(img)
        charater_animation.append(lista_temporal)
    animacion_mob.append(charater_animation)

def dibujar_texto(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    ventana.blit(img, (x, y))

#Funcion para mostrar informacion del juego
def draw_info():
    pygame.draw.rect(ventana, cons.PANEL,(0, 0, cons.ANCHO_VENTANA,50))
    pygame.draw.line(ventana, cons.BLANCO,(0,50),(cons.ANCHO_VENTANA,50))


    mitad_corazon_dibujado = False
    #Dibujar Vidas
    for i in range(5):
        if player.salud >= ((i + 1) * 20):
            ventana.blit(corazon_lleno,(10 + i * 50, 0))
        elif (player.salud % 20 > 0) and mitad_corazon_dibujado == False:
            ventana.blit(corazon_mitad,(10 + i * 50, 0))
            mitad_corazon_dibujado = True
        else:
            ventana.blit(corazon_vacio,(10 + i * 50, 0))

    #mostrar Gemas colectadas
    dibujar_texto(f"x {player.score}", font, cons.BLANCO, cons.ANCHO_VENTANA - 100, 15)
    #Mostrar el nivel
    dibujar_texto(f"N I V E L :   {level}",font, cons.BLANCO, cons.ANCHO_VENTANA / 2, 15)

#Funcion para resetear el nivel
def reset_game():
    global level, player, world, enemy_list, damage_text_group, arrow_group, item_group, fireball_group

    # Resetear nivel
    level = 1
    
    # Limpiar todos los grupos de sprites
    damage_text_group.empty()
    arrow_group.empty()
    item_group.empty()
    fireball_group.empty()

    # Cargar datos del nivel 1
    world_data = []
    for row in range(cons.ROWS):
        rows = [-1] * cons.COLS
        world_data.append(rows)

    # Cargar el nivel desde el archivo CSV
    with open(f"levels/level{level}_data.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    # Crear nuevo mundo
    world = World()
    world.process_data(world_data, tile_list, item_images, animacion_mob)

    # Obtener el jugador y enemigos del nuevo mundo
    player = world.player
    enemy_list = world.character_list

    # Reiniciar música
    pygame.mixer.music.play(-1, 0.0, 9000)
    boss_fx.stop()

    # Recrear el item de score
    score_gem = Item(cons.ANCHO_VENTANA - 115, 23, 1, lista_gema, True)
    item_group.empty()
    item_group.add(score_gem)
    for item in world.item_list:
        item_group.add(item)

    return True


#Clase para el texto del daño
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.contador = 0

    def update(self):
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        #Mover numero de daño hacia arriba
        self.rect.y -= 1

        #Desvanecer texto
        self.contador += 1
        if self.contador > 30:
            self.kill()

class ScreenFade():
    def __init__(self,direction,color,speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:# 1: Desvanecido para cambio de nivel
            pygame.draw.rect(ventana, self.color, (0 - self.fade_counter, 0, cons.ANCHO_VENTANA // 2, cons.ALTO_VENTANA))
            pygame.draw.rect(ventana, self.color, (cons.ANCHO_VENTANA // 2 + self.fade_counter,0,cons.ANCHO_VENTANA,cons.ALTO_VENTANA))
            pygame.draw.rect(ventana, self.color, (0, 0 - self.fade_counter, cons.ANCHO_VENTANA, cons.ALTO_VENTANA // 2))
            pygame.draw.rect(ventana, self.color, (0, cons.ALTO_VENTANA // 2 + self.fade_counter, cons.ANCHO_VENTANA, cons.ALTO_VENTANA))

        elif self.direction == 2:# 2; Desvanecido para muerte del personaje
            pygame.draw.rect(ventana, self.color, (0,0, cons.ANCHO_VENTANA, 0 + self.fade_counter))


        if self.fade_counter >= cons.ANCHO_VENTANA:
            fade_complete = True

        return fade_complete

world_data=[]
for row in range(cons.ROWS):
    rows = [-1] * cons.COLS
    world_data.append(rows)

#Cargar los datos de los niveles a traves de los csv
with open(f"levels/level{level}_data.csv",newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

#Objeto Jugador
# player = Character(400, 300,10, animacion_mob,0,False)

#Objeto enemigo
enemigo = Character(100,300,100, animacion_mob,2,False,1)

#cargar las imagenes del mundo
tile_list=[]
for x in range(18):
    tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (cons.TILE_SIZE, cons.TILE_SIZE))
    tile_list.append(tile_image)

world = World()
world.process_data(world_data, tile_list,item_images,animacion_mob)


#Crear grupos de los sprites
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()


score_gem = Item(cons.ANCHO_VENTANA - 115,23,1, lista_gema,True)
item_group.add(score_gem)


#agregar los objeto de los datos del modulo WORLD
for item in world.item_list:
    item_group.add(item)

#Crear Jugador
player = world.player
#Crear enemigos extrayendo desde la clase world
enemy_list = world.character_list
#objeto Arma
arco = Weapons(imagen_arco,imagen_flecha)

#Nombre del juego
pygame.display.set_caption('Dungeon Escape')

#Variables para controlar el jugador
mover_arriba = False
mover_abajo = False
mover_derecha = False
mover_izquierda = False

#Crear suavizado de ventana
intro_fade = ScreenFade(1,cons.VERDE,4)
death_fade = ScreenFade(2,cons.ROSA,4)

#Dibujar botones
start_button = Button(cons.ANCHO_VENTANA // 2 - 145, cons.ALTO_VENTANA // 2 - 150, start_image)
exit_button = Button(cons.ANCHO_VENTANA // 2 - 110, cons.ALTO_VENTANA // 2 + 50, exit_image)
restart_button = Button(cons.ANCHO_VENTANA // 2 - 175, cons.ALTO_VENTANA // 2 - 50, restart_image)
resume_button = Button(cons.ANCHO_VENTANA // 2 - 175, cons.ALTO_VENTANA // 2 - 150, resume_image)

reloj = pygame.time.Clock()


#Main GameLoop

run = True
while run:
    events = pygame.event.get()

    reloj.tick(cons.FPS)


    if level == 3 and not boss_fx.get_num_channels():
        pygame.mixer.music.stop()
        boss_fx.play(-1)


    if start_game == False:
        ventana.blit(menu_background,(0,0))
        if start_button.draw(ventana):
            start_game = reset_game() 
            start_intro = True
        if exit_button.draw(ventana):
            run = False
    else:
        if pause_game == True:
            ventana.blit(menu_background,(0,0))
            if resume_button.draw(ventana):
                pause_game = False
            if exit_button.draw(ventana):
                run = False
        else:
            #color de fondo
            # ventana.fill(cons.BACKGROUND_COLOR)
            fondo = pygame.image.load("assets/images/background_dungeon.jpg").convert_alpha()
            ventana.blit(fondo, (0,0))

            if player.alive:
                #calcular el movimiento del jugador
                delta_x = 0
                delta_y = 0

                if mover_derecha == True:
                    delta_x = cons.CHARACTER_SPEED
                if mover_izquierda == True:
                    delta_x = -cons.CHARACTER_SPEED
                if mover_arriba == True:
                    delta_y = -cons.CHARACTER_SPEED
                if mover_abajo == True:
                    delta_y = cons.CHARACTER_SPEED

                #movimiento jugador
                screen_scroll, nivel_completado =player.movement(delta_x, delta_y,world.obstacle_tiles,world.exit_tiles)

                #Actualizacion de objetos
                player.update_animation()
                flecha = arco.update_weapon(player)
                world.update(screen_scroll)

                if flecha:
                    arrow_group.add(flecha)
                    shot_fx.play()
                for arrow in arrow_group:
                    damage,damage_pos = arrow.update(screen_scroll,world.obstacle_tiles,enemy_list)
                    if damage:
                        hit_fx.play()
                        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), cons.ROJO)
                        damage_text_group.add(damage_text)

                damage_text_group.update()
                arrow_group.update(screen_scroll, world.obstacle_tiles, enemy_list)
                item_group.update(screen_scroll,player,coin_fx,heal_fx)
                fireball_group.update(screen_scroll,player)


                #Actualizacion enemigo
                for enemigo in enemy_list:
                    fireball = enemigo.inteligencia_artificial(player,world.obstacle_tiles,screen_scroll,imagen_bolaFuego)
                    if fireball:
                        fireball_group.add(fireball)
                    

            #Dibujar personaje
            world.draw(ventana)
            player.draw(ventana)
            arco.draw(ventana)
            for arrow in arrow_group:
                arrow.draw(ventana)
            damage_text_group.draw(ventana)
            for fireball in fireball_group:
                fireball.draw(ventana)

            #dibujar enemigo
            for enemy in enemy_list:
                if enemy.alive:
                    enemy.draw(ventana)

            item_group.draw(ventana)
            draw_info()
            score_gem.draw(ventana)
            fireball_group.draw(ventana)

            #Verificar
            if nivel_completado == True:
                start_intro = True
                if level == 3:
                    start_game = False
                    boss_fx.stop()
                    pygame.mixer.music.play(-1, 0.0, 9000)
                else:
                    level +=1
                    world_data = []
                    for row in range(cons.ROWS):
                        rows = [-1] * cons.COLS
                        world_data.append(rows)
                    # Cargar los datos de los niveles a traves de los csv
                    with open(f"levels/level{level}_data.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    temp_hp = player.salud
                    temp_score = player.score

                    world = World()
                    world.process_data(world_data, tile_list, item_images, animacion_mob)
                    player = world.player
                    player.salud = temp_hp
                    player.score = temp_score
                    enemy_list = world.character_list
                    score_gem = Item(cons.ANCHO_VENTANA - 115, 23, 1, lista_gema, True)
                    item_group.add(score_gem)
                    

                    for item in world.item_list:
                        item_group.add(item)

            #Mostrar Intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            if player.alive == False:
                if death_fade.fade():
                    if restart_button.draw(ventana):
                        death_fade.fade_counter = 0
                        start_intro = True
                        world_data = reset_game()
                        # Cargar los datos de los niveles a traves de los csv
                        with open(f"levels/level{level}_data.csv", newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        temp_score = player.score

                        world = World()
                        world.process_data(world_data, tile_list, item_images, animacion_mob)
                        player = world.player
                        player.score = temp_score
                        enemy_list = world.character_list
                        score_gem = Item(cons.ANCHO_VENTANA - 115, 23, 1, lista_gema, True)
                        item_group.add(score_gem)

                        for item in world.item_list:
                            item_group.add(item)


    for event in events:
        if event.type == pygame.QUIT:
            run = False

        #Eventos cuando se presiona una tecla
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                mover_izquierda = True
            if event.key == pygame.K_d:
                mover_derecha = True
            if event.key == pygame.K_w:
                mover_arriba = True
            if event.key == pygame.K_s:
                mover_abajo = True
            if event.key == pygame.K_ESCAPE:
                pause_game = True


        #Evento cuando se suelta una tecla
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                mover_izquierda = False
            if event.key == pygame.K_d:
                mover_derecha = False
            if event.key == pygame.K_w:
                mover_arriba = False
            if event.key == pygame.K_s:
                mover_abajo = False

    pygame.display.update()

pygame.quit()

