import random
# y = g**x % p
C, y, g, p = map(int, input("").split(' '))
e = random.randint(1, 9999)
print(f"{e}")
t = int(input(""))
if (g**t)%p == (y**e*C)%p:
    print("1")
else:
    print("0")