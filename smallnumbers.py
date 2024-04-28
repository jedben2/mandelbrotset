# Small numbers package to handle small numbers
import numpy as np
import ray
@ray.remote
def f(x):
    return [i for i in range(x)], [i ** 2 for i in range(x)]

task = f.remote(4)
a = np.array(ray.get(f.remote(4)))
print(a)