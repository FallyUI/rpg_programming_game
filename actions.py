from random import choice, randint
import time
from files import load_x_y, dump_x_y, load_json, save_json


x_y_file = 'data/x_y.txt'
x_y_fight_file = 'data/x_y_fight.txt'


MOVE_SPEED = 8


def check_json():
    data = load_json()
    print(data["code_status"])
    if data["code_status"] == 1:
        data["code_status"] = 0
        save_json(data)


def printing(enemy):
    print(enemy.armor.armor)
    print(enemy.game_class.health)
    print()
    time.sleep(2)


def get_damage(my_class, enemy, user_damage):
    if my_class.game_class.category_up == enemy.game_class.category:
        rand_damage = randint(0, 100)
        if rand_damage >= 95:
            return user_damage * 3
        return user_damage * 2
    return user_damage


def check_damage(my_class, enemy):
    damage = get_damage(my_class, enemy, my_class.weapon.damage)
    if enemy.armor.armor:
        if (enemy.armor.armor - damage) < 0:
            health_damage = damage - enemy.armor.armor
            enemy.armor.armor = 0
            enemy.game_class.health -= health_damage
            printing(enemy)
        else:
            enemy.armor.armor -= damage
            printing(enemy)
    else:
        if (enemy.game_class.health - damage) <= 0:
            enemy.game_class.health -= damage
            print('Вы победили!')
        else:
            enemy.game_class.health -= damage
            printing(enemy)


def player_right():
    bg_x, bg_y = load_x_y(x_y_file)
    bg_x -= MOVE_SPEED
    dump_x_y(bg_x, bg_y, x_y_file)


def player_left():
    bg_x, bg_y = load_x_y(x_y_file)
    bg_x += MOVE_SPEED
    dump_x_y(bg_x, bg_y, x_y_file)


def right():
    bg_x, bg_y = load_x_y(x_y_fight_file)
    bg_x -= MOVE_SPEED
    dump_x_y(bg_x, bg_y, x_y_fight_file)
    data = load_json()
    data["animation_side"] = "right"
    save_json(data)


def left():
    bg_x, bg_y = load_x_y(x_y_fight_file)
    bg_x += MOVE_SPEED
    dump_x_y(bg_x, bg_y, x_y_fight_file)
    data = load_json()
    data["animation_side"] = "left"
    save_json(data)

