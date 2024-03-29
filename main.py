import numpy as np
import random
import matplotlib.pyplot as plt

arr = np.zeros((100, 100))

def add_random(x):
    return x + round(random.random(), 2)

def add(x):
    return x + 0.1

vectorize_add_random = np.vectorize(add_random)

new_array = vectorize_add_random(arr)

plt.imshow(new_array, cmap='Grays', interpolation='nearest')
plt.show()

print(new_array)