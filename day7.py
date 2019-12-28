"""
https://adventofcode.com/2019/day/7
"""


import abc
import copy
import time
import queue
import logging
import itertools
import multiprocessing
from collections import namedtuple, deque


log = logging.getLogger(__name__)


IntCodeArg = namedtuple("IntCodeArg", ("mode", "raw", "value"))


class IntCodeOperation(abc.ABC):
	@abc.abstractclassmethod
	def opcode(cls):
		pass

	@abc.abstractclassmethod
	def length(cls):
		pass

	@abc.abstractclassmethod
	def _eval(cls, data, pos, *args):
		pass

	@classmethod
	def eval(cls, state):
		data, pos = state
		opm = data[pos]
		#op = opm % 100
		f = (opm // 100) % 10
		s = (opm // 1000) % 10
		t = opm // 10000
		args = []
		for mode, arg in zip([f, s ,t], data[pos+1:pos+cls.length()]):
			if mode == 0: # position
				args.append(IntCodeArg(mode, arg, data[arg]))
			elif mode == 1: # immediate
				args.append(IntCodeArg(mode, arg, arg))
			else:
				raise RuntimeError("Invalid mode {} at {}".format(mode, pos))
		return cls._eval(data, pos, *args)

	@classmethod
	def getops(cls):
		for subclass in cls.__subclasses__():
			yield from subclass.getops()
			yield subclass


class OneIntCode(IntCodeOperation):
	@classmethod
	def length(cls):
		return 1


class TwoIntCode(IntCodeOperation):
	@classmethod
	def length(cls):
		return 2


class ThreeIntCode(IntCodeOperation):
	@classmethod
	def length(cls):
		return 3


class FourIntCode(IntCodeOperation):
	@classmethod
	def length(cls):
		return 4


class EndOperation(OneIntCode):
	@classmethod
	def opcode(cls):
		return 99

	@classmethod
	def _eval(cls, data, pos, *args):
		log.debug("HALT")
		return len(data)


class AddOperation(FourIntCode):
	@classmethod
	def opcode(cls):
		return 1

	@classmethod
	def _eval(cls, data, pos, *args):
		a, b, loc = args
		log.debug("ADD: data[{}] = {}({}) + {}({})".format(
			loc.raw,
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			b.value,
			"data[{}]".format(b.raw) if b.mode == 0 else "i"
		))
		data[loc.raw] = a.value + b.value
		return pos + cls.length()


class MulOperation(FourIntCode):
	@classmethod
	def opcode(cls):
		return 2

	@classmethod
	def _eval(cls, data, pos, *args):
		a, b, loc = args
		log.debug("MUL: data[{}] = {}({}) * {}({})".format(
			loc.raw,
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			b.value,
			"data[{}]".format(b.raw) if b.mode == 0 else "i"
		))
		data[loc.raw] = a.value * b.value
		return pos + cls.length()


class InOperation(TwoIntCode):
	@classmethod
	def opcode(cls):
		return 3

	@classmethod
	def _eval(cls, data, pos, *args):
		loc = args[0]
		raw = input("input: ")
		if raw:
			val = int(raw)
		else:
			val = 0
		log.debug("IN: data[{}] = {}(i)".format(loc.raw, val))
		data[loc.raw] = val
		return pos + cls.length()


class InQueueOperation(TwoIntCode):
	@classmethod
	def opcode(cls):
		return None

	@classmethod
	def _eval(cls, data, pos, *args):
		loc = args[0]
		raw = cls.inq.get()
		if raw:
			val = int(raw)
		else:
			val = 0
		log.debug("INQ: data[{}] = {}(i)".format(loc.raw, val))
		data[loc.raw] = val
		return pos + cls.length()


class OutOperation(TwoIntCode):
	@classmethod
	def opcode(cls):
		return 4

	@classmethod
	def _eval(cls, data, pos, *args):
		a = args[0]
		log.debug("OUT: {}({})".format(
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i"
		))
		if a.mode == 0:
			print(data[a.raw])
		else:
			print(a.value)
		return pos + cls.length()


class OutQueueOperation(TwoIntCode):
	outq = None
	@classmethod
	def opcode(cls):
		return None

	@classmethod
	def _eval(cls, data, pos, *args):
		a = args[0]
		log.debug("OUTQ: {}({})".format(
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i"
		))
		if a.mode == 0:
			cls.outq.put(data[a.raw])
		else:
			cls.outq.put(a.value)
		return pos + cls.length()


class JumpIfTrueOperation(ThreeIntCode):
	@classmethod
	def opcode(cls):
		return 5

	@classmethod
	def _eval(cls, data, pos, *args):
		a, jmp = args
		log.debug("JUMP IF TRUE: {}({}) != 0 ? IP += {}({})".format(
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			jmp.value if a.value != 0 else cls.length(),
			"data[{}]".format(jmp.raw) if jmp.mode == 0 and a.value != 0 else "i"
		))
		return jmp.value if a.value != 0 else pos + cls.length()


class JumpIfFalseOperation(ThreeIntCode):
	@classmethod
	def opcode(cls):
		return 6

	@classmethod
	def _eval(cls, data, pos, *args):
		a, jmp = args
		log.debug("JUMP IF FALSE: {}({}) == 0 ? IP += {}({})".format(
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			jmp.value if a.value == 0 else cls.length(),
			"data[{}]".format(jmp.raw) if jmp.mode == 0 and a.value == 0 else "i"
		))
		return jmp.value if a.value == 0 else pos + cls.length()


class LessThanOperation(FourIntCode):
	@classmethod
	def opcode(cls):
		return 7

	@classmethod
	def _eval(cls, data, pos, *args):
		a, b, loc = args
		log.debug("LESS THAN: data[{}] = {}({}) < {}({})".format(
			loc.raw,
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			b.value,
			"data[{}]".format(b.raw) if b.mode == 0 else "i"
		))
		data[loc.raw] = 1 if a.value < b.value else 0
		return pos + cls.length()


class EqualsOperation(FourIntCode):
	@classmethod
	def opcode(cls):
		return 8

	@classmethod
	def _eval(cls, data, pos, *args):
		a, b, loc = args
		log.debug("EQUALS: data[{}] = {}({}) == {}({})".format(
			loc.raw,
			a.value,
			"data[{}]".format(a.raw) if a.mode == 0 else "i",
			b.value,
			"data[{}]".format(b.raw) if b.mode == 0 else "i"
		))
		data[loc.raw] = 1 if a.value == b.value else 0
		return pos + cls.length()


class IntCode(object):
	def __init__(self, state, q=(None, None)):
		self._state = state
		self._pos = 0
		self._ops = None
		self._inst_buf = deque(maxlen=50)
		self._state_buf = deque(maxlen=50)
		self._inqueue = q[0]
		self._outqueue = q[1]

	@property
	def output(self):
		return self._state[0]

	@property
	def state(self):
		return self._state

	def nextop(self):
		if not self._ops:
			self._ops = dict([(op.opcode(), op) for op in IntCodeOperation.getops()])
		op = self._state[self._pos] % 100
		ret = self._ops[op]
		if self._inqueue is not None and ret is InOperation:
			ret = InQueueOperation
		elif self._outqueue is not None and ret is OutOperation:
			ret = OutQueueOperation
		return ret

	def step_forward(self):
		op = self.nextop()
		inst = self._state[self._pos:self._pos + op.length()]
		log.debug("IP: {}; INST {}: {}".format(self._pos, len(self._inst_buf), inst))
		self._inst_buf.append(inst)
		self._state_buf.append((copy.deepcopy(self._state), self._pos))
		if self._inqueue is not None:
			op.inq = self._inqueue
		if self._outqueue is not None:
			op.outq = self._outqueue
		self._pos = op.eval((self._state, self._pos))
		
	def step_backward(self):
		if len(self._state_buf) > 0:
			inst = self._inst_buf.pop()
			state, pos = self._state_buf.pop()
			self._pos = pos
			self._state = state
			log.debug("IP: {}; INST {}: {}".format(self._pos, len(self._inst_buf), inst))

	def eval(self):
		while self._pos < len(self._state):
			self.step_forward()

	def debug(self):
		step = True
		bps = []
		try:
			while self._pos < len(self._state):
				if step:
					d = input(">> ")
					if d.lower() == "n" or len(d) == 0:
						self.step_forward()
					elif d.lower() == "b":
						self.step_backward()
					elif d.lower() == "c":
						step = False
					elif d.lower().startswith("p"):
						data = d.split(" ")
						if len(data) == 1:
							print("state: {}".format(self._state))
						if len(data) == 2:
							idx = int(data[1])
							print("state[{}]: {}".format(idx, self._state[idx]))
						elif len(data) == 3:
							sidx = int(data[1])
							eidx = int(data[2])
							print("state[{}:{}]: {}".format(sidx, eidx, self._state[sidx:eidx]))
					elif d.lower().startswith("bp"):
						data = d.split(" ")
						if len(data) == 1:
							print("breakpoints: {}".format(bps))
						elif len(data) == 2:
							loc = int(d.split(" ")[1])
							if loc not in bps:
								bps.append(loc)
					else:
						print("please enter (n)ext, (b)ack, (c)ontinue, (p)rint, or (bp)reakpoint")
				else:
					self.step_forward()
					for bp in bps:
						if self._pos >= bp:
							step = True
							bps.remove(bp)
		except KeyboardInterrupt:
			pass


def amp_harness(data, q):
	evaluator = IntCode(data, q)
	evaluator.eval()


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	grp = parser.add_mutually_exclusive_group(required=True)
	grp.add_argument("-i", "--input")
	grp.add_argument("-p", "--path", type=str)
	parser.add_argument("-d", "--debug", default=False, action="store_true")
	parser.add_argument("-s", "--step", default=False, action="store_true")
	parser.add_argument("-a", "--amp", default=False, action="store_true")
	parser.add_argument("-e", "--phase", default="01234")
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
	data = list(map(int, args.input.strip().split(",")))
	if args.step:
		evaluator = IntCode(data)
		logging.basicConfig(
			format="[%(levelname)s %(filename)s:(%(lineno)d)] %(message)s",
			level=logging.DEBUG,
			stream=sys.stdout
		)
		evaluator.debug()
	elif args.amp:
		highest = [0, None]
		for inputs in itertools.permutations(args.phase, 5):
			n = 0
			log.debug(inputs)
			amps = []
			for l in "ABCDE":
				inq = multiprocessing.Queue()
				outq = multiprocessing.Queue()
				p = multiprocessing.Process(
					name="Amp {}".format(l),
					target=amp_harness,
					args=(copy.deepcopy(data), (inq, outq))
				)
				amps.append({ "proc": p, "inq": inq, "outq": outq })
				p.start()
			# initial run for inputting phase settings
			for idx, i in enumerate(inputs):
				log.debug("phase setting: {}; input signal: {}".format(i, n))
				amps[idx]["inq"].put(i)
				amps[idx]["inq"].put(n)
				n = amps[idx]["outq"].get()
				log.debug("output: {}".format(n))
			stop = False
			while not stop:
				for amp in amps:
					if not amp["proc"].is_alive():
						stop = True
						break
					log.debug("{} receives input signal {}".format(amp["proc"].name, n))
					amp["inq"].put(n, False)
					time.sleep(0.25)
					try:
						n = amp["outq"].get(1)
						log.debug("{} output: {}".format(amp["proc"].name, n))
					except queue.Empty:
						stop = True
						break
			if n > highest[0]:
				log.debug("new highest: {}, inputs: {}".format(n, inputs))
				highest = [n, inputs]
		print("highest: {}, inputs: {}".format(highest[0], highest[1]))
	else:
		evaluator = IntCode(data)
		evaluator.eval()
	return 0


if __name__ == "__main__":
	import sys
	sys.exit(main())
