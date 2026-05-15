import pickle, subprocess, json, os, time


SELECTED_CLASS_FILE = 'data/selected_class.json'
ENEMIES_FILE = 'data/enemies.json'
ENEMIES_LOCK = ENEMIES_FILE + '.lock'


user_code = ('from actions import *\n'
             'from random import choice, randint\n'
             'import pickle, time\n\n'
             'with open("data/classes.pkl", "rb") as file:\n'
             '  game_state = pickle.load(file)\n'
             'print(game_state)\n\n'
             'my_class = game_state["player"]\n'
             'enemy = game_state["enemies"]\n\n')


def save_selected_class(class_name):
    with open(SELECTED_CLASS_FILE, 'w') as f:
        json.dump({"selected_class": class_name}, f)


def load_selected_class():
    try:
        with open(SELECTED_CLASS_FILE, 'r') as f:
            return json.load(f).get("selected_class", "Warrior")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Warrior"


def acquire_lock(lock_path, timeout=2.0, retry=0.005):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(retry)
    return False


def release_lock(lock_path):
    try:
        os.remove(lock_path)
    except FileNotFoundError:
        pass


async def create_code(code):
    checked_code = []
    for line in code:
        if line.startswith('while'):
            checked_code.append(line + '\n')
        elif line.startswith('for'):
            checked_code.append(line + '\n')
        elif line in ['\tright()', '\tleft()', '\tattack_enemy()', '\tclear_dead()']:
            checked_code.append(line + '\n')
            checked_code.append('\ttime.sleep(2)\n')
        elif line in ['right()', 'left()', 'attack_enemy()', 'clear_dead()']:
            checked_code.append(line + '\n')
            checked_code.append('time.sleep(2)\n')
        elif line.startswith('a =') or line.startswith('b ='):
            checked_code.append(line + '\n')

    return checked_code


async def create_file(game_state, code):
    with open('user_code.py', 'w') as file:
        print(code)
        print(type(code))
        checked_code = await create_code(code)
        file.write(user_code + ''.join(checked_code))

    with open('data/classes.pkl', 'wb') as file:
        pickle.dump(game_state, file)

    return start_file()


def start_file():
    data = load_json()
    data["code_status"] = 1
    save_json(data)
    result = subprocess.run(
        ["python", 'user_code.py'],
        capture_output=True,
        text=True,
        timeout=5
    )
    output = result.stdout
    if result.stderr:
        output += "\n[ошибка]:\n" + result.stderr
        data = load_json()
        data["code_status"] = 0
        save_json(data)
    return output


def load_x_y(file):
    lock_path = file + '.lock'
    acquire_lock(lock_path)
    try:
        for attempt in range(10):
            try:
                with open(file, 'r') as f:
                    text = f.read().strip()
                if not text:
                    continue
                parts = text.split(' ', maxsplit=1)
                return int(parts[0]), int(parts[1])
            except (ValueError, IndexError):
                continue
        return 0, 0
    finally:
        release_lock(lock_path)


def dump_x_y(x, y, file):
    lock_path = file + '.lock'
    acquire_lock(lock_path)
    try:
        with open(file, 'w') as f:
            f.write(f'{x} {y}')
    finally:
        release_lock(lock_path)


def load_json():
    try:
        with open('data/data.json', 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        save_json({"code_status": 0, "animation_side": "right", "fireball_launch": None})
        return {"code_status": 0, "animation_side": "right", "fireball_launch": None}


def save_json(data):
    with open('data/data.json', 'w') as file:
        json.dump(data, file)
    return 'ok'


def load_enemies():
    acquire_lock(ENEMIES_LOCK)
    try:
        with open(ENEMIES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    finally:
        release_lock(ENEMIES_LOCK)


def save_enemies(enemies):
    acquire_lock(ENEMIES_LOCK)
    try:
        with open(ENEMIES_FILE, 'w') as f:
            json.dump(enemies, f)
    finally:
        release_lock(ENEMIES_LOCK)