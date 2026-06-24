from collections.abc import Callable;
from random import randint
import time

def get_initial_leds_matrix() -> list[list[str]]:
    return [
        ['.', '.', '.','.','.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.']
    ];

class basic:
    @staticmethod
    def pause(ms):
        time.sleep(ms);

def print_leds_matrix(matrix: list[list[str]]) -> None:
    final_str = "";
    for row in matrix:
        final_str += " ".join(row) + "\n"
    print(final_str);


leds_matrix: LedsMatrixType = get_initial_leds_matrix();

class Led:
    @staticmethod
    def plot(x: int, y: int):
        global leds_matrix;
        leds_matrix[x][y] = '#';
        # led.plot(x,y);

    @staticmethod
    def unplot(x: int, y: int):
        global leds_matrix;
        leds_matrix[x][y] = '.';
        # led.unplot(x,y)

    @staticmethod
    def plot_brightness(x: int, y: int, bright: int):
        Led.plot(x,y)
        # led.plot_brightness(*args)
    @staticmethod
    def plot_briefly(x: int, y: int):
        i = 0
        for _ in range(3):
            i += 1
            Led.plot_brightness(x, y, (85 * i))
            basic.pause(50)
        for _ in range(3):
            i -= 1
            Led.plot_brightness(x, y, (85 * i))
            basic.pause(50)
        Led.unplot(x,y);

class UserPlatform:
    def __init__(self):
        self.__position: tuple[int, int] = (4, 2);
        Led.plot(self.x, self.y);
    @property
    def x(self): return self.__position[0];
    @property
    def y(self): return self.__position[1];
    def go_left(self):
        if (self.y - 1) == -1:
            return;
        Led.unplot(self.x, self.y);
        self.__position = self.x, self.y - 1;
        Led.plot(self.x, self.y);
    def go_right(self):
        if (self.y + 1) == 5:
            return;
        Led.unplot(self.x, self.y);
        self.__position = self.x, self.y + 1;
        Led.plot(self.x, self.y);


class Enemy:
    @staticmethod
    def __new_position(enemies_counter: int = 0) -> tuple[int, int]|None:
        if enemies_counter == 5: return None;
        new_position: tuple[int, int] = 0, randint(0, 4);
        return Enemy.__new_position(enemies_counter+1) \
            if Enemy.has_enemy(new_position[0], new_position[1]) \
            else new_position;
    @staticmethod
    def new():
        enemy_position = Enemy.__new_position();
        if enemy_position:
            Led.plot(*enemy_position)
    @staticmethod
    def has_enemy(x: int, y: int) -> bool:
        return leds_matrix[x][y] == '#';
    @staticmethod
    def kill_enemy(x: int, y: int):
        Led.unplot(x, y);

class Bullet:
    def __init__(self, platform: UserPlatform):
        self.bullet_position = {"x": platform.x - 1, "y": platform.y};
        self.__bullet_walk();
    @property
    def x(self):
        return self.bullet_position["x"];
    @property
    def y(self):
        return self.bullet_position["y"];
    def __plot_bullet(self):
        Led.plot_briefly(self.x, self.y);
    def __is_collision_with_enemy(self) -> bool:
        if Enemy.has_enemy(self.x, self.y):
            Enemy.kill_enemy(self.x, self.y)
            return True
        return False

    def __bullet_walk(self):
        while self.x != 0:
            self.bullet_position["x"] -= 1;
            if self.__is_collision_with_enemy(): break;
            self.__plot_bullet()

if __name__ == '__main__':
    platform = UserPlatform();
    Enemy.new();
    Enemy.new();
    Enemy.new();
    print_leds_matrix(leds_matrix);
    print("__________________________________")
    platform.go_right()
    platform.go_right()
    print_leds_matrix(leds_matrix);
    print("__________________________________")
    Bullet(platform)
    print("__________________________________")