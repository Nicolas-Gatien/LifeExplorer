import math
import random
from PIL import Image
import imageio
import neat

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
        difference = 0
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
                cell = self.get_cell(col_num, row_num)
                difference += abs((cell[0] - true_red) + (cell[1] - true_green) + (cell[2] - true_blue))
                self.set_cell(col_num, row_num, [true_red, true_green, true_blue])
        return difference

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

def run_network(net, id):
    kernel = Board(5)
    display_board(kernel).save(f"frames/{id}_kernel.png", "png")
    for i, row in enumerate(kernel.grid):
        for j, col in enumerate(row):
            for k, cha in enumerate(col):
                output = net.activate((i, j, k))
                kernel.grid[i][j][k] = output[0]

    attempts = 1
    scores = []
    for a in range(attempts):
        total_score = 0
        board = Board(25)
        names = []
        iterations = 50
        for i in range(iterations):
            name = f"frames/{id}_run_{a}_frame_{i}.png"
            display_board(board).save(name, "png")
            names.append(name)
            score = board.apply_kernel(kernel)
            total_score += score * iterations

            if score < 20 * iterations:
                total_score /= 2
            #if i % 5 == 0:
                #print(f"Iteration {i}/{iterations} Complete")

        #print("Compiling GIF")
        try:
            images = []
            for filename in names:
                images.append(imageio.imread(filename))
            imageio.mimsave(f'results/{id}_frames_{a}.gif', images)
            #print("Attempt 1 Complete")
        except:
            print(f"Could not make gif for: {id}")
        scores.append(total_score)

    return sum(scores) / len(scores)
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = run_network(net, genome_id)

import os
import neat

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 50)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    run_network(winner_net, "winner")
    p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)