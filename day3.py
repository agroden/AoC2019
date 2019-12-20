"""
https://adventofcode.com/2019/day/3
"""

import sys
import logging
from collections import UserDict
from uuid import uuid4
from urllib import request

log = logging.getLogger(__name__)


def manhattan_distance(p1, p2):
	return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


class Point(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __getitem__(self, key):
		if key > 1 or key < 0:
			raise IndexError(key)
		if key == 0:
			return self.x
		elif key == 1:
			return self.y

	def __setitem__(self, key, value):
		if key > 1 or key < 0:
			raise IndexError(key)
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value

	def as_tuple(self):
		return (self.x, self.y)

	def __str__(self):
		return "({}, {})".format(self.x, self.y)


class SparseGraph(UserDict):
	def __init__(self, dims=2):
		super().__init__()
		if dims <= 0:
			raise ValueError("dimensions must be higher than 0")
		self._dims = dims

	def __getitem__(self, key):
		#print("[get] dims: {}, key: {}".format(self._dims, key))
		#if self._dims <= 1:
			#	raise IndexError("exceeded graph dimensions")
		if key not in self.data and self._dims > 1:
			self.data[key] = SparseGraph(dims=self._dims - 1)
		return self.data[key]

	def __setitem__(self, key, value):
		#print("[set] dims: {}, key: {}, value: {}".format(self._dims, key, value))
		super().__setitem__(key, value)


class WireGrid(object):
	def __init__(self):
		self._grid = SparseGraph()
		self._wires = []
		self._intersections = []

	def add_wire(self, wire):
		def draw(pos, sym, wid, steps):
			csym, cid, csteps = self._grid.get(pos.x).get(pos.y, ["", None, 0])
			if csym in ["-", "|", "+"] and cid != wid:
				#print("intersection detected at {} (s1: {}; s2: {})".format(pos, csteps, steps))
				self._intersections.append(pos.as_tuple())
				self._grid[pos.x][pos.y] = ("X", [cid, wid], steps + csteps)
			elif csym == "X":
				self._intersections.append(pos.as_tuple())
				self._grid[pos.x][pos.y] = ("X", cid.append(wid), steps + csteps)
			else:
				self._grid[pos.x][pos.y] = (sym, wid, steps)
				#print((sym, wid, steps))

		wid = uuid4()
		self._wires.append((wid, wire))
		pos = Point(0, 0)
		draw(pos, "o", None, 0)
		instructions = wire.split(",")
		steps = 1
		for idx, inst in enumerate(instructions):
			direction = inst[0]
			length = int(inst[1:])
			sym = "-" if direction in ["R", "L"] else "|"
			if direction == "R":
				for x in range(length):
					if x == length - 1 and idx != len(instructions) - 1:
						sym = "+"
					pos.x += 1
					draw(pos, sym, wid, steps)
					steps += 1
			elif direction == "L":
				for x in range(length):
					if x == length - 1 and idx != len(instructions) - 1:
						sym = "+"
					pos.x -= 1
					draw(pos, sym, wid, steps)
					steps += 1
			elif direction == "U":
				for y in range(length):
					if y == length - 1 and idx != len(instructions) - 1:
						sym = "+"
					pos.y += 1
					draw(pos, sym, wid, steps)
					steps += 1
			elif direction == "D":
				for y in range(length):
					if y == length - 1 and idx != len(instructions) - 1:
						sym = "+"
					pos.y -= 1
					draw(pos, sym, wid, steps)
					steps += 1

	def add_wires(self, wires):
		for w in wires:
			self.add_wire(w)


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	parser.add_argument("-m", "--manhattan-distance", default=False, action="store_true")
	parser.add_argument("-s", "--signal-delay", default=False, action="store_true")
	args = parser.parse_args()
	if args.path:
		with open(args.path, "r") as f:
			args.input = f.read()
	args.input = args.input.strip().split("\n")
	grid = WireGrid()
	grid.add_wires(args.input)
	if args.manhattan_distance:
		closest = None
		for p in grid._intersections:
			dist = manhattan_distance((0,0), p)
			if closest is None or dist < closest:
				closest = dist
		print(closest)
	if args.signal_delay:
		min_steps = None
		for p in grid._intersections:
			_, wids, steps = grid._grid[p[0]][p[1]]
			if min_steps is None or steps < min_steps:
				min_steps = steps
		print(min_steps)


if __name__ == "__main__":
	sys.exit(main())
