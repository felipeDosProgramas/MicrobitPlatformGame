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
    def __init__(self, x: int, y: int):
        self.__position = x, y

    @property
    def x(self): return self.__position[0]

    @property
    def y(self): return self.__position[1]

    def set_position(self, x: int, y: int):
        self.__position = (x, y)

class TickMovement:
    def __init__(self, position_before_move: CartesianPosition, new_x: int, new_y: int):
        self.__position_before_move = position_before_move
        self.__new_position = CartesianPosition(new_x, new_y)
    @property
    def position_before_move(self): return self.__position_before_move
    @property
    def position_after_move(self): return self.__new_position

class CartesianMove(CartesianPosition):
    tick_movements: list[TickMovement] = []
    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def set_position(self, x: int, y: int):
        self.tick_movements.append(
            TickMovement(self, x, y)
        )

class Led:
    def __init__(self):
        self.leds_matrix = ['. . . . .'.split() for _ in range(5)]

    def plot(self, position: CartesianPosition, character: str):
        self.leds_matrix[position.x][position.y] = character
        # led.plot(x,y)
    def unplot(self, position: CartesianPosition):
        self.leds_matrix[position.x][position.y] = ObjectCharactersEnum.EMPTY
        # led.unplot(x,y)

class UserPlatform(CartesianMove):
    def __init__(self):
        super().__init__(4, 2)

    def go_left(self):
        if self.y == 0:
            return
        self.set_position(self.x, self.y - 1)

    def go_right(self):
        if self.y == 4:
            return
        self.set_position(self.x, self.y + 1)


class Enemy(CartesianMove):
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


class Bullet(CartesianMove):
    def __init__(self, position: CartesianPosition):
        super().__init__(position.x - 1, position.y)

    def walk(self):
        self.set_position(self.x - 1, self.y)


class BulletsFactory:
    def __init__(self):
        self.bullets: list[Bullet] = []
        self.dead_bullet_indexes: list[int] = []

    def new_bullet(self, new_bullet_position: CartesianPosition):
        self.bullets.append(Bullet(new_bullet_position))

    def update_bullets(self, enemies_factory: EnemiesFactory):
        self.dead_bullet_indexes = []
        for bullet_index in range(len(self.bullets)):
            self.bullets[bullet_index].walk()
            if enemies_factory.check_enemies(self.bullets[bullet_index]) or self.bullets[bullet_index].x == 0:
                self.dead_bullet_indexes.append(bullet_index)

    def clear_killed_bullets(self):
        for dead_bullet_index in reversed(self.dead_bullet_indexes):
            self.bullets.pop(dead_bullet_index)


class Game:
    def __init__(self):
        self._player = UserPlatform()
        self._object_renderer = Led()
        self._bullets_factory = BulletsFactory()

class GameRenderer(Game):
    def __render_player(self):
        for player_movement in self._player.tick_movements:
            self._object_renderer.unplot(player_movement.position_before_move)
            self._object_renderer.plot(player_movement.position_after_move, ObjectCharactersEnum.PLAYER)
        self._player.tick_movements = []
    def __render_bullets(self):
        for dead_bullet_index in self._bullets_factory.dead_bullet_indexes:
            self._object_renderer.unplot(self._bullets_factory.bullets[dead_bullet_index])
        self._bullets_factory.clear_killed_bullets()
        for bullet in self._bullets_factory.bullets:
            self._object_renderer.plot(bullet, ObjectCharactersEnum.BULLET)
    def render(self):
        self.__render_player()
        self.__render_bullets()
