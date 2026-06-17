from collections.abc import Callable
from setup import *;

type LedsMatrixType = List[List[str]];
leds_matrix: LedsMatrixType = get_initial_leds_matrix();

class Led:
    @staticmethod
    def plot(x: int, y: int) -> None:
        global leds_matrix;
        leds_matrix[x][y] = '#';

    @staticmethod
    def unplot(x: int, y: int) -> None:
        global leds_matrix;
        leds_matrix[x][y] = '.';
        # led.unplot(x,y)

    @staticmethod
    def plot_brightness(x: int, y: int, bright: int) -> None:
        Led.plot(x,y)
        # led.plot_brightness(*args)



class UserPlatform:
    def __init__(self):
        self.position: (int, int) = (4, 2);

    def __able_to_go(self, limit: int) -> bool:
        return self.position[1] != limit;

    def __go(self, operation: Callable[[int], int]) -> bool:
        self.position = (self.position[0], operation(self.position[1]));
        return True;

    def go_left(self) -> None:
        if not self.__able_to_go(0): return;
        Led.unplot(*self.position);
        self.__go(lambda x: x - 1);
        Led.plot(*self.position);

    def go_right(self) -> None:
        if not self.__able_to_go(4): return;
        Led.unplot(*self.position);
        self.__go(lambda x: x + 1);
        Led.plot(*self.position);



if __name__ == '__main__':
    platform = UserPlatform();
    platform.go_right()
    print_leds_matrix(leds_matrix)
    platform.go_right()
    print_leds_matrix(leds_matrix)

    platform.go_left()
    print_leds_matrix(leds_matrix)
    platform.go_left()
    print_leds_matrix(leds_matrix)