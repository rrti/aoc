from collections import defaultdict as ddict
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		rexprs = ("#ip\s*([0-9]+)", "([a-z]+)\s*([0-9]+)\s*([0-9]+)\s*([0-9]+)")
		instrs = []

		for line in f.readlines():
			instrs.append((re_search(rexprs[0], line), re_search(rexprs[1], line)))

		return instrs

	return []

def handle_input(instrs):
	def addr(regs, a, b, c): regs[c] = regs[a] + regs[b]
	def addi(regs, a, b, c): regs[c] = regs[a] +      b 

	def mulr(regs, a, b, c): regs[c] = regs[a] * regs[b]
	def muli(regs, a, b, c): regs[c] = regs[a] *      b 

	def banr(regs, a, b, c): regs[c] = regs[a] & regs[b]
	def bani(regs, a, b, c): regs[c] = regs[a] &      b 

	def borr(regs, a, b, c): regs[c] = regs[a] | regs[b]
	def bori(regs, a, b, c): regs[c] = regs[a] |      b 

	def setr(regs, a, b, c): regs[c] = regs[a]          
	def seti(regs, a, b, c): regs[c] =      a           

	def gtir(regs, a, b, c): regs[c] = int(     a  >  regs[b])
	def gtri(regs, a, b, c): regs[c] = int(regs[a] >       b )
	def gtrr(regs, a, b, c): regs[c] = int(regs[a] >  regs[b])

	def eqir(regs, a, b, c): regs[c] = int(     a  == regs[b])
	def eqri(regs, a, b, c): regs[c] = int(regs[a] ==      b )
	def eqrr(regs, a, b, c): regs[c] = int(regs[a] == regs[b])


	## opcode order as derived in day16
	opcodes = [gtri, bani, eqrr, gtir, eqir, bori, seti, setr, addr, borr, muli, banr, addi, eqri, mulr, gtrr]
	optable = dict([(f.func_name, f) for f in opcodes])
	vm_code = [None] * (len(instrs) - 1)
	vm_regs = ([0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0])

	## parse instructions
	for i in xrange(len(instrs)):
		instr = instrs[i]

		if (instr[0] != None):
			assert(instr[1] == None)
			assert(i == 0)
			continue

		assert(instr[0] == None)
		assert(i > 0)

		vm_code[i - 1] = (optable[instr[1].group(1)], int(instr[1].group(2)), int(instr[1].group(3)), int(instr[1].group(4)))


	def calc_factor_sum(N):
		res = 0

		for i in xrange(1, N + 1):
			res += ((((N / i) * i) == N) * i)

		return res

	def calc_factors(N):
		factors = []

		for i in xrange(1, N + 1):
			if ((N % i) == 0):
				factors.append(i)

		return factors


	def run_vm(code, regs, ip_reg = 0, ip_val = 0):
		assert(ip_reg < len(regs))
		print("[dbg] #code=%d ip_reg=%d" % (len(code), ip_reg))

		cur_ip = ip_val
		reg_01 = regs[: 2]

		ip_map = ddict(lambda: -1)

		def exec_opc(opc, a, b, c):
			regs[ip_reg] = cur_ip
			opc(regs, a, b, c)
			return (regs[ip_reg] + 1)

		## step VM until IP enters a loop, then extract regs[2] (N)
		while (cur_ip >= 0 and cur_ip < len(code)):
			vm_ins = code[cur_ip]
			cur_ip = exec_opc(vm_ins[0], vm_ins[1], vm_ins[2], vm_ins[3])

			## dump state when register 0 changes
			## if (regs[0] != reg_01[0]):
			##	reg_01 = regs[: 2]
			##
			## in.test binds ip to register 0
			if (ip_reg != 0 and ip_map[cur_ip] > 0):
				break

			ip_map[cur_ip] += 1

		if (ip_reg == 0):
			return regs[0]

		return (calc_factor_sum(regs[2]))


	## regs[2] is called N; starts at 976 for part 1 and 10551376 for part 2
	## regs[1] increases from 1 to N, regs[3] increases to N * regs[1] (N^2)
	##
	## if N is not a prime number, regs[1] contains factors of N
	## if N is a prime number, regs[1] only ever contains 1 and N
	## regs[0] contains the running sum of all factors found
	##
	part1 = run_vm(vm_code, vm_regs[0], int(instrs[0][0].group(1)))
	part2 = run_vm(vm_code, vm_regs[1], int(instrs[0][0].group(1)))

	return (part1, part2)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (   6,        6))
run(parse_input(__file__[: -2] + "in"     ), (1922, 22302144))

