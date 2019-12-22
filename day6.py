"""
https://adventofcode.com/2019/day/6
"""


from anytree import Node, RenderTree, search, AsciiStyle, LevelOrderIter, Walker
import logging


log = logging.getLogger(__name__)


class UniversalOrbitMap(object):
	@classmethod
	def from_orbits(cls, orbits):
		ret = UniversalOrbitMap()
		ret.nodes = {}
		for orbit in orbits:
			p1, p2 = orbit.split(")")
			if p1 not in ret.nodes:
				ret.nodes[p1] = Node(p1)
			if p2 == "YOU":
				ret.you = ret.nodes[p1]
				continue
			elif p2 == "SAN":
				ret.santa = ret.nodes[p1]
				continue
			elif p2 not in ret.nodes:
				ret.nodes[p2] = Node(p2, parent=ret.nodes[p1])
			else:
				if ret.nodes[p2].parent is None:
					ret.nodes[p2].parent = ret.nodes[p1]
				else:
					raise RuntimeError(
						"Parent mismatch for {}, cannot set to {} (previously {})".format(
							p2, p1, ret.nodes[p2].parent.name
						))
			if p1 == "COM":
				ret.orbits = ret.nodes[p1]
		if not ret.orbits:
			raise RuntimeError("No COM found")
		for node in ret.nodes:
			res = search.findall(ret.orbits, filter_=lambda n: n == node)
			if len(res) != 0:
				raise RuntimeError("Orphan node: {}".format(res))
		return ret

	def checksum(self):
		nodes = [n for n in LevelOrderIter(self.orbits)]
		ret = 0
		for node in nodes:
			sub = [n for n in LevelOrderIter(node)]
			if len(sub) != 1:
				log.debug(list(map(lambda n: n.name, sub)))
				ret += len(sub) - 1
		return ret

	def transfers(self, p1, p2):
		ret = []
		w = Walker()
		xup, xc, xdw = w.walk(p1, p2)
		ret.extend(xup)
		ret.append(xc)
		ret.extend(xdw)
		return ret

	def __str__(self):
		return RenderTree(self.orbits, style=AsciiStyle()).by_attr()


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	parser.add_argument("-c", "--checksum", default=False, action="store_true")
	parser.add_argument("-x", "--transfers", default=False, action="store_true")
	parser.add_argument("-s", "--show", default=False, action="store_true")
	parser.add_argument("-d", "--debug", default=False, action="store_true")
	args = parser.parse_args()
	if args.debug:
		logging.basicConfig(
			format="[%(levelname)s %(filename)s:(%(lineno)d)] %(message)s",
			level=logging.DEBUG,
			stream=sys.stdout
		)
	if args.path:
		with open(args.path, "r") as f:
			args.input = f.read()
	args.input = args.input.split("\n")
	uom = UniversalOrbitMap.from_orbits(args.input)
	if args.checksum:
		print("Checksum: {}".format(uom.checksum()))
	if args.transfers:
		xfr =  uom.transfers(uom.you, uom.santa)
		for idx in range(len(xfr) - 1):
			print("{} to {}".format(xfr[idx].name, xfr[idx + 1].name))
		print("Total Transfers: {}".format(len(xfr) - 1))
	if args.show:
		print(uom)


if __name__ == "__main__":
	import sys
	sys.exit(main())
