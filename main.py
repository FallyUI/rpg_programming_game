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
BACKGROUND_STARS = [(randint(0, size["width"]), randint(0, size["height"])) for _ in range(80)]


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
PLAYER_MAX_HP = int
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


ENEMY_MELEE_RANGE = 200
ENEMY_ATTACK_CD = 5.0
ENEMY_BASE_DAMAGE = 5


ENEMY_FIREBALL_SPEED = 5
ENEMY_FIREBALL_CD = 5.0
ENEMY_FIREBALL_RANGE = 600
ENEMY_FIREBALL_DAMAGE = 5

enemy_fireballs = []
enemy_fireball_timers = {}


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


        self.slimy_enemy_animation = [
            pygame.image.load('images/attacks/fireball_reverse_1.png').convert_alpha(),
            pygame.image.load('images/attacks/fireball_reverse_2.png').convert_alpha()
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


class EnemyFireball:
    def __init__(self, start_x, start_y, target_x, target_y, damage, sprites):
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.damage = damage
        self.sprites = sprites
        self.anim_phase = 0
        self.last_anim_tick = pygame.time.get_ticks()

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        self.vx = dx / dist * ENEMY_FIREBALL_SPEED
        self.vy = dy / dist * ENEMY_FIREBALL_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy
        now = pygame.time.get_ticks()
        if now - self.last_anim_tick >= FIREBALL_ANIM_DELAY:
            self.anim_phase = (self.anim_phase + 1) % len(self.sprites)
            self.last_anim_tick = now
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        return (dx ** 2 + dy ** 2) ** 0.5 < ENEMY_FIREBALL_SPEED * 1.5

    def draw(self, screen):
        sprite = self.sprites[self.anim_phase]
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, rect)


def update_enemy_fireballs(screen, window, player_screen_x, player_screen_y, player_hp):
    global enemy_fireballs

    for fb in enemy_fireballs[:]:
        reached = fb.update()
        fb.draw(screen)
        if reached:
            player_hp -= fb.damage
            player_hp = max(0, player_hp)
            print(f"Вражеский фаербол попал! -{fb.damage} hp → осталось: {player_hp}")
            enemy_fireballs.remove(fb)

    return player_hp


def maybe_launch_enemy_fireballs(window, player_screen_x, player_screen_y):
    global enemy_fireballs, enemy_fireball_timers
    now = time.time()
    enemies = load_enemies()
    player_cx = player_screen_x + 48
    player_cy = player_screen_y + 48

    for i, enemy in enumerate(enemies):
        if not enemy["alive"]:
            continue

        ex = enemy.get("world_x", ENEMY_SCREEN_X + i * ENEMY_SPACING_X) + BG_X_FIGHT + 48
        ey = ENEMY_SCREEN_Y + 48
        dist = abs(ex - player_cx)

        if dist <= ENEMY_FIREBALL_RANGE:
            last_shot = enemy_fireball_timers.get(i, 0.0)
            if now - last_shot >= ENEMY_FIREBALL_CD:
                enemy_fireball_timers[i] = now
                fb = EnemyFireball(
                    start_x=ex, start_y=ey,
                    target_x=player_cx, target_y=player_cy,
                    damage=ENEMY_FIREBALL_DAMAGE,
                    sprites=window.slimy_enemy_animation
                )
                enemy_fireballs.append(fb)
                print(f"Враг #{i} запускает фаербол в игрока!")


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
    screen.fill((0, 0, 0))
    screen.blit(menu_image_background, (-((512 - 800) // 2), -((512 - 600) // 2)))

    text_surface = fonts[0].render('Triple', True, (42, 42, 42))
    text_surface_2 = fonts[0].render('CodeMand', True, (42, 42, 42))
    text_surface_3 = fonts[1].render('играть', True, (255, 255, 255))

    text_surface_rect = text_surface.get_rect(topleft=((size["width"] - text_surface.get_width()) / 2, 110))
    text_surface_2_rect = text_surface_2.get_rect(topleft=((size["width"] - text_surface_2.get_width()) / 2, 190))
    text_surface_3_rect = text_surface_3.get_rect(topleft=((size["width"] - text_surface_3.get_width()) / 2, 350))

    screen.blit(text_surface, text_surface_rect)
    screen.blit(text_surface_2, text_surface_2_rect)
    screen.blit(text_surface_3, text_surface_3_rect)

    mouse = pygame.mouse
    if text_surface_3_rect.collidepoint(mouse.get_pos()):
        text_surface_3 = fonts[1].render('играть', True, (230, 230, 230))
        screen.blit(text_surface_3, text_surface_3_rect)
        if mouse.get_pressed()[0]:
            MOUSE_PRESSED = True
            GAME_STAGE_STATUS = 'choose_character'
    else:
        text_surface_3 = fonts[1].render('играть', True, (255, 255, 255))
        screen.blit(text_surface_3, text_surface_3_rect)


def choose_character(window, screen, fonts):
    global GAME_STAGE_STATUS, PLAYER, MOUSE_PRESSED, PLAYER_MAX_HP
    screen.fill((0, 0, 0))
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
            PLAYER_MAX_HP = 150
            save_selected_class("Warrior")
            GAME_STAGE_STATUS = 'fight'
        else:
            MOUSE_PRESSED = False
    elif text_surface_3_rect.collidepoint(mouse.get_pos()):
        text_surface_3 = fonts[1].render('лучник', True, (230, 230, 230))
        screen.blit(text_surface_3, text_surface_3_rect)
        if mouse.get_pressed()[0] and MOUSE_PRESSED == False:
            PLAYER = window.archer_animation_right
            PLAYER_MAX_HP = 100
            save_selected_class("Archer")
            GAME_STAGE_STATUS = 'fight'
        else:
            MOUSE_PRESSED = False
    elif text_surface_4_rect.collidepoint(mouse.get_pos()):
        text_surface_4 = fonts[1].render('маг', True, (230, 230, 230))
        screen.blit(text_surface_4, text_surface_4_rect)
        if mouse.get_pressed()[0] and MOUSE_PRESSED == False:
            PLAYER = window.wizard_animation_right
            PLAYER_MAX_HP = 80
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


def pause_menu(screen, font, frozen_frame):
    if frozen_frame is not None:
        screen.blit(frozen_frame, (0, 0))

    overlay = pygame.Surface((size["width"], size["height"]), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    text_surface = font.render('пауза', True, (255, 255, 255))
    screen.blit(text_surface, ((size["width"] - text_surface.get_width()) / 2, 220))


def victory_screen(screen, fonts, mouse_pressed_ref):
    global GAME_STAGE_STATUS
    screen.fill((20, 20, 40))

    for star in BACKGROUND_STARS:
        pygame.draw.circle(screen, (200, 200, 255), star, 1)
    screen.blit(menu_image_background, (-((512 - 800) // 2), -((512 - 600) // 2)))

    title = fonts[0].render('Победа!', True, (255, 185, 0))
    subtitle = fonts[1].render('все враги', True, (240, 240, 255))
    subtitle_2 = fonts[1].render('повержены', True, (240, 240, 255))
    btn = fonts[1].render('в меню', True, (255, 255, 255))

    title_rect = title.get_rect(center=(size["width"] // 2, 190))
    subtitle_rect = subtitle.get_rect(center=(size["width"] // 2, 290))
    subtitle_2_rect = subtitle_2.get_rect(center=(size["width"] // 2, 340))
    btn_rect = btn.get_rect(center=(size["width"] // 2, 420))

    screen.blit(title, title_rect)
    screen.blit(subtitle, subtitle_rect)
    screen.blit(subtitle_2, subtitle_2_rect)

    mouse = pygame.mouse
    if btn_rect.collidepoint(mouse.get_pos()):
        btn = fonts[1].render('в меню', True, (230, 230, 230))
        if mouse.get_pressed()[0] and not mouse_pressed_ref:
            mouse_pressed_ref = True
            GAME_STAGE_STATUS = 'main_menu'
    else:
        mouse_pressed_ref = False

    screen.blit(btn, btn_rect)
    return mouse_pressed_ref


def defeat_screen(screen, fonts, mouse_pressed_ref):
    global GAME_STAGE_STATUS
    screen.fill((15, 5, 5))

    for star in BACKGROUND_STARS:
        pygame.draw.circle(screen, (180, 40, 40), star, 1)
    screen.blit(menu_image_background, (-((512 - 800) // 2), -((512 - 600) // 2)))

    title = fonts[0].render('Поражение', True, (200, 30, 30))
    subtitle = fonts[1].render('вы пали в бою', True, (180, 100, 100))
    btn = fonts[1].render('в меню', True, (255, 255, 255))

    title_rect = title.get_rect(center=(size["width"] // 2, 180))
    subtitle_rect = subtitle.get_rect(center=(size["width"] // 2, 275))
    btn_rect = btn.get_rect(center=(size["width"] // 2, 390))

    screen.blit(title, title_rect)
    screen.blit(subtitle, subtitle_rect)

    mouse = pygame.mouse
    if btn_rect.collidepoint(mouse.get_pos()):
        btn = fonts[1].render('в меню', True, (230, 230, 230))
        if mouse.get_pressed()[0] and not mouse_pressed_ref:
            mouse_pressed_ref = True
            GAME_STAGE_STATUS = 'main_menu'
    else:
        mouse_pressed_ref = False

    screen.blit(btn, btn_rect)
    return mouse_pressed_ref


def check_enemy_attacks_player(player_screen_x, player_hp):
    now = time.time()
    enemies = load_enemies()
    changed = False

    player_cx = player_screen_x + 48

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        idx = enemies.index(enemy)
        ex = enemy.get("world_x", ENEMY_SCREEN_X + idx * ENEMY_SPACING_X) + BG_X_FIGHT + 48
        dist = abs(ex - player_cx)

        if dist <= ENEMY_MELEE_RANGE:
            last_atk = enemy.get("last_attack_at", 0.0)
            if now - last_atk >= ENEMY_ATTACK_CD:
                dmg = enemy.get("damage", ENEMY_BASE_DAMAGE)
                player_hp -= dmg
                enemy["last_attack_at"] = now
                changed = True
                print(f"Враг атакует игрока! -{dmg} hp → осталось: {player_hp}")

    if changed:
        save_enemies(enemies)

    return player_hp


def draw_player_hp(screen, current_hp, max_hp):
    bar_w, bar_h = 200, 18
    x, y = 16, 16
    ratio = max(0.0, current_hp / max_hp)

    pygame.draw.rect(screen, (80, 0, 0), (x, y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(screen, (200, 30, 30), (x, y, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_w, bar_h), 2, border_radius=4)


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
    ex = enemy.get("world_x", ENEMY_SCREEN_X + idx * ENEMY_SPACING_X) + fight_x + 48
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


def check_victory():
    enemies = load_enemies()
    if not enemies:
        return False
    return all(not e["alive"] for e in enemies)


def pygame_init():
    global GAME_STAGE_STATUS, PAST_GAME_STATE_STATUS, PHASE_PLAYER_ANIMATION, PLAYER, PREV_GAME_STAGE_STATUS, MOUSE_PRESSED
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
    player_hp = PLAYER_MAX_HP
    player_max_hp = PLAYER_MAX_HP

    frozen_frame = None

    victory_delay = 1.2
    victory_delay_start = 0.0

    while running:
        pygame.display.update()

        if GAME_STAGE_STATUS == 'fight' and PREV_GAME_STAGE_STATUS not in ('fight', 'pause_menu'):
            generate_level_enemies(STAGE_PLAYER_LEVEL)
            dump_x_y(FIGHT_BG_START_X, BG_Y_FIGHT, x_y_fight_file)
            fireballs.clear()
            enemy_fireballs.clear()
            enemy_fireball_timers.clear()
            player_hp = PLAYER_MAX_HP
            player_max_hp = PLAYER_MAX_HP
            victory_delay_start = 0.0

        PREV_GAME_STAGE_STATUS = GAME_STAGE_STATUS

        if GAME_STAGE_STATUS == 'main_menu':
            main_menu(game_screen, [window.font_bold_60, window.font_bold_40])
        elif GAME_STAGE_STATUS == 'choose_character':
            choose_character(window, game_screen, [window.font_bold_60, window.font_bold_40])
        elif GAME_STAGE_STATUS == 'pause_menu':
            pause_menu(game_screen, window.font_bold_60, frozen_frame)
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

            maybe_launch_enemy_fireballs(window, player_screen_x, player_screen_y)
            player_hp = update_enemy_fireballs(game_screen, window, player_screen_x, player_screen_y, player_hp)

            player_hp = check_enemy_attacks_player(player_screen_x, player_hp)
            player_hp = max(0, player_hp)

            draw_player_hp(game_screen, player_hp, player_max_hp)

            if player_hp <= 0:
                GAME_STAGE_STATUS = 'defeat'

            elif check_victory():
                now = time.time()
                if victory_delay_start == 0.0:
                    victory_delay_start = now
                elif now - victory_delay_start >= victory_delay:
                    GAME_STAGE_STATUS = 'victory'
        elif GAME_STAGE_STATUS == 'victory':
            MOUSE_PRESSED = victory_screen(game_screen,
                                           [window.font_bold_80, window.font_bold_60],
                                           MOUSE_PRESSED)
        elif GAME_STAGE_STATUS == 'defeat':
            MOUSE_PRESSED = defeat_screen(game_screen,
                                          [window.font_bold_80, window.font_bold_60],
                                          MOUSE_PRESSED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if GAME_STAGE_STATUS == 'pause_menu':
                        GAME_STAGE_STATUS = PAST_GAME_STATE_STATUS
                        PAST_GAME_STATE_STATUS = 'pause_menu'
                    elif GAME_STAGE_STATUS not in ('main_menu', 'victory'):
                        frozen_frame = game_screen.copy()
                        PAST_GAME_STATE_STATUS = GAME_STAGE_STATUS
                        GAME_STAGE_STATUS = 'pause_menu'


        # pygame.display.flip()

        clock.tick(60)

    pygame.quit()