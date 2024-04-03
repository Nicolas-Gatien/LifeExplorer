import math
import random
from PIL import Image
import imageio
import os
import neat

class Board:
    def __init__(self, size):
        self.grid = []
        self.size = size
        for y in range(size):
            row = []
            for x in range(size):
                if random.random() > 0.01:
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
            pixels[x, y] = ((round(board.get_cell(x, y) * 255)), (round(board.get_cell(x, y) * 255)), (round(board.get_cell(x, y) * 255)))

    return img

def format_subgrid_as_inputs(grid):
    inputs = []
    for row in grid:
        for col in row:
            inputs.append(col)

    return inputs


def run_network(net, id, board_size):
    attempts = 1
    scores = []
    for a in range(attempts):
        total_score = 0
        board = Board(board_size)
        names = []
        iterations = 100
        for i in range(iterations):
            name = f"frames/{id}_run_{a}_frame_{i}.png"
            display_board(board).save(name, "png")
            for y, row in enumerate(board.grid):
                for x, col in enumerate(row):
                    subgrid = board.get_subgrid(y, x, 3)
                    inputs = format_subgrid_as_inputs(subgrid)
                    output = net.activate(inputs)
                    if output[0] > 0.5:
                        output[0] = 1
                    else:
                        output[0] = 0
                    board.set_cell(x, y, output[0])


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

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = run_network(net, genome_id, 75) / 1000

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
    winner = p.run(eval_genomes, 100)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    run_network(winner_net, "winner", 1000)
    p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'conway-config-feedforward')
    run(config_path)