from random import choice, randint
import time, pickle
from files import load_x_y, dump_x_y, load_json, save_json, load_enemies, save_enemies


x_y_file = 'data/x_y.txt'
x_y_fight_file = 'data/x_y_fight.txt'
classes_file = 'data/classes.pkl'


MOVE_SPEED = 8


def _load_my_class():
    with open(classes_file, 'rb') as f:
        game_state = pickle.load(f)
    return game_state["player"]


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


def attack_enemy(index=0):
    my_class = _load_my_class()
    enemies = load_enemies()

    if not enemies:
        print("Нет врагов.")
        return

    if index is None:
        index = next((i for i, e in enumerate(enemies) if e["alive"]), None)
        if index is None:
            print("Все враги побеждены.")
            return

    if index >= len(enemies):
        print(f"Враг #{index} не существует. Всего врагов: {len(enemies)}")
        return

    enemy = enemies[index]

    if not enemy["alive"]:
        print(f"Враг #{index} уже побеждён.")
        return

    if my_class.game_class.category == "Wizard":
        base = my_class.weapon.damage
        is_crit = False
        if enemy.get("category_up", "") == my_class.game_class.category:
            roll = randint(0, 100)
            if roll >= 95:
                base *= 3
                is_crit = True
            else:
                base *= 2
                is_crit = True

        data = load_json()
        data["fireball_launch"] = {
            "enemy_index": index,
            "damage": base,
            "is_crit": is_crit,
        }
        save_json(data)
        print(f"Маг запускает фаербол → враг #{index} (урон: {base}{'!' if is_crit else ''})")
        return

    base = my_class.weapon.damage
    is_crit = False

    if enemy.get("category_up", "") == my_class.game_class.category:
        roll = randint(0, 100)
        if roll >= 95:
            base *= 3
            is_crit = True
            print("Критический удар!")
        else:
            base *= 2
            is_crit = True

    if enemy["armor"] > 0:
        remaining = enemy["armor"] - base
        if remaining < 0:
            enemy["armor"] = 0
            enemy["health"] += remaining
        else:
            enemy["armor"] = remaining
    else:
        enemy["health"] -= base

    enemy["hit_at"] = time.time()

    if enemy["health"] <= 0:
        enemy["health"] = 0
        enemy["alive"] = False
        enemy["hit_type"] = "died"
        print(f"Враг #{index} ({enemy['type']}) побеждён!")
    elif is_crit:
        enemy["hit_type"] = "crit"
        print(f"Враг #{index} — броня: {enemy['armor']}, хп: {enemy['health']}/{enemy['max_health']} (крит!)")
    else:
        enemy["hit_type"] = "normal"
        print(f"Враг #{index} — броня: {enemy['armor']}, хп: {enemy['health']}/{enemy['max_health']}")

    enemies[index] = enemy
    save_enemies(enemies)


def clear_dead():
    enemies = load_enemies()
    alive = [e for e in enemies if e["alive"]]
    removed = len(enemies) - len(alive)
    save_enemies(alive)
    print(f"Убрано мёртвых врагов: {removed}. Осталось: {len(alive)}")
