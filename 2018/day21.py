from collections import defaultdict as ddict
from re import search as re_search
from sys import stdin
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
	def run_native(magic):
		def calc_round_value(r5_round, r5_magic):
			r4 = r5_round | 65536
			r5 = r5_magic

			## for second part we want the "lowest non-negative integer value
			## for register 0 that causes the program to halt after executing
			## the most instructions", i.e. the last value reached before cycle
			## restarts
			while (r4 != 0):
				r5 += (r4 & 255)
				r5 &= 16777215
				r5 *= 65899
				r5 &= 16777215
				r4 >>= 8

			return r5

		def calc_round_values(r0, r5_magic):
			cur_iter = 1
			r5_part2 = 0
			r5_part1 = calc_round_value(r5_part2, r5_magic)
			r5_round = r5_part1

			r5_cache = dict([(r5_round, cur_iter)])

			## program first compares against r0 after performing one round
			while (r0 != r5_round):
				r5_round = calc_round_value(r5_round, r5_magic)
				cur_iter += 1

				if (r5_round in r5_cache):
					print("[dbg] cycle-value %d->%d detected after %d rounds" % (r5_part2, r5_round, cur_iter))
					break

				r5_part2 = r5_round
				r5_cache[r5_round] = cur_iter

			return (r5_part1, r5_part2)

		## terminates when magic is 13284195, otherwise loops forever
		return (calc_round_values(0, magic))

	"""
	#ip 1                                           bind $ip to r1

	00  seti 123 0 5        // r5 = 123             -
	01  bani 5 456 5        // r5 = r5 & 456        r5 becomes 72
	02  eqri 5 72 5         // r5 = (r5 == 72)      r5 becomes 1 if bani works
	03  addr 5 1 1          // r1 = r5 + r1         r1 becomes r1 + 1 (skip to instr 04)
	04  seti 0 0 1          // r1 = 0               goto instr 00 (+1 on ret; loop forever if bani is broken)

	// setup for first iteration of outer loop
	05  seti 0 3 5          // r5 = 0               -
	06  bori 5 65536 4      // r4 = r5 | 65536      r4 becomes 65536 (r5 is 0)

	// outer loop start
	07  seti 13284195 4 5   // r5 = 13284195        r5 becomes weird magic number
	08  bani 4 255 3        // r3 = r4 & 255        r3 becomes 0,0,... (1st iter r4=65536, 2nd iter r4=256,...)
	09  addr 5 3 5          // r5 = r5 + r3         r5 remains unchanged (1st iter r3=0, 2nd iter r3=0)
	10  bani 5 16777215 5   // r5 = r5 & 16777215   r5 remains unchanged (1st iter r5=13284195, 2nd iter r5=13589857)
	11  muli 5 65899 5      // r5 = r5 * 65899      r5 becomes 875415166305,895557986443,...
	12  bani 5 16777215 5   // r5 = r5 & 16777215   r5 becomes 13589857,6973579,...
	13  gtir 256 4 3        // r3 = (256 > r4)      r3 becomes 0,0,... (256 > 65536 false, 256 > 256 false,...)
	14  addr 3 1 1          // r1 = r3 + r1         r1 becomes 14+0, 14+0, ... (no change to $ip)
	15  addi 1 1 1          // r1 = r1 + 1          r1 becomes 15+1; return also adds 1 so next instr is 17
	16  seti 27 1 1         // r1 = 27              goto instr 27 (+1 on ret)

	// inner loop start (calculates r4 >> 8)
	17  seti 0 5 3          // r3 = 0               r3 becomes 0
	18  addi 3 1 2          // r2 = r3 + 1          r2 becomes {1,2,3,...,255,256}, {1,2,3,...}
	19  muli 2 256 2        // r2 = r2 * 256        r2 becomes 256,512,768,...,65536,65792
	20  gtrr 2 4 2          // r2 = (r2 > r4)       r2 becomes 0,0,0,...,0,1
	21  addr 2 1 1          // r1 = r2 + r1         r1 becomes 20+0 (+1 on ret; $ip jumps to 22 until iter 256, then to 23)
	22  addi 1 1 1          // r1 = r1 + 1          r1 becomes 21+1; return also adds 1 so next instr is 24
	23  seti 25 2 1         // r1 = 25              goto instr 25 (+1 on ret, $ip jumps to 26)
	24  addi 3 1 3          // r3 = r3 + 1          r3 becomes 1,2,3,...,255,256
	25  seti 17 1 1         // r1 = 17              goto instr 17 (+1 on ret; loop until r2 > 65536)     ends after #ops=1803 with regs=[7290500, 19, 65536, 255, 65536, 13589857] ip=20 opc=gtrr

	26  setr 3 7 4          // r4 = r3              copy 256,... into r4
	27  seti 7 3 1          // r1 = 7               goto instr 7 (+1 on ret)

	28  eqrr 5 0 3          // r3 = (r5 == r0)      compare against user-set value
	29  addr 3 1 1          // r1 = r3 + r1         advance $ip one extra instr if r3 is 1
	30  seti 5 3 1          // r1 = 5               back to outer loop preamble
	"""
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
	vm_regs = [0, 0, 0, 0, 0, 0]

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

	def run_vm(code, regs, ip_reg = 0, ip_val = 0):
		assert(ip_reg < len(regs))

		op_cnt = 0
		cur_ip = ip_val

		r5_part1 = 0
		r5_part2 = 0

		r5_cache = {}

		def exec_opc(opc, a, b, c):
			regs[ip_reg] = cur_ip
			opc(regs, a, b, c)
			return (regs[ip_reg] + 1)

		while (cur_ip >= 0 and cur_ip < len(code)):
			if (False):
				## enable single-step debugging
				print("[dbg] #ops=%d regs=%s ip=%d opc=%s(a=%d,b=%d,c=%d)" % (op_cnt, regs, cur_ip, code[cur_ip][0].func_name, code[cur_ip][1], code[cur_ip][2], code[cur_ip][3]))
				while (stdin.readline() != "\n"):
					pass

			## save r5 when program first compares it to r0 for part 1
			if (cur_ip == 28):
				r5_part1 = (regs[5] * (r5_part1 == 0)) + (r5_part1 * (r5_part1 != 0))

				if (regs[5] in r5_cache):
					break

				r5_part2 = regs[5]
				r5_cache[r5_part2] = op_cnt

			vm_ins = code[cur_ip]
			cur_ip = exec_opc(vm_ins[0], vm_ins[1], vm_ins[2], vm_ins[3])
			op_cnt += 1

		return (r5_part1, r5_part2)

	## painfully slow for part 2
	## return (run_vm(vm_code, vm_regs, int(instrs[0][0].group(1))))
	return (run_native(13284195))

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), (7224964, 13813247))

