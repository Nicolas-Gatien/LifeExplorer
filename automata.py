import math
import random
from PIL import Image
import imageio

class Board:
    def __init__(self, size):
        self.grid = []
        self.size = size
        for y in range(size):
            row = []
            for x in range(size):
                row.append([round(random.random(), 1), round(random.random(), 1), round(random.random(), 1)])
            self.grid.append(row)

    def print(self):
        for row in self.grid:
            print(row)

    def set_cell(self, x, y, value):
        self.grid[y][x] = value

    def get_cell(self, x, y):
        return self.grid[y][x]

    def activate(self, value):
        if value < 0:
            return 0
        if value > 1:
            return 1
        return value

    def apply_kernel(self, kernel):
        for row_num, row in enumerate(self.grid):
            for col_num, col in enumerate(row):
                neighbors = self.get_subgrid(row_num, col_num, kernel.size)
                red = 0
                for x in range(len(kernel.grid)):
                    for y in range(len(kernel.grid)):
                        red += kernel.grid[x][y][0] * neighbors[x][y][0]

                average_red = red / (kernel.size * kernel.size)
                true_red = self.activate(average_red)
                green = 0
                for x in range(len(kernel.grid)):
                    for y in range(len(kernel.grid)):
                        green += kernel.grid[x][y][1] * neighbors[x][y][1]

                average_green = green / (kernel.size * kernel.size)
                true_green = self.activate(average_green)

                blue = 0
                for x in range(len(kernel.grid)):
                    for y in range(len(kernel.grid)):
                        blue += kernel.grid[x][y][2] * neighbors[x][y][2]

                average_blue = blue / (kernel.size * kernel.size)
                true_blue = self.activate(average_blue)
                self.set_cell(col_num, row_num, [true_red, true_green, true_blue])



    def get_subgrid(self, starting_row, starting_col, size):
        offset = math.floor(size/2)
        starting_row -= offset
        starting_col -= offset

        # Loop Around
        if starting_row < 0:
            starting_row = len(self.grid)-offset

        if starting_col < 0:
            starting_col = len(self.grid)-offset

        subgrid = []
        steps = 0
        i = starting_row
        while steps < size:
            if i >= len(self.grid):
                i = 0

            row = self.grid[i][starting_col:starting_col+size]
            # Loop Around
            leftover = starting_col+size - len(self.grid)
            if leftover > 0:
                remainder = self.grid[i][0:leftover]
                subgrid.append(row + remainder)
            else:
                subgrid.append(row)
            steps += 1
            i += 1

        return subgrid

def display_board(board):
    img = Image.new(mode="RGBA", size=(board.size, board.size))
    pixels = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pixels[x, y] = ((round(board.get_cell(x, y)[0] * 255)), (round(board.get_cell(x, y)[1] * 255)), (round(board.get_cell(x, y)[2] * 255)))

    return img

kernel = Board(3)
display_board(kernel).show()

kernel.grid = [
    [[3, 3, 0.1], [0.5,32, 0.5], [0.1, 3, 3]],
    [[3, 0.5, 0.1], [0.5, 0.5, 0.5], [0.1, 0.5, 3]],
    [[3, 0.1, 0.1], [0.5, 0.1, 0.5], [0.1, 0.1, 3]]]

attempts = 5
for a in range(attempts):
    board = Board(100)
    names = []
    iterations = 100
    for i in range(100):
        display_board(board).save(f"frames/frame_{i}.png", "png")
        names.append(f"frames/frame_{i}.png")
        board.apply_kernel(kernel)
        if i % 5 == 0:
            print(f"Iteration {i}/{iterations} Complete")

    print("Compiling GIF")
    images = []
    for filename in names:
        images.append(imageio.imread(filename))
    imageio.mimsave(f'frames_{a}.gif', images)
    print("Attempt 1 Complete")