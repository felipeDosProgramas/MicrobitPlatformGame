import time

def get_initial_leds_matrix() -> LedsMatrixType:
    return [
        ['.', '.', '.','.','.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '#', '.', '.']
    ];

class basic:
    def pause(self):
        time.sleep(.5);

def print_leds_matrix(matrix: list[list[str]]) -> None:
    final_str = "";
    for row in matrix:
        final_str += f"{" ".join(row)}\n";
    print(final_str);
