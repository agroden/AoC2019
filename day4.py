"""
https://adventofcode.com/2019/day/4
"""




def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	args = parser.parse_args()
	dups = ["00", "11", "22", "33", "44", "55", "66", "77", "88", "99"]
	candidates = []
	pmin, pmax = map(int, args.input.split("-"))
	for p in range(pmin, pmax): # must be in given range
		sp = str(p)
		if len(sp) != 6: # must be 6 digit number
			continue
		d = [x for x in dups if x in sp]
		if not d: # must have 2 adjacent duplicate digits
			continue
		valid = False
		for x in d: # part 2 - adjacent duplicates cannot be part of larger runs
			idx = sp.find(x)
			if idx != len(sp) - 2 and sp[idx+2] == x[0]:
				continue
			valid = True
		if not valid:
			continue
		if p != int(''.join(sorted([x for x in sp]))): 
			continue
		candidates.append(p)
	print(len(candidates))


if __name__ == "__main__":
	import sys
	sys.exit(main())
