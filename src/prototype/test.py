import random
import math
import matplotlib.pyplot as plt

u = []
for i in range(1000):
    u.append(random.random())
    u[i] = 200 - 200 * math.sqrt(1 - u[i])
    u[i] = round(u[i], 1)
u.sort()

fig, ax = plt.subplots()

ax.hist(u, bins=50)
plt.show()
