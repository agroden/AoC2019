"""
PART 1
------
The Elves quickly load you into a spacecraft and prepare to launch.

At the first Go / No Go poll, every Elf is Go until the Fuel Counter-Upper. They haven't determined the amount of fuel required yet.

Fuel required to launch a given module is based on its mass. Specifically, to find the fuel required for a module, take its mass, divide by three, round down, and subtract 2.

For example:

    For a mass of 12, divide by 3 and round down to get 4, then subtract 2 to get 2.
    For a mass of 14, dividing by 3 and rounding down still yields 4, so the fuel required is also 2.
    For a mass of 1969, the fuel required is 654.
    For a mass of 100756, the fuel required is 33583.

The Fuel Counter-Upper needs to know the total fuel requirement. To find it, individually calculate the fuel needed for the mass of each module (your puzzle input), then add together all the fuel values.

What is the sum of the fuel requirements for all of the modules on your spacecraft?

PART 2
------
During the second Go / No Go poll, the Elf in charge of the Rocket Equation Double-Checker stops the launch sequence. Apparently, you forgot to include additional fuel for the fuel you just added.

Fuel itself requires fuel just like a module - take its mass, divide by three, round down, and subtract 2. However, that fuel also requires fuel, and that fuel requires fuel, and so on. Any mass that would require negative fuel should instead be treated as if it requires zero fuel; the remaining mass, if any, is instead handled by wishing really hard, which has no mass and is outside the scope of this calculation.

So, for each module mass, calculate its fuel and add it to the total. Then, treat the fuel amount you just calculated as the input mass and repeat the process, continuing until a fuel requirement is zero or negative. For example:

    A module of mass 14 requires 2 fuel. This fuel requires no further fuel (2 divided by 3 and rounded down is 0, which would call for a negative fuel), so the total fuel required is still just 2.
    At first, a module of mass 1969 requires 654 fuel. Then, this fuel requires 216 more fuel (654 / 3 - 2). 216 then requires 70 more fuel, which requires 21 fuel, which requires 5 fuel, which requires no further fuel. So, the total fuel required for a module of mass 1969 is 654 + 216 + 70 + 21 + 5 = 966.
    The fuel required by a module of mass 100756 and its fuel is: 33583 + 11192 + 3728 + 1240 + 411 + 135 + 43 + 12 + 2 = 50346.

What is the sum of the fuel requirements for all of the modules on your spacecraft when also taking into account the mass of the added fuel? (Calculate the fuel requirements for each module separately, then add them all up at the end.)
"""


import sys
import math


def calculate_fuel(mass):
	ret = math.floor(mass / 3) - 2
	if ret < 0:
		ret = 0
	return ret


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-m", "--mass", nargs="+", type=int)
	grp.add_argument("-f", "--file", type=str)
	parser.add_argument("-a", "--add-fuel", default=False, action="store_true")
	args = parser.parse_args()
	if args.file:
		args.mass = []
		with open(args.file, "r") as f:
			lines = f.readlines()
		for line in lines:
			line = line.strip()
			if len(line) > 0:
				args.mass.append(int(line.strip()))
	total = 0
	for m in args.mass:
		m_fuel = calculate_fuel(m)
		total += m_fuel
		if args.add_fuel:
			while m_fuel != 0:
				m_fuel = calculate_fuel(m_fuel)
				total += m_fuel
	print(total)
	return 0


if __name__ == "__main__":
	sys.exit(main())
