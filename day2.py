"""
https://adventofcode.com/2019/day/2
"""


import sys
import abc
import copy
import itertools
import logging


log = logging.getLogger(__name__)


class IntCodeOperation(abc.ABC):
	@abc.abstractclassmethod
	def opcode(cls):
		pass

	@abc.abstractclassmethod
	def eval(cls, state):
		pass

	@classmethod
	def getops(cls):
		for subclass in cls.__subclasses__():
			yield from subclass.getops()
			yield subclass


class AddOperation(IntCodeOperation):
	@classmethod
	def opcode(cls):
		return 1

	@classmethod
	def eval(cls, state):
		data, pos = state
		opcode, x, y, z = data[pos:pos+4]
		a = data[x]
		b = data[y]
		data[z] = a + b
		log.debug("data[{}] ({}) + data[{}] ({}) = data[{}] ({})".format(
			x, a, y, b, z, data[z]
		))
		return pos + 4


class MulOperation(IntCodeOperation):
	@classmethod
	def opcode(cls):
		return 2

	@classmethod
	def eval(cls, state):
		data, pos = state
		opcode, x, y, z = data[pos:pos+4]
		a = data[x]
		b = data[y]
		data[z] = a * b
		log.debug("data[{}] ({}) * data[{}] ({}) = data[{}] ({})".format(
			x, a, y, b, z, data[z]
		))
		return pos + 4


class EndOperation(IntCodeOperation):
	@classmethod
	def opcode(cls):
		return 99

	@classmethod
	def eval(cls, state):
		return len(state[0])


class IntCode(object):
	def __init__(self, state):
		self._state = state
		self._pos = 0
		self._ops = None
		log.debug("initial state: {}".format(self._state))

	@property
	def output(self):
		return self._state[0]

	@property
	def state(self):
		return self._state

	def nextop(self):
		if not self._ops:
			self._ops = dict([(op.opcode(), op) for op in IntCodeOperation.getops()])
		return self._ops[self._state[self._pos]]

	def step(self):
		op = self.nextop()
		log.debug("position: {}".format(self._pos))
		self._pos = op.eval((self._state, self._pos))
		
	def eval(self):
		while self._pos < len(self._state):
			self.step()
			log.debug("state: {}".format(self._state))


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	parser.add_argument("-f", "--fuzz", default=False, action="store_true")
	parser.add_argument("-n", "--noun", type=int)
	parser.add_argument("-v", "--verb", type=int)
	parser.add_argument("-t", "--target", type=int)
	parser.add_argument("-d", "--debug", default=False, action="store_true")
	args = parser.parse_args()
	if args.debug:
		logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	if args.path:
		with open(args.path, "r") as f:
			args.input = f.read()
	data = [x for x in map(int, args.input.strip().split(","))]
	if args.fuzz:
		found = False
		for n, v in itertools.product(range(100), repeat=2):
			d = copy.deepcopy(data)
			d[args.noun] = n
			d[args.verb] = v
			evaluator = IntCode(d)
			evaluator.eval()
			log.debug("noun: {}; verb: {}; output: {}".format(n, v, evaluator.output))
			if evaluator.output == args.target:
				print("noun: {}; verb: {}".format(n, v))
				found = True
				break
		if not found:
			return 1
	else:
		evaluator = IntCode(data)
		evaluator.eval()
		log.debug(",".join(map(str, evaluator.state())))
		print(evaluator.state[0])
	return 0


if __name__ == "__main__":
	sys.exit(main())
