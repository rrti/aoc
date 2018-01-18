def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		insts = [0] * len(lines)

		for i in xrange(len(lines)):
			insts[i] = int(lines[i])

		return insts


## def mod_instr_p1(joffset): return 1
## def mod_instr_p2(joffset): return (((joffset >= 3) and -1) or 1)
## more than a second slower
## def mod_instr_p2(joffset): return (1 - 2 * (joffset >= 3))

def exec_instrs(jump_ins, jump_mod):
	## local copy, saves 0.2s
	jump_mod = jump_mod[:]

	ins_index = 0
	num_insts = 0
	max_insts = len(jump_ins)

	while (ins_index < max_insts):
		jump_ofs = jump_ins[ins_index]

		jump_ins[ins_index] += jump_mod[jump_ofs >= 3]
		## jump_ins[ins_index] += jump_mod(jump_ofs)

		ins_index += jump_ofs
		num_insts += 1

	return num_insts


TEST_INSTRS = [0, 3, 0, 1, -3]
REAL_INSTRS = parse_input("day05.in")
## calling a function is expensive in general, use tuples
JUMP_MODS = ((1,  1), (1, -1))

assert(exec_instrs(TEST_INSTRS[:], JUMP_MODS[0]) ==        5)
assert(exec_instrs(REAL_INSTRS[:], JUMP_MODS[0]) ==   373543) ## part 1
assert(exec_instrs(REAL_INSTRS[:], JUMP_MODS[1]) == 27502966) ## part 2

