"""
https://adventofcode.com/2019/day/8
"""


import copy
import logging


log = logging.getLogger(__name__)


def chunk(l, n):
	for x in range(0, len(l), n):
		yield l[x:x+n]


def checksum(layers, height, width):
	zcount = height * width
	l = None
	for idx, layer in enumerate(layers):
		cnt = layer.count(0)
		if cnt < zcount:
			zcount = cnt
			l = idx
	log.debug("layer with fewest 0s: {}".format(l))
	ones = layers[l].count(1)
	twos = layers[l].count(2)
	return ones * twos


def flatten(layers):
	ret = copy.deepcopy(layers[0])
	for layer in layers:
		log.debug("layer data: {}".format(layer))
		for idx in range(len(ret)):
			if ret[idx] == 2:
				log.debug("replacing ret[{}] with {}".format(idx, layer[idx]))
				ret[idx] = layer[idx]
		log.debug("current image: {}".format(ret))
	return ret


def draw(data, height, width):
	ret = ""
	img = list(chunk(data, width))
	for row in img:
		for pixel in row:
			if pixel == 0:
				ret += " "
			elif pixel == 1:
				ret += "W"
			elif pixel == 2:
				ret += " "
			ret += " "
		ret += "\n"
	return ret


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	parser.add_argument("-d", "--debug", default=False, action="store_true")
	parser.add_argument("-c", "--checksum", default=False, action="store_true")
	parser.add_argument("-w", "--width", type=int, required=True)
	parser.add_argument("-t", "--height", type=int, required=True)
	
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
	data = list(map(int, args.input.strip()))
	layers = list(chunk(data, args.height * args.width))
	for idx, layer in enumerate(layers):
		l = chunk(layer, args.width)
		log.debug("Layer {}:\n{}".format(idx + 1, "\n".join(["".join([str(x) for x in row]) for row in l])))
	if args.checksum:
		print(checksum(layers, args.height, args.width))
	else:
		flat = flatten(layers)
		print(draw(flat, args.height, args.width))

if __name__ == "__main__":
	import sys
	sys.exit(main())
