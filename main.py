class ObjectCharactersEnum:
    EMPTY = '.'
    ENEMY = 'E'
    BULLET = 'B'
    PLAYER = 'P'
    DEFAULT = '#'


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
        self.position_before_move = CartesianPosition(position_before_move.x, position_before_move.y)
        self.position_after_move = CartesianPosition(new_x, new_y)


class CartesianMove(CartesianPosition):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.tick_movements = []

    def set_position(self, x: int, y: int):
        self.tick_movements.append(
            TickMovement(self, x, y)
        )
        super().set_position(x, y)


class Led:
    def __init__(self):
        self.leds_matrix = [
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.']
        ]

    def plot(self, position: CartesianPosition, character: str):
        if not self.is_position_an(position, character):
            self.leds_matrix[position.y][position.x] = character
        led.plot(position.y, position.x)

    def unplot(self, position: CartesianPosition):
        self.leds_matrix[position.y][position.x] = ObjectCharactersEnum.EMPTY
        led.unplot(position.y, position.x)
    def is_position_an(self, position: CartesianPosition, character: str) -> bool:
        return self.leds_matrix[position.y][position.x] == character

class UserPlatform(CartesianMove):
    def __init__(self):
        super().__init__(4, 2)
        self.set_position(4, 2)

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
        self.empty_enemy_slots =   [
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        ]  # list(range(8)) doesn't works on MicroPython

    def new_enemy(self):
        new_enemy_position = self.__new_position()
        self.enemies.append(Enemy(new_enemy_position))

    def __new_position(self):
        enemy_slot_position_index = randint(0, len(self.empty_enemy_slots) - 1)
        new_y_position = self.empty_enemy_slots.pop(enemy_slot_position_index)
        return CartesianPosition(
            0 if new_y_position > 4 else 1,
            new_y_position if new_y_position < 5 else new_y_position - 5
        )  # this whole was in the same line

    def __kill_enemy_if_on_position(self, enemy: Enemy, position: CartesianPosition):
        if not enemy.is_on_position(position):
            return
        self.empty_enemy_slots.append(enemy.y)
        self.killed_enemies.append(enemy)

    def check_enemies(self, position: CartesianPosition):
        for enemy in self.enemies:
            self.__kill_enemy_if_on_position(enemy, position)
        for killed_enemy in self.killed_enemies:
            self.enemies.remove(killed_enemy)


class Bullet(CartesianMove):
    def __init__(self, position: CartesianPosition):
        super().__init__(position.x, position.y)

    def walk(self):
        super().set_position(self.x - 1, self.y)

def __check_enemy_y(enemy: Enemy, bullet: Bullet) -> bool:
    return enemy.y == bullet.y
def __check_enemies_area(enemy: Enemy, bullet: Bullet) -> bool:
    return bullet.x < 2
def __check_enemy_x(enemy: Enemy, bullet: Bullet) -> bool:
    return enemy.x == bullet.x


class BulletsFactory:
    def __init__(self):
        self.bullets = []
        self.dead_bullet_indexes = []

    def new_bullet(self, player_position: CartesianPosition):
        self.bullets.append(Bullet(player_position))

    def __update_bullet(self, bullet: Bullet, bullet_index: int):
        bullet.walk()
        if bullet.x == -1:
            self.dead_bullet_indexes.append(bullet_index)
    def __check_for_enemies(self,bullet: Bullet, enemies_position: list[Enemy], bullet_index: int):
        for enemy in enemies_position:
            if __check_enemy_y(enemy, bullet) and __check_enemies_area(enemy, bullet) and __check_enemy_x(enemy, bullet):
                self.dead_bullet_indexes.append(bullet_index)

    def update_bullets(self, enemies_position: list[Enemy]):
        self.dead_bullet_indexes = []
        for bullet_index in range(len(self.bullets)):
            self.__update_bullet(self.bullets[bullet_index], bullet_index)
            self.__check_for_enemies(self.bullets[bullet_index], enemies_position, bullet_index)

    def clear_killed_bullets(self):
        for dead_bullet_index_i in range(len(self.dead_bullet_indexes) - 1, -1, -1):
            self.bullets.pop(self.dead_bullet_indexes[dead_bullet_index_i])
        self.dead_bullet_indexes = []


class AbstractGame:
    def __init__(self):
        self._player = UserPlatform()
        self._object_renderer = Led()
        self._bullets_factory = BulletsFactory()
        self._enemies_factory = EnemiesFactory()


class GameUpdater(AbstractGame):
    def update(self):
        self._bullets_factory.update_bullets(self._enemies_factory.enemies)
        for bullet_index_i in range(len(self._bullets_factory.dead_bullet_indexes) - 1, -1, -1):
            self._enemies_factory.check_enemies(
                self._bullets_factory.bullets[self._bullets_factory.dead_bullet_indexes[bullet_index_i]]
            )


class GameRenderer(GameUpdater):
    def __render_enemies(self):
        for enemy in self._enemies_factory.enemies:
            self._object_renderer.plot(enemy, ObjectCharactersEnum.ENEMY)
        for killed_enemy in self._enemies_factory.killed_enemies:
            self._object_renderer.unplot(killed_enemy)
        self._enemies_factory.killed_enemies = []

    def __render_player_movement(self, player_movement: TickMovement):
        self._object_renderer.unplot(player_movement.position_before_move)
        self._object_renderer.plot(player_movement.position_after_move, ObjectCharactersEnum.PLAYER)

    def __render_player(self):
        for player_movement in self._player.tick_movements:
            self.__render_player_movement(player_movement)
        self._player.tick_movements = []

    def __render_bullet_movement(self, bullet_movement: TickMovement):
        if not self._object_renderer.is_position_an(
            bullet_movement.position_before_move, ObjectCharactersEnum.PLAYER
            ):
            self._object_renderer.unplot(bullet_movement.position_before_move)
        self._object_renderer.plot(bullet_movement.position_after_move, ObjectCharactersEnum.BULLET)

    def __render_bullet(self, bullet: Bullet):
        for bullet_movement in bullet.tick_movements:
            self.__render_bullet_movement(bullet_movement)
    def __render_bullets(self):
        for bullet in self._bullets_factory.bullets:
            self.__render_bullet(bullet)
        for dead_bullet_index in self._bullets_factory.dead_bullet_indexes:
            self._object_renderer.unplot(self._bullets_factory.bullets[dead_bullet_index])
        self._bullets_factory.clear_killed_bullets()


    def render(self):
        self.__render_player()
        self.__render_bullets()
        self.__render_enemies()


class GameRun(GameRenderer):
    """
        MicroPython doesn't understand Lambdas, and can't differentiate
        a class property and a class method declaration:
            self._player.go_left <-- he identifies it as a property
        input.on_button_pressed() needs a function name, so I had
        to declare an inner function inside the method.
    """
    def __setup_left_movement_event(self):
        def go_left(): self._player.go_left()
        input.on_button_pressed(Button.A, go_left)

    def __setup_right_movement_event(self):
        def go_right(): self._player.go_right()
        input.on_button_pressed(Button.B, go_right)

    def __setup_shot_action_event(self):
        def shot(): self._bullets_factory.new_bullet(self._player)
        input.on_button_pressed(Button.AB, shot)

    def setup(self):
        self.__setup_left_movement_event()
        self.__setup_right_movement_event()
        self.__setup_shot_action_event()

    def level1(self):
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()

    def level2(self):
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()

    def level3(self):
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self._enemies_factory.new_enemy()
        self.__run()

    def __run(self):
        self.render()
        while len(self._enemies_factory.enemies) != 0:
            basic.pause(300)
            self.update()
            self.render()


gm = GameRun()
gm.setup()
gm.level1()
gm.level2()
gm.level3()
basic.show_string("Parabens!")