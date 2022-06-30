#   _____      _   _      __ _           _ _              __      ___                 _ _
#  |  __ \    | | | |    / _(_)         | (_)             \ \    / (_)               | (_)
#  | |__) |_ _| |_| |__ | |_ _ _ __   __| |_ _ __   __ _   \ \  / / _ ___ _   _  __ _| |_ _______ _ __
#  |  ___/ _` | __| '_ \|  _| | '_ \ / _` | | '_ \ / _` |   \ \/ / | / __| | | |/ _` | | |_  / _ \ '__|
#  | |  | (_| | |_| | | | | | | | | | (_| | | | | | (_| |    \  /  | \__ \ |_| | (_| | | |/ /  __/ |
#  |_|   \__,_|\__|_| |_|_| |_|_| |_|\__,_|_|_| |_|\__, |     \/   |_|___/\__,_|\__,_|_|_/___\___|_|
#                                                   __/ |
#                                                  |___/

import pygame
from enum import Enum
from queue import PriorityQueue
import math


class GridSquareState(Enum):
    EMPTY = pygame.Color(255, 255, 255)
    BARRIER = pygame.Color(0, 0, 0)
    START = pygame.Color(255, 255, 0)
    END = pygame.Color(0, 255, 255)
    NO_PATH = pygame.Color(255, 0, 0)
    POSSIBLE_PATH = pygame.Color(0, 255, 0)
    DEFINITIVE_PATH = pygame.Color(0, 255, 255)


class GridSquare:

    def __init__(self, window, blocksize, x, y):
        self.window = window
        self.blocksize = blocksize
        self.x = x
        self.y = y
        self.square = pygame.Rect(x * blocksize, y * blocksize, blocksize, blocksize)
        self.state = GridSquareState.EMPTY

    def draw(self):
        pygame.draw.rect(self.window, self.state.value, self.square)

    def draw_and_update(self):
        self.draw()
        # pygame.display.flip()
        # pygame.display.update()

    def make_start(self):
        self.state = GridSquareState.START
        self.draw_and_update()

    def make_end(self):
        self.state = GridSquareState.END
        self.draw_and_update()

    def make_barrier(self):
        self.state = GridSquareState.BARRIER
        self.draw_and_update()

    def make_empty(self):
        self.state = GridSquareState.EMPTY
        self.draw_and_update()

    def make_possible_path(self):
        self.state = GridSquareState.POSSIBLE_PATH
        self.draw_and_update()

    def make_no_path(self):
        self.state = GridSquareState.NO_PATH
        self.draw_and_update()

    def make_path(self):
        self.state = GridSquareState.DEFINITIVE_PATH
        self.draw_and_update()

    def is_barrier(self):
        return self.state == GridSquareState.BARRIER

    def __lt__(self, other):
        return False


class Grid:

    def __init__(self, window, rows, width, height):
        assert (width == height)

        self.window = window
        self.rows = rows
        self.width = width
        self.height = height

        self.grid = []
        self.blocksize = width // rows

        for y in range(rows):
            self.grid.append([])
            for x in range(rows):
                square = GridSquare(window, self.blocksize, x, y)
                square.draw()
                self.grid[y].append(square)
        pygame.display.flip()
        pygame.display.update()

    def get_pos_of_mouse_clicked(self, pos):
        x, y = pos

        row = y // self.blocksize
        col = x // self.blocksize

        if 0 <= row < self.rows and 0 < col < self.rows:
            return row, col
        return -1, -1

    def get_square(self, row, col):
        if 0 <= row < self.rows and 0 < col < self.rows:
            return self.grid[row][col]
        return None

    def reset_grid(self):
        for y in range(self.rows):
            for x in range(self.rows):
                self.grid[y][x].make_empty()

    def get_neigbors(self, square):
        x = square.x
        y = square.y

        out = []

        for coord in [(x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1)]:
            # for c in [x - 1, x, x + 1]:
            #    for r in [y - 1, y, y + 1]:
            if 0 <= coord[0] < self.rows and 0 <= coord[1] < self.rows:  # and not (x == c and y == r):
                neighbor = self.grid[coord[1]][coord[0]]
                if not neighbor.is_barrier():
                    out.append(neighbor)
        return out


class Button:
    # https://github.com/russs123/pygame_tutorials/tree/main/Button
    def __init__(self, window, x, y, img, img_size, function):
        self.window = window
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(img, (img_size, img_size))
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)
        self.function = function
        self.clicked = False

        self.window.blit(self.img, (self.rect.x, self.rect.y))

    def act(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        if action:
            self.function()


def reconstruct_path(came_from, current):
    while current in came_from:
        current = came_from[current]
        current.make_path()


def h(node, end):
    # return math.sqrt((node.x - end.x) ** 2 + (node.y - end.y) ** 2)
    return abs(node.x - end.x) + abs(node.y - end.y)


def algorithm(grid, start, goal):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))  # f_score, count, node
    open_set_values = {start}

    came_from = {}

    f_score = {square: float("inf") for row in grid.grid for square in row}
    f_score[start] = h(start, goal)

    g_score = {square: float("inf") for row in grid.grid for square in row}
    g_score[start] = 0

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_values.remove(current)

        if current == goal:
            reconstruct_path(came_from, goal)
            return

        neighbors = grid.get_neigbors(current)

        for n in neighbors:
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g_score
                f_score[n] = tentative_g_score + h(n, goal)
                if n not in open_set_values:
                    count += 1
                    open_set.put((f_score[n], count, n))
                    open_set_values.add(n)
                    n.make_possible_path()

        if current != start:
            current.make_no_path()

    # goal never reached
    return


class Game:

    def __init__(self, rows, width):

        extra_space = 100  # for buttons

        self.width = width
        self.rows = rows
        self.window = pygame.display.set_mode((width, width + extra_space))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("A* Path Finding Algorithm")
        self.grid = Grid(self.window, rows, width, width)

        # play button (https://www.freeiconspng.com/img/18927)
        play_img = pygame.image.load("images/play.png").convert_alpha()
        self.play_btn = Button(self.window, 350, 820, play_img, 40, self.start_animation)
        self.play_btn.act()

        # reload button (https://www.freeiconspng.com/img/16891)
        reload_img = pygame.image.load("images/reload.png").convert_alpha()
        self.reload_btn = Button(self.window, 450, 820, reload_img, 40, self.reload_animation)
        self.reload_btn.act()

        pygame.display.flip()
        pygame.display.update()

        self.start = None
        self.end = None

        self.play()

    def reload_animation(self):
        self.grid.reset_grid()
        # pygame.display.flip()
        # pygame.display.update()
        self.play()

    def start_animation(self):
        if self.start and self.end:
            algorithm(self.grid, self.start, self.end)
        print("started animation")

    def play(self):
        run = True

        self.start = None
        self.end = None

        while run:
            self.play_btn.act()
            self.reload_btn.act()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed()[0]:  # Left click
                    pos = pygame.mouse.get_pos()
                    row, col = self.grid.get_pos_of_mouse_clicked(pos)
                    square = self.grid.get_square(row, col)

                    if square:
                        if not self.start and square != self.end:
                            self.start = square
                            self.start.make_start()
                        elif not self.end and square != self.start:
                            self.end = square
                            self.end.make_end()
                        elif square != self.start and square != self.end:
                            square.make_barrier()

                if pygame.mouse.get_pressed()[2]:  # Right click
                    pos = pygame.mouse.get_pos()
                    row, col = self.grid.get_pos_of_mouse_clicked(pos)
                    square = self.grid.get_square(row, col)

                    if square:
                        if square == self.start:
                            self.start = None
                        elif square == self.end:
                            self.end = None
                        square.make_empty()

            pygame.display.flip()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    pygame.init()

    WIDTH = 800
    NUMBER_OF_ROWS = 50

    Game(NUMBER_OF_ROWS, WIDTH)
