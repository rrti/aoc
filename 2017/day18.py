## NB: day23 code only uses {set,sub,mul,jnz}
OP_CODES = {
	"snd": 0,
	"rcv": 1,
	"set": 2,
	"add": 3,
	"sub": 4,
	"mul": 5,
	"mod": 6,
	"jgz": 7,
	"jnz": 8,
}

REG_NAMES = {chr(ord('a') + c): c for c in xrange(26)}
REG_NAMES['$'] = True ## program-counter
REG_NAMES['~'] = True ## sndr-history (day 18, part 1)
REG_NAMES['*'] = True ## mult-counter (day 23, part 1)
REG_NAMES['{'] = True ## recv-counter
REG_NAMES['}'] = True ## send-counter (day 18, part 2)

TEST_INSTRS = [
	"set a 1",
	"add a 2",
	"mul a a",
	"mod a 5",
	"snd a",
	"set a 0",
	"rcv a",
	"jgz a -1",
	"set a 1",
	"jgz a -2",
]

REAL_INSTRS_DBG = [
	"snd 1",
	"snd 2",
	"snd p",
	"rcv a",
	"rcv b",
	"rcv c",
	"rcv d",
]


def parse_input(fn):
	with open(fn, 'r') as f:
		return (f.readlines())


class program:
	## NB:
	##   test-flag argument is only relevant for day23.in
	##   day18.in overwrites the a-register, so assigning
	##   it a value here is harmless
	def __init__(self, code, program_id, recv_mode, test_flag):
		self.code = code[:]
		self.regs = {'p': program_id, 'a': test_flag}

		self.sbuf = []
		self.rbuf = []

		for i in xrange(len(code)):
			self.code[i] = self.code[i].strip("\n")
			self.code[i] = self.code[i].split()

			if (len(self.code[i]) < 3):
				self.code[i].append(None)

			## save a few lookups
			self.code[i][0] = OP_CODES[ self.code[i][0] ]

		self.ops = [None] * len(OP_CODES)
		self.ops[ OP_CODES["snd"] ] = self.sndr
		self.ops[ OP_CODES["set"] ] = self.setr
		self.ops[ OP_CODES["add"] ] = self.addr
		self.ops[ OP_CODES["sub"] ] = self.subr
		self.ops[ OP_CODES["mul"] ] = self.mulr
		self.ops[ OP_CODES["mod"] ] = self.modr
		self.ops[ OP_CODES["jgz"] ] = self.jgzr
		self.ops[ OP_CODES["jnz"] ] = self.jnzr

		if (recv_mode == 0):
			self.ops[ OP_CODES["rcv"] ] = self.rcvr0
		else:
			self.ops[ OP_CODES["rcv"] ] = self.rcvr1

	def valid_pctr(self, pctr): return (pctr >= 0 and pctr < len(self.code))
	def has_exited(self): return (not self.valid_pctr(self.load_val('$')))

	def cond_jump(self, jump, mask): self.store_val('$', self.load_val('$') + jump * mask)
	def next_instr(self): self.store_val('$', self.load_val('$') + 1)

	def store_val(self, reg, val):
		assert(reg in REG_NAMES)
		self.regs[reg] = val
	def load_val(self, op):
		if (op in REG_NAMES):
			return (self.regs.get(op, 0))

		return (int(op))

	## main opcode-handlers; jumps are relative
	def setr(self, lop, rop):
		self.store_val(lop,                      self.load_val(rop))
		self.next_instr()
		return 1
	def addr(self, lop, rop):
		self.store_val(lop, self.load_val(lop) + self.load_val(rop))
		self.next_instr()
		return 1
	def subr(self, lop, rop):
		self.store_val(lop, self.load_val(lop) - self.load_val(rop))
		self.next_instr()
		return 1
	def mulr(self, lop, rop):
		self.store_val(lop, self.load_val(lop) * self.load_val(rop))
		self.store_val('*', self.load_val('*') + 1)
		self.next_instr()
		return 1
	def modr(self, lop, rop):
		self.store_val(lop, self.load_val(lop) % self.load_val(rop))
		self.next_instr()
		return 1
	def jgzr(self, lop, rop):
		self.cond_jump(self.load_val(rop) - 1, self.load_val(lop) > 0)
		self.next_instr()
		return 1
	def jnzr(self, lop, rop):
		self.cond_jump(self.load_val(rop) - 1, self.load_val(lop) != 0)
		self.next_instr()
		return 1


	def sndr(self, lop, rop):
		self.store_val('~', self.load_val(lop))
		self.store_val('}', self.load_val('}') + 1)
		self.sbuf.append(self.load_val(lop))
		self.next_instr()
		return 1

	## mode 0; stops at the first rcv instruction for
	## which the LHS register operand is greater than
	## zero
	def rcvr0(self, lop, rop):
		val = self.load_val(lop)
		ret = (val <= 0) * 2 - 1

		self.cond_jump(max(0, ret), 1)
		return ret

	def rcvr1(self, lop, rop):
		self.store_val('{', self.load_val('{') + 1)
		self.cond_jump(1, len(self.rbuf) > 0)

		if (len(self.rbuf) == 0):
			return -1

		self.regs[lop] = self.rbuf[0]
		self.rbuf = self.rbuf[1: ]
		return 1


	def exec_instr(self, cycle):
		ins = self.code[self.load_val('$')]
		opc = ins[0]
		lop = ins[1]
		rop = ins[2]

		return (self.ops[opc](lop, rop))

	def send_buffer(self, prog):
		self.sbuf.reverse()

		while (len(self.sbuf) > 0):
			prog.rbuf.append(self.sbuf.pop())




def exec_progs(progs, cycle):
	exit_ctr = 0
	rval_sum = 0

	## interleave execution; this way send-buffer
	## will only ever contain at most one element
	## (for part 2)
	for i in xrange(len(progs)):
		j = (i + 1) % len(progs)

		pi = progs[i]
		pj = progs[j]

		if (pi.has_exited()):
			exit_ctr += 1
			continue

		rval_sum += pi.exec_instr(cycle)

		## transmit data from pi to pj or to itself
		pi.send_buffer(pj)

	return (exit_ctr == len(progs) or rval_sum == -len(progs))


## params := (num_programs, output_idx, recv_mode, test_flag, output_reg)
def run_progs(instrs, params):
	cycle = 0

	progs = [program(instrs, i, params[2], params[3]) for i in xrange(params[0])]

	while (not exec_progs(progs, cycle)):
		cycle += 1

	return (progs[ params[1] ].load_val(params[4]))


assert(run_progs(parse_input("day18.in"), (1, 0, 0, -1, '~')) == 8600)
assert(run_progs(parse_input("day18.in"), (2, 1, 1, -1, '}')) == 7239)

