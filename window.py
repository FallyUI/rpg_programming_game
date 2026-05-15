from tkinter import *
from tkinter import messagebox

from models import *
from files import *
from main import pygame_init

import asyncio
from multiprocessing import Process

def starting():
    subprocess.run(
        ["python", 'main.py'],
        capture_output=True,
        text=True,
        timeout=5
    )


is_running_user_code = False



def build_game_state():
    class_name = load_selected_class()

    if class_name == "Wizard":
        player = Character(Wizard(), Fireball(), NoArmor(), NoShield())
    elif class_name == "Archer":
        player = Character(Archer(), Bow(), NoArmor(), NoShield())
    else:
        player = Character(Warrior(), Sword(), NoArmor(), NoShield())

    enemy = Character(Slime(), ShortSword(), NoArmor(), NoShield())

    return {
        "player": player,
        "enemies": enemy
    }

keys = set()

def checked_text(text):
    list_lines = list()
    line = str()
    new_texts = text.replace("\n", "&")
    for char in new_texts:
        if char == '&':
            line += ''
            if len(line) > 2:
                list_lines.append(line)
            line = ''
        else:
            line += char

    return list_lines


def add_keys(event):
    global is_running_user_code
    keys.add(event.keysym)
    print(keys)
    try:
        keys.remove("Shift_R")
    except KeyError:
        pass
    if "Shift_L" in keys and "Return" in keys:
        print("Return")
        textarea.insert("insert", "\n")
        return "break"
    elif event.keysym == "Return":
        data = load_json()
        if data["code_status"] == 0 and not is_running_user_code:
            is_running_user_code = True
            text = textarea.get("1.0", "end")
            new_text = checked_text(text)
            logs = asyncio.run(create_file(build_game_state(), new_text))
            print(logs)
            is_running_user_code = False
            data["code_status"] = 0
            save_json(data)
        else:
            messagebox.showinfo('консоль', 'код выполняется\nпожалуйста, подождите...')
        return "break"
    elif ("BackSpace" or "Delete") in keys:
        try:
            textarea.delete("sel.first", "sel.last")
        except TclError:
            if event.keysym == "BackSpace":
                textarea.delete("insert-1c")
            elif event.keysym == "Delete":
                textarea.delete("insert")
            return "break"

    return event.char


def remove_keys(event):
    keys.discard(event.keysym)



if __name__ == "__main__":
    game_process = Process(target=pygame_init)
    game_process.start()

    root = Tk()
    root.title('console')
    root.geometry('500x500+730+250')
    root.resizable(False, False)
    root.iconbitmap('images/icon-console.ico')

    textarea = Text(root, background='black', foreground='white', height=100, width=100, insertbackground='white')
    textarea.bind('<KeyPress>', add_keys)
    textarea.bind('<KeyRelease>', remove_keys)
    textarea.focus()
    textarea.pack()

    root.mainloop()

    game_process.terminate()



