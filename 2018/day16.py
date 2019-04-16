from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		samples = []
		instrs = []

		cur_index = 0
		max_index = 0

		## opcode-sample lines
		while (cur_index < len(lines)):
			if (lines[cur_index].find("Before") == 0):
				regs_pre  = re_search(r"Before:\s*\[([0-9]+),\s*([0-9]+),\s*([0-9]+),\s*([0-9]+)\]", lines[cur_index + 0][: -1])
				regs_post = re_search(r"After:\s*\[([0-9]+),\s*([0-9]+),\s*([0-9]+),\s*([0-9]+)\]", lines[cur_index + 2][:-1])
				opc_instr = re_search(r"([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)", lines[cur_index + 1][: -1])

				samples.append((opc_instr, regs_pre, regs_post))

				max_index = cur_index + 2 + 1
				cur_index += 3
			else:
				cur_index += 1

		## test-program lines
		while (max_index < len(lines)):
			opc_instr = re_search(r"([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)", lines[max_index][: -1])

			if (opc_instr != None):
				instrs.append(opc_instr)

			max_index += 1

		return (samples, instrs)

	return ([], [])

def handle_input((samples, instrs)):
	## opcodes; c is always a register
	def addr(regs, a, b, c): regs[c] = regs[a] + regs[b]; return regs
	def addi(regs, a, b, c): regs[c] = regs[a] +      b ; return regs

	def mulr(regs, a, b, c): regs[c] = regs[a] * regs[b]; return regs
	def muli(regs, a, b, c): regs[c] = regs[a] *      b ; return regs

	def banr(regs, a, b, c): regs[c] = regs[a] & regs[b]; return regs
	def bani(regs, a, b, c): regs[c] = regs[a] &      b ; return regs

	def borr(regs, a, b, c): regs[c] = regs[a] | regs[b]; return regs
	def bori(regs, a, b, c): regs[c] = regs[a] |      b ; return regs

	def setr(regs, a, b, c): regs[c] = regs[a]          ; return regs
	def seti(regs, a, b, c): regs[c] =      a           ; return regs

	def gtir(regs, a, b, c): regs[c] = int(     a  >  regs[b]); return regs
	def gtri(regs, a, b, c): regs[c] = int(regs[a] >       b ); return regs
	def gtrr(regs, a, b, c): regs[c] = int(regs[a] >  regs[b]); return regs

	def eqir(regs, a, b, c): regs[c] = int(     a  == regs[b]); return regs
	def eqri(regs, a, b, c): regs[c] = int(regs[a] ==      b ); return regs
	def eqrr(regs, a, b, c): regs[c] = int(regs[a] == regs[b]); return regs

	def get_opcode_candidates(opcode_list, opcode_sample):
		opc_cands = []

		opc_instr = opcode_sample[0]
		regs_pre  = opcode_sample[1]
		regs_post = opcode_sample[2]

		## check which opcodes produce the "after" register-state from "before" given instr
		for i in xrange(len(opcode_list)):
			opcode_func = opcode_list[i]

			if (opcode_func == None):
				continue

			if (opcode_func(regs_pre[:], opc_instr[1], opc_instr[2], opc_instr[3]) == regs_post):
				opc_cands.append((i, opcode_func))

		return opc_cands

	opcode_funcs = [addr, addi,  mulr, muli,  banr, bani,  borr, bori,  setr, seti,  gtir, gtri, gtrr,  eqir, eqri, eqrr]
	mapped_funcs = [None] * len(opcode_funcs)

	program_regs = [0, 0, 0, 0]
	program_instrs = [ [int(instr.group(i)) for i in xrange(1, 4 + 1)] for instr in instrs ]
	opcode_samples = [
		([int(sample[0].group(i)) for i in xrange(1, 4 + 1)],
		 [int(sample[1].group(j)) for j in xrange(1, 4 + 1)],
		 [int(sample[2].group(k)) for k in xrange(1, 4 + 1)])
		for sample in samples
	]

	match3_count = 0
	mapped_count = 1

	## part 1
	for opcode_sample in opcode_samples:
		match3_count += (len(get_opcode_candidates(opcode_funcs, opcode_sample)) >= 3)

	## part 2; loop until no opcodes can be mapped
	while (mapped_count != 0):
		mapped_count = 0

		## each sample contains the register-state before and after opcode execution
		## if only *one* candidate, opcode is definitively mapped and can be removed
		for opcode_sample in opcode_samples:
			opcode_cands = get_opcode_candidates(opcode_funcs, opcode_sample)

			if (len(opcode_cands) == 1):
				mapped_count += 1

				print("[dbg] opcode %d maps to function %s" % (opcode_sample[0][0], opcode_cands[0][1].func_name))
				assert(opcode_funcs[ opcode_cands[0][0] ] != None)
				assert(mapped_funcs[ opcode_sample[0][0] ] == None)

				opcode_funcs[ opcode_cands[0][0] ] = None
				mapped_funcs[ opcode_sample[0][0] ] = opcode_cands[0][1]

	assert(len(program_instrs) == 0 or mapped_funcs.count(None) == 0)

	for instr in program_instrs:
		mapped_funcs[ instr[0] ](program_regs, instr[1], instr[2], instr[3])


	print("[dbg] opcode_samples=%d match3_count=%d program_regs=%s" % (len(opcode_samples), match3_count, program_regs))
	return (match3_count, program_regs[0])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  1,   0))
run(parse_input(__file__[: -2] + "in"     ), (542, 575))

