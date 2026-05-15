import pygame, time
from random import randint
from files import dump_x_y, load_x_y, load_json, save_json, load_enemies, save_enemies, save_selected_class


size = {"width": 800, "height": 600}
x_y_file = 'data/x_y.txt'
x_y_fight_file = 'data/x_y_fight.txt'


menu_image_background = None
fight_image_background = None
bg_width = size["width"] * 2
bg_height = size["height"] * 2


bg_x = -(bg_width - size["width"]) // 2
bg_y = -(bg_height - size["height"]) // 2


FIGHT_BG_START_X = -200
FIGHT_BG_MIN_X = -800
FIGHT_BG_MAX_X = 0

BG_X_FIGHT = 0
BG_Y_FIGHT = -510


dump_x_y(bg_x, bg_y, x_y_file)
dump_x_y(BG_X_FIGHT, BG_Y_FIGHT, x_y_fight_file)


PLAYER = None
ENEMY = []
MOUSE_PRESSED = False
STAGE_PLAYER_LEVEL = 1
PAST_GAME_STATE_STATUS = ''
GAME_STAGE_STATUS = 'main_menu'
PREV_GAME_STAGE_STATUS = ''
PHASE_PLAYER_ANIMATION = 0
ANIMATION_DELAY = 500


LEVEL_CONFIG = {
    1: {"types": ["slime"], "count": (1, 3)},
    2: {"types": ["slime"], "count": (2, 4)},
    3: {"types": ["slime"], "count": (3, 5)},
}


ENEMY_SCREEN_X = 560
ENEMY_SPACING_X = 70
ENEMY_SCREEN_Y = 425
HIT_FLASH_DURATION = 0.3
DIED_SHOW_DURATION = 1.5


FIREBALL_SPEED = 6
FIREBALL_ANIM_DELAY = 80
FIREBALL_Y_OFFSET = -20


class GameWindow:
    def __init__(self):
        global menu_image_background, fight_image_background, PLAYER
        pygame.init()
        self.screen = pygame.display.set_mode((size["width"], size["height"]))

        pygame.display.set_icon(pygame.image.load('images/icon-main.png'))
        pygame.display.set_caption('Triple CodeMand')

        self.knight_animation_right = [
            pygame.image.load('images/characters/knight/knight_idle_right_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/knight/knight_idle_right_2_96.png').convert_alpha()
        ]
        self.knight_animation_left = [
            pygame.image.load('images/characters/knight/knight_idle_left_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/knight/knight_idle_left_2_96.png').convert_alpha()
        ]
        self.wizard_animation_right = [
            pygame.image.load('images/characters/wizard/wizard_idle_right_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/wizard/wizard_idle_right_2_96.png').convert_alpha()
        ]
        self.wizard_animation_left = [
            pygame.image.load('images/characters/wizard/wizard_idle_left_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/wizard/wizard_idle_left_2_96.png').convert_alpha()
        ]
        self.archer_animation_right = [
            pygame.image.load('images/characters/archer/archer_idle_right_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/archer/archer_idle_right_2_96.png').convert_alpha()
        ]
        self.archer_animation_left = [
            pygame.image.load('images/characters/archer/archer_idle_left_1_96.png').convert_alpha(),
            pygame.image.load('images/characters/archer/archer_idle_left_2_96.png').convert_alpha()
        ]
        self.slime_animation = [
            pygame.image.load('images/enemies/slime/slime_idle_1_96.png').convert_alpha(),
            pygame.image.load('images/enemies/slime/slime_idle_2_96.png').convert_alpha()
        ]
        self.slime_animation_damage = [
            pygame.image.load('images/enemies/slime/slime_damaged_1_96.png').convert_alpha(),
            pygame.image.load('images/enemies/slime/slime_damaged_2_96.png').convert_alpha()
        ]
        self.slime_animation_crit_damage = pygame.image.load('images/enemies/slime/slime_damaged_3_96.png').convert_alpha()
        self.slime_animation_died = pygame.image.load('images/enemies/slime/slime_died_96.png').convert_alpha()

        self.fireball_wizard_animation = [
            pygame.image.load('images/attacks/fireball_1.png').convert_alpha(),
            pygame.image.load('images/attacks/fireball_2.png').convert_alpha()
        ]

        self.font_bold_80 = pygame.font.Font('fonts/Nunito-Bold.ttf', 80)
        self.font_bold_60 = pygame.font.Font('fonts/Nunito-Bold.ttf', 60)
        self.font_bold_40 = pygame.font.Font('fonts/Nunito-Bold.ttf', 40)

        menu_image_background = pygame.transform.scale(pygame.image.load('images/background_menu.png').convert_alpha(), (512, 512))
        fight_image_background = pygame.image.load('images/image_background_forest_1600_600.jpg').convert()

        sound_background = pygame.mixer.Sound('sounds/background_sound.mp3')
        sound_background.set_volume(0.24)
        sound_background.play(loops=-1)

        PLAYER = self.knight_animation_right


class FireballProjectile:
    def __init__(self, start_x, start_y, target_screen_x, target_screen_y,
                 enemy_index, damage, is_crit, sprites):
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = float(target_screen_x)
        self.target_y = float(target_screen_y)
        self.enemy_index = enemy_index
        self.damage = damage
        self.is_crit = is_crit
        self.sprites = sprites
        self.anim_phase = 0
        self.last_anim_tick = pygame.time.get_ticks()
        self.hit = False

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        self.vx = dx / dist * FIREBALL_SPEED
        self.vy = dy / dist * FIREBALL_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy

        now = pygame.time.get_ticks()
        if now - self.last_anim_tick >= FIREBALL_ANIM_DELAY:
            self.anim_phase = (self.anim_phase + 1) % len(self.sprites)
            self.last_anim_tick = now

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        return dist < FIREBALL_SPEED * 1.5

    def draw(self, screen):
        sprite = self.sprites[self.anim_phase]
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, rect)

    def apply_damage(self):
        enemies = load_enemies()
        if self.enemy_index >= len(enemies):
            return
        enemy = enemies[self.enemy_index]
        if not enemy["alive"]:
            return

        if enemy["armor"] > 0:
            remaining = enemy["armor"] - self.damage
            if remaining < 0:
                enemy["armor"] = 0
                enemy["health"] += remaining
            else:
                enemy["armor"] = remaining
        else:
            enemy["health"] -= self.damage

        enemy["hit_at"] = time.time()

        if enemy["health"] <= 0:
            enemy["health"] = 0
            enemy["alive"] = False
            enemy["hit_type"] = "died"
        elif self.is_crit:
            enemy["hit_type"] = "crit"
        else:
            enemy["hit_type"] = "normal"

        enemies[self.enemy_index] = enemy
        save_enemies(enemies)
        self.hit = True


def generate_level_enemies(level):
    config = LEVEL_CONFIG.get(level, LEVEL_CONFIG[1])
    count = randint(*config["count"])
    enemies = []
    for i in range(count):
        enemy_type = config["types"][0]
        if enemy_type == "slime":
            world_x = (ENEMY_SCREEN_X - FIGHT_BG_START_X) + i * ENEMY_SPACING_X
            enemies.append({
                "type": "slime",
                "category": "Slime",
                "category_up": "Wizard",
                "health": 40,
                "max_health": 40,
                "armor": 0,
                "alive": True,
                "hit_at": 0.0,
                "hit_type": "none",
                "world_x": world_x
            })
    save_enemies(enemies)
    print(f"Уровень {level}: создано {count} врагов")


def get_slime_sprite(enemy, window, anim_phase):
    now = time.time()
    hit_age = now - enemy["hit_at"]
    hit_type = enemy.get("hit_type", "none")

    if hit_type == "died" and hit_age < DIED_SHOW_DURATION:
        return window.slime_animation_died

    if hit_type in ("crit", "normal") and hit_age < HIT_FLASH_DURATION:
        if hit_type == "crit":
            return window.slime_animation_crit_damage
        else:
            return window.slime_animation_damage[anim_phase]

    if not enemy["alive"]:
        return window.slime_animation_died

    return window.slime_animation[anim_phase]


def render_enemies(screen, window, anim_phase):
    enemies = load_enemies()
    for i, enemy in enumerate(enemies):
        ex = enemy.get("world_x", ENEMY_SCREEN_X + i * ENEMY_SPACING_X) + BG_X_FIGHT
        ey = ENEMY_SCREEN_Y
        sprite = get_slime_sprite(enemy, window, anim_phase)
        screen.blit(sprite, (ex, ey))


def player_animation(last_animation_tick):
    global PHASE_PLAYER_ANIMATION
    now_ticks = pygame.time.get_ticks()
    if now_ticks - last_animation_tick >= ANIMATION_DELAY:
        if PHASE_PLAYER_ANIMATION == 1:
            PHASE_PLAYER_ANIMATION = 0
        else:
            PHASE_PLAYER_ANIMATION += 1
        last_animation_tick = now_ticks
    return last_animation_tick


def check_animation(window):
    global PLAYER
    data = load_json()

    if data.get("animation_side", "right") == "left":
        if PLAYER == window.knight_animation_right:
            PLAYER = window.knight_animation_left
        elif PLAYER == window.archer_animation_right:
            PLAYER = window.archer_animation_left
        elif PLAYER == window.wizard_animation_right:
            PLAYER = window.wizard_animation_left
    elif  data.get("animation_side", "right") == "right":
        if PLAYER == window.knight_animation_left:
            PLAYER = window.knight_animation_right
        elif PLAYER == window.archer_animation_left:
            PLAYER = window.archer_animation_right
        elif PLAYER == window.wizard_animation_left:
            PLAYER = window.wizard_animation_right

    return PLAYER


def change_x_y(file):
    global bg_x, bg_y
    bg_x, bg_y = load_x_y(file)

    bg_x = max(-(bg_width - size["width"]), min(0, bg_x))
    bg_y = max(-(bg_height - size["height"]), min(0, bg_y))

    dump_x_y(bg_x, bg_y, file)


def change_x_y_fight(file):
    global BG_X_FIGHT, BG_Y_FIGHT
    BG_X_FIGHT, BG_Y_FIGHT = load_x_y(file)

    BG_X_FIGHT = max(FIGHT_BG_MIN_X, min(FIGHT_BG_MAX_X, BG_X_FIGHT))
    BG_Y_FIGHT = BG_Y_FIGHT

    dump_x_y(BG_X_FIGHT, BG_Y_FIGHT, file)


def main_menu(screen, fonts):
    global GAME_STAGE_STATUS, MOUSE_PRESSED
    screen.blit(menu_image_background, (-((512 - 800) // 2), -((512 - 600) // 2)))

    text_surface = fonts[0].render('Triple CodeMand', True, (42, 42, 42))
    text_surface_2 = fonts[1].render('играть', True, (255, 255, 255))

    text_surface_rect = text_surface.get_rect(topleft=((size["width"] - text_surface.get_width()) / 2, 110))
    text_surface_2_rect = text_surface_2.get_rect(topleft=((size["width"] - text_surface_2.get_width()) / 2, 350))

    screen.blit(text_surface, text_surface_rect)
    screen.blit(text_surface_2, text_surface_2_rect)

    mouse = pygame.mouse
    if text_surface_2_rect.collidepoint(mouse.get_pos()):
        text_surface_2 = fonts[1].render('играть', True, (230, 230, 230))
        screen.blit(text_surface_2, text_surface_2_rect)
        if mouse.get_pressed()[0]:
            MOUSE_PRESSED = True
            GAME_STAGE_STATUS = 'choose_character'
    else:
        text_surface_2 = fonts[1].render('играть', True, (255, 255, 255))
        screen.blit(text_surface_2, text_surface_2_rect)


def choose_character(window, screen, fonts):
    global GAME_STAGE_STATUS, PLAYER, MOUSE_PRESSED
    screen.blit(menu_image_background, (-((512 - 800) // 2), -((512 - 600) // 2)))

    text_surface = fonts[0].render('персонаж', True, (42, 42, 42))
    text_surface_2 = fonts[1].render('рыцарь', True, (255, 255, 255))
    text_surface_3 = fonts[1].render('лучник', True, (255, 255, 255))
    text_surface_4 = fonts[1].render('маг', True, (255, 255, 255))

    text_surface_rect = text_surface.get_rect(topleft=((size["width"] - text_surface.get_width()) / 2, 110))
    text_surface_2_rect = text_surface_2.get_rect(topleft=((size["width"] - text_surface_2.get_width()) / 2, 250))
    text_surface_3_rect = text_surface_3.get_rect(topleft=((size["width"] - text_surface_3.get_width()) / 2, 340))
    text_surface_4_rect = text_surface_4.get_rect(topleft=((size["width"] - text_surface_4.get_width()) / 2, 420))

    screen.blit(text_surface, text_surface_rect)
    screen.blit(text_surface_2, text_surface_2_rect)
    screen.blit(text_surface_3, text_surface_3_rect)
    screen.blit(text_surface_4, text_surface_4_rect)

    mouse = pygame.mouse
    if text_surface_2_rect.collidepoint(mouse.get_pos()):
        text_surface_2 = fonts[1].render('рыцарь', True, (230, 230, 230))
        screen.blit(text_surface_2, text_surface_2_rect)
        if mouse.get_pressed()[0] and MOUSE_PRESSED == False:
            PLAYER = window.knight_animation_right
            save_selected_class("Warrior")
            GAME_STAGE_STATUS = 'fight'
        else:
            MOUSE_PRESSED = False
    elif text_surface_3_rect.collidepoint(mouse.get_pos()):
        text_surface_3 = fonts[1].render('лучник', True, (230, 230, 230))
        screen.blit(text_surface_3, text_surface_3_rect)
        if mouse.get_pressed()[0] and MOUSE_PRESSED == False:
            PLAYER = window.archer_animation_right
            save_selected_class("Archer")
            GAME_STAGE_STATUS = 'fight'
        else:
            MOUSE_PRESSED = False
    elif text_surface_4_rect.collidepoint(mouse.get_pos()):
        text_surface_4 = fonts[1].render('маг', True, (230, 230, 230))
        screen.blit(text_surface_4, text_surface_4_rect)
        if mouse.get_pressed()[0] and MOUSE_PRESSED == False:
            PLAYER = window.wizard_animation_right
            save_selected_class("Wizard")
            GAME_STAGE_STATUS = 'fight'
        else:
            MOUSE_PRESSED = False
    else:
        text_surface_2 = fonts[1].render('рыцарь', True, (255, 255, 255))
        text_surface_3 = fonts[1].render('лучник', True, (255, 255, 255))
        text_surface_4 = fonts[1].render('маг', True, (255, 255, 255))

        screen.blit(text_surface_2, text_surface_2_rect)
        screen.blit(text_surface_3, text_surface_3_rect)
        screen.blit(text_surface_4, text_surface_4_rect)


def pause_menu(screen, font):
    text_surface = font.render('пауза', True, (255, 255, 255))

    screen.fill((100, 100, 100))
    screen.blit(text_surface, ((size["width"] - text_surface.get_width()) / 2, 150))


def check_fireball_launch(window, fireballs, player_screen_x, player_screen_y):
    data = load_json()
    launch = data.get("fireball_launch")
    if not launch:
        return

    enemies = load_enemies()
    idx = launch["enemy_index"]
    if idx >= len(enemies) or not enemies[idx]["alive"]:
        data.pop("fireball_launch", None)
        save_json(data)
        return

    enemy = enemies[idx]

    fight_x, _ = load_x_y(x_y_fight_file)

    ex = enemy.get(
        "world_x",
        ENEMY_SCREEN_X + idx * ENEMY_SPACING_X
    ) + fight_x + 48
    ey = ENEMY_SCREEN_Y + 48

    sx = player_screen_x + 48
    sy = player_screen_y + 48 + FIREBALL_Y_OFFSET

    fb = FireballProjectile(
        start_x=sx, start_y=sy,
        target_screen_x=ex, target_screen_y=ey,
        enemy_index=idx,
        damage=launch["damage"],
        is_crit=launch["is_crit"],
        sprites=window.fireball_wizard_animation
    )
    fireballs.append(fb)

    data.pop("fireball_launch", None)
    save_json(data)


def update_fireballs(screen, fireballs):
    for fb in fireballs[:]:
        reached = fb.update()
        fb.draw(screen)
        if reached:
            fb.apply_damage()
            fireballs.remove(fb)



def pygame_init():
    global GAME_STAGE_STATUS, PAST_GAME_STATE_STATUS, PHASE_PLAYER_ANIMATION, PLAYER, PREV_GAME_STAGE_STATUS
    window = GameWindow()
    game_screen = window.screen

    clock = pygame.time.Clock()
    last_animation_tick = pygame.time.get_ticks()
    running = True

    square_player = pygame.surface.Surface((64, 64))

    background = pygame.transform.scale(fight_image_background, (bg_width, bg_height))

    player_screen_x = 100
    player_screen_y = 420

    fireballs = []

    while running:
        pygame.display.update()

        if GAME_STAGE_STATUS == 'fight' and PREV_GAME_STAGE_STATUS != 'fight':
            generate_level_enemies(STAGE_PLAYER_LEVEL)
            dump_x_y(FIGHT_BG_START_X, BG_Y_FIGHT, x_y_fight_file)
            fireballs.clear()
        PREV_GAME_STAGE_STATUS = GAME_STAGE_STATUS

        if GAME_STAGE_STATUS == 'main_menu':
            main_menu(game_screen, [window.font_bold_80, window.font_bold_60])
        elif GAME_STAGE_STATUS == 'choose_character':
            choose_character(window, game_screen, [window.font_bold_60, window.font_bold_40])
        elif GAME_STAGE_STATUS == 'pause_menu':
            pause_menu(game_screen, window.font_bold_60)
        elif GAME_STAGE_STATUS == 'gameplay':
            last_animation_tick = player_animation(last_animation_tick)

            game_screen.blit(background, (bg_x, bg_y))
            game_screen.blit(PLAYER[PHASE_PLAYER_ANIMATION], ((size["width"] - square_player.get_width()) / 2, (size["height"] - square_player.get_height()) / 2))

            change_x_y(x_y_file)
        elif GAME_STAGE_STATUS == 'fight':
            PLAYER = check_animation(window)
            last_animation_tick = player_animation(last_animation_tick)

            change_x_y_fight(x_y_fight_file)
            game_screen.blit(background, (BG_X_FIGHT, BG_Y_FIGHT))

            check_fireball_launch(window, fireballs, player_screen_x, player_screen_y)
            update_fireballs(game_screen, fireballs)

            render_enemies(game_screen, window, PHASE_PLAYER_ANIMATION)
            game_screen.blit(PLAYER[PHASE_PLAYER_ANIMATION],(player_screen_x, player_screen_y))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if GAME_STAGE_STATUS == 'pause_menu':
                        GAME_STAGE_STATUS = PAST_GAME_STATE_STATUS
                        PAST_GAME_STATE_STATUS = 'pause_menu'
                    else:
                        PAST_GAME_STATE_STATUS = GAME_STAGE_STATUS
                        GAME_STAGE_STATUS = 'pause_menu'


        # pygame.display.flip()

        clock.tick(60)

    pygame.quit()