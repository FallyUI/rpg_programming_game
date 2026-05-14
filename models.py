# маг -> лучник -> воин -> маг


#  главный класс

class Character:
    def __init__(self, game_class, weapon, armor, shield):
        self.game_class = game_class
        self.weapon = weapon
        self.armor = armor
        self.shield = shield


#  классы персонажей

class Wizard:
    def __init__(self):
        self.name = 'Маг'
        self.category = 'Wizard'
        self.category_up = 'Archer'
        self.health = 80

class Archer:
    def __init__(self):
        self.name = 'Лучник'
        self.category = 'Archer'
        self.category_up = 'Warrior'
        self.health = 100

class Warrior:
    def __init__(self):
        self.name = 'Воин'
        self.category = 'Warrior'
        self.category_up = 'Wizard'
        self.health = 150


#  классы врагов

class Slime:
    def __init__(self):
        self.name = 'Слизень'
        self.category = 'Slime'
        self.category_up = 'Wizard'
        self.health = 40
        self.armor = 0
        self.damage = 5


#  классы оружия

class ShortSword:
    def __init__(self):
        self.damage = 5

class Sword:
    def __init__(self):
        self.damage = 10

class Axe:
    def __init__(self):
        self.damage = 20

#
class FastBow:
    def __init__(self):
        self.damage = 10

class Bow:
    def __init__(self):
        self.damage = 15

class CrossBow:
    def __init__(self):
        self.damage = 20

#
class Thunder:
    def __init__(self):
        self.damage = 5

class Fireball:
    def __init__(self):
        self.damage = 10

class Ray:
    def __init__(self):
        self.damage = 15


#  классы брони

class NoArmor:
    def __init__(self):
        self.armor = 0

class LightArmor:
    def __init__(self):
        self.armor = 30

class ChainMail:
    def __init__(self):
        self.armor = 60

class IronArmor:
    def __init__(self):
        self.armor = 100

class GoldArmor:
    def __init__(self):
        self.armor = 150


#  классы щитов

class NoShield:
    def __init__(self):
        self.shield = 0

class SmallShield:
    def __init__(self):
        self.shield = 30

class Shield:
    def __init__(self):
        self.shield = 60

class LargeShield:
    def __init__(self):
        self.shield = 90

class IronShield:
    def __init__(self):
        self.shield = 150