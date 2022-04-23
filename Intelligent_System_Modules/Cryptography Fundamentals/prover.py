import random
x, g, p = map(int, input("").split(' '))
r = random.randint(1, 9999)
C = (g ** r) % p
print(f"{C}")
e = int(input(""))
t = e*x + r
print(f"{t}")
