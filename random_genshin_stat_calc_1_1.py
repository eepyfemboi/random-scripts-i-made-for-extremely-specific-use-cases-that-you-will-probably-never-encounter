import random

base_mats = 300
chances = int(base_mats / 3)

def percent(percentage: int, number: int):
    return ((number / 100) * percentage)

def sim(percent_win: int) -> int:
    times_won = 0
    end = int(100 / percent_win)
    for i in range(chances):
        if random.randint(1, end) == 1:
            times_won += 1
    return times_won

print(f"Base materials used (for reference): {base_mats}")
print(f"The values provided are the total extra base materials produced from the given stat")
print(f"Statistical results:")
print(f"10% chance for 3 extra of the base: {int(percent(10, chances) * 3)}")
print(f"25% chance for 1 extra of the base: {int(percent(25, chances))}")
print(f"Simulated results:")
print(f"10% chance for 3 extra of the base: {int(sim(10) * 3)}")
print(f"25% chance for 1 extra of the base: {sim(25)}")
