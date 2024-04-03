import math
import random
from PIL import Image
import imageio
import os

class Board:
    def __init__(self, size):
        self.grid = []
        self.size = size
        self._populate_grid(0.1)


    def _populate_grid(self, rate):
        self.grid = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                if random.random() > rate:
                    row.append(0)
                else:
                    row.append(1)
            self.grid.append(row)

    def print(self):
        for row in self.grid:
            print(row)

    def set_cell(self, x, y, value):
        self.grid[y][x] = value

    def get_cell(self, x, y):
        return self.grid[y][x]

    def count_neighbors(self, x, y):
        values = []

        left_pos = x-1
        if left_pos < 0:
            left_pos = self.size - 1
        right_pos = x+1
        if right_pos >= self.size:
            right_pos = 0
        up_pos = y-1
        if up_pos < 0:
            up_pos = self.size - 1
        down_pos = y+1
        if down_pos >= self.size:
            down_pos = 0

        values.append(self.get_cell(left_pos, up_pos))
        values.append(self.get_cell(x, up_pos))
        values.append(self.get_cell(right_pos, up_pos))
        values.append(self.get_cell(left_pos, y))
        values.append(self.get_cell(right_pos, y))
        values.append(self.get_cell(left_pos, down_pos))
        values.append(self.get_cell(x, down_pos))
        values.append(self.get_cell(right_pos, down_pos))

        return sum(values)

def display_board(board):
    img = Image.new(mode="RGBA", size=(board.size, board.size))
    pixels = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pixels[x, y] = ((round(board.get_cell(x, y) * 255)), (round(board.get_cell(x, y) * 255)), (round(board.get_cell(x, y) * 255)))

    return img

def format_subgrid_as_inputs(grid):
    inputs = []
    for row in grid:
        for col in row:
            inputs.append(col)

    return inputs


def run_network(id, board_size):
    attempts = 1
    scores = []
    for a in range(attempts):
        total_score = 0
        board = Board(board_size)
        next_board = Board(board_size)
        names = []
        iterations = 500
        for i in range(iterations):
            print(f"i = {iterations}")
            board.grid = next_board.grid
            next_board._populate_grid(0)
            name = f"frames/{id}_run_{a}_frame_{i}.png"
            display_board(board).save(name, "png")
            for y, row in enumerate(board.grid):
                for x, col in enumerate(row):
                    living_neighbors = board.count_neighbors(x, y)
                    state = board.get_cell(x, y)

                    next_state = 0
                    if state == 0:
                        if living_neighbors == 3:
                            next_state = 1
                    if state == 1:
                        if living_neighbors == 3 or living_neighbors == 2:
                            next_state = 1

                        if living_neighbors < 2:
                            next_state = 0
                        if living_neighbors > 3:
                            next_state = 0

                    next_board.set_cell(x, y, next_state)



            names.append(name)
            total_score += 1

        try:
            images = []
            for filename in names:
                images.append(imageio.imread(filename))
                # Add Score to Saved Image
            imageio.mimsave(f'results/0_0_0_{id}_binary_{a}.gif', images)
        except:
            print(f"Could not make gif for: {id}")
        scores.append(total_score)

    return sum(scores) / len(scores)

if __name__ == '__main__':
    run_network(23, 250)