from random import randint
import time


class basic:
    @staticmethod
    def pause(ms):
        time.sleep(ms/1000)

def print_leds_matrix(matrix: list[list[str]]) -> None:
    final_str = ""
    for row in matrix:
        final_str += " ".join(row) + "\n"
    print(final_str)


class ObjectCharactersEnum:
    EMPTY = '.'
    ENEMY = 'E'
    BULLET = 'B'
    PLAYER = 'P'
    DEFAULT= '#'

class CartesianPosition:
    __position  = (0,0)
    __char: ObjectCharactersEnum = ObjectCharactersEnum.DEFAULT
    @property
    def x(self): return self.__position[0]

    @property
    def y(self): return self.__position[1]

    def set_position(self, x: int, y: int):
        self.__position = (x, y)

class Led:
    def __init__(self):
        self.leds_matrix = ['. . . . .'.split() for _ in range(5)]

    def plot(self, x: int, y: int, char: str):
        self.leds_matrix[x][y] = char
        # led.plot(x,y)

    def unplot(self, x: int, y: int):
        self.leds_matrix[x][y] = '.'
        # led.unplot(x,y)

    def plot_brightness(self, x: int, y: int, bright: int, char: str):
        self.plot(x,y, char)
        # led.plot_brightness(x, y, bright)

    def is_position_a(self, x: int, y: int, char: str) -> bool:
        return self.leds_matrix[x][y] == char

class UserPlatform(CartesianPosition):
    def __init__(self, leds_manager_instance: Led):
        self.set_position(4, 2)
        self.leds_manager = leds_manager_instance
        self.leds_manager.plot(self.x, self.y, ObjectCharactersEnum.PLAYER)

    def go_left(self):
        if (self.y - 1) == -1:
            return
        self.leds_manager.unplot(self.x, self.y)
        self.set_position(self.x, self.y - 1)
        self.leds_manager.plot(self.x, self.y, ObjectCharactersEnum.PLAYER)

    def go_right(self):
        if (self.y + 1) == 5:
            return
        self.leds_manager.unplot(self.x, self.y)
        self.set_position(self.x, self.y + 1)
        self.leds_manager.plot(self.x, self.y, ObjectCharactersEnum.PLAYER)


class Enemy(CartesianPosition):
    def __init__(self, leds_manager_instance: Led):
        self.leds_manager = leds_manager_instance
        enemy_position = self.__new_position()
        if enemy_position:
            self.set_position(enemy_position[0], enemy_position[1])
            self.leds_manager.plot(*enemy_position)

    def __new_position(self, enemies_counter: int = 0):
        if enemies_counter == 5:
            return None
        new_position= (0, randint(0, 4), ObjectCharactersEnum.ENEMY)
        return self.__new_position(enemies_counter+1) \
            if self.leds_manager.is_position_a(new_position[0], new_position[1], ObjectCharactersEnum.ENEMY) \
            else new_position

class Bullet(CartesianPosition):
    def __init__(self, platform: UserPlatform, leds_manager_instance: Led):
        self.set_position(platform.x - 1, platform.y)
        self.leds_manager = leds_manager_instance
    def __is_collision_with_enemy(self) -> bool:
        if self.leds_manager.is_position_a(self.x, self.y, ObjectCharactersEnum.ENEMY): # If it has enemy
            self.leds_manager.unplot(self.x, self.y) # Kills it
            return True
        return False

    def walk(self) -> bool:
        if self.x == 0: return False # Reached last row
        if self.leds_manager.is_position_a(self.x, self.y, ObjectCharactersEnum.BULLET):
            self.leds_manager.unplot(self.x, self.y)
        self.set_position(self.x - 1, self.y)
        if self.__is_collision_with_enemy(): return False
        self.leds_manager.plot(self.x, self.y, ObjectCharactersEnum.BULLET) # Plot bullet's led
        return True

def main():
    leds_manager = Led()
    user_platform = UserPlatform(leds_manager)
    enemies: list[Enemy] = [Enemy(leds_manager) for _ in range(3)]
    #user_input = input("A para esquerda, D para direita, W para atirar")
    print_leds_matrix(leds_manager.leds_matrix)
    b = Bullet(user_platform, leds_manager)
    b.walk()
    print_leds_matrix(leds_manager.leds_matrix)
    b.walk()
    print_leds_matrix(leds_manager.leds_matrix)
    b.walk()
    print_leds_matrix(leds_manager.leds_matrix)

main()