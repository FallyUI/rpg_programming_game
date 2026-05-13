from actions import *
from random import choice, randint
import pickle, time

with open("data/classes.pkl", "rb") as file:
  game_state = pickle.load(file)
print(game_state)

my_class = game_state["player"]
enemy = game_state["enemies"]

while True:
    right()
time.sleep(2)
right()
time.sleep(2)
