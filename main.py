from random import randint

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
    __position: tuple[int, int]  = (0,0)
    def __init__(self, x: int, y: int):
        self.__position = x, y

    @property
    def x(self): return self.__position[0]

    @property
    def y(self): return self.__position[1]

    def set_position(self, x: int, y: int):
        self.__position = (x, y)

class Led:
    def __init__(self):
        self.leds_matrix = ['. . . . .'.split() for _ in range(5)]

    def plot(self, position: CartesianPosition, character: str):
        self.leds_matrix[position.x][position.y] = character
        # led.plot(x,y)
    def unplot(self, position: CartesianPosition):
        self.leds_matrix[position.x][position.y] = ObjectCharactersEnum.EMPTY
        # led.unplot(x,y)
    def plot_brightness(self, position: CartesianPosition, bright: int, char: str):
        self.plot(position, char)
        # led.plot_brightness(x, y, bright)

    def is_position_a(self,position: CartesianPosition , char: str) -> bool:
        return self.leds_matrix[position.x][position.y] == char

class UserPlatform(CartesianPosition):
    def __init__(self, leds_manager_instance: Led):
        super().__init__(4, 2)
        self.leds_manager = leds_manager_instance
        self.leds_manager.plot(self, ObjectCharactersEnum.PLAYER)

    def go_left(self):
        if (self.y - 1) == -1:
            return
        self.leds_manager.unplot(self)
        self.set_position(self.x, self.y - 1)
        self.leds_manager.plot(self, ObjectCharactersEnum.PLAYER)

    def go_right(self):
        if (self.y + 1) == 5:
            return
        self.leds_manager.unplot(self)
        self.set_position(self.x, self.y + 1)
        self.leds_manager.plot(self, ObjectCharactersEnum.PLAYER)


class Enemy(CartesianPosition):
    def __init__(self, position: CartesianPosition):
        super().__init__(position.x, position.y)

    def is_on_position(self, pos: CartesianPosition) -> bool:
        return self.x == pos.x and self.y == pos.y

class EnemiesFactory:
    def __init__(self):
        self.enemies = []
        self.killed_enemies = []
        self.enemies_empty_slots: list[int] = [0,1,2,3,4] # list(range(5)) doesn't works on MicroPython

    def new_enemy(self):
        new_enemy_position = self.__new_position()
        self.enemies.append(Enemy(new_enemy_position))

    def __new_position(self):
        return CartesianPosition(
            0,
            self.enemies_empty_slots.pop(
                randint(0, len(self.enemies_empty_slots) - 1)
            )
        )
    def kill_enemy(self, enemy: Enemy):
        self.enemies_empty_slots.append(enemy.y)
        self.enemies.remove(enemy)
        self.killed_enemies.append(enemy)

    def check_enemies(self, position: CartesianPosition) -> bool:
        for enemy in self.enemies:
            if enemy.is_on_position(position):
                self.kill_enemy(enemy)
                return True
        return False

    def render_enemies(self, leds_manager: Led):
        for enemy in self.enemies:
            leds_manager.plot(enemy, ObjectCharactersEnum.ENEMY)

    def flush_dead_enemies(self, leds_manager: Led):
        for enemy in self.killed_enemies:
            leds_manager.unplot(enemy)
        self.killed_enemies = []


class Bullet(CartesianPosition):
    def __init__(self, position: CartesianPosition):
        super().__init__(position.x - 1, position.y)

    def walk(self):
        self.set_position(self.x - 1, self.y)


class BulletsFactory:
    def __init__(self, leds_manager_instance: Led):
        self.bullets: list[Bullet] = []
        self.leds_manager = leds_manager_instance
        self.dead_bullet_indexes: list[int] = []

    def new_bullet(self, new_bullet_position: CartesianPosition):
        self.bullets.append(Bullet(new_bullet_position))

    def update_bullets(self, enemies_factory: EnemiesFactory):
        for bullet_index in range(len(self.bullets)):
            self.leds_manager.unplot(self.bullets[bullet_index])
            self.bullets[bullet_index].walk()
            if enemies_factory.check_enemies(self.bullets[bullet_index]) or self.bullets[bullet_index].x == 0:
                self.dead_bullet_indexes.append(bullet_index)

    def render_bullets(self):
        for dead_bullet_index in reversed(self.dead_bullet_indexes):
            self.bullets.pop(dead_bullet_index)
        self.dead_bullet_indexes = []
        for bullet in self.bullets:
            self.leds_manager.plot(bullet, ObjectCharactersEnum.BULLET)





