import re

class turing_machine:
	def __init__(self, fn, re):
		with open(fn, 'r') as f:
			self.parse_state_blocks((re, f.readlines()))
			self.compile_state_blocks()

	def parse_state_blocks(self, state_descr):
		## parse header lines
		start_state_match = re.search(state_descr[0]["start_state"], state_descr[1][0].strip("\n"))
		cycle_count_match = re.search(state_descr[0]["cycle_count"], state_descr[1][1].strip("\n"))

		self.cycle_count = int(cycle_count_match.group(1))
		self.start_state =     start_state_match.group(1)

		self.state_table = {}
		self.memory_tape = {}

		instr_blocks = [None]

		i = 2
		n = len(state_descr[1])

		while (i < n):
			i += self.parse_instr_blocks(i,  instr_blocks, state_descr)
			i += self.parse_block_instrs(i,  instr_blocks, state_descr)


	def parse_instr_blocks(self, i,  instr_blocks, state_descr):
		cur_state_match = re.search(state_descr[0]["cur_state"], state_descr[1][i].strip("\n"))

		if (cur_state_match == None):
			return 0

		## instruction blocks for val==1 and val==0 branches; always two per state
		self.state_table[cur_state_match.group(1)] = instr_blocks[0] = [[], []]
		return 1

	def parse_block_instrs(self, i,  instr_blocks, state_descr):
		cur_value_match = re.search(state_descr[0]["cur_value"], state_descr[1][i].strip("\n"))

		## skip whitespace lines
		if (cur_value_match == None):
			return 1

		mem_write_match = re.search(state_descr[0]["write_val"], state_descr[1][i + 1].strip("\n"))
		move_head_match = re.search(state_descr[0]["move_head"], state_descr[1][i + 2].strip("\n"))
		set_state_match = re.search(state_descr[0]["set_state"], state_descr[1][i + 3].strip("\n"))

		block_guard_val = int(cur_value_match.group(1))
		block_write_val = int(mem_write_match.group(1))

		cur_instr_block = instr_blocks[0][block_guard_val]

		## filter out redundant write-ops; minor performance increase
		if (block_write_val != block_guard_val):
			cur_instr_block.append("self.memory_tape[head_pos] = %d;" % block_write_val)

		cur_instr_block.append("head_pos %s 1;" % (((move_head_match.group(1) == "left") and "-=") or "+="))
		cur_instr_block.append("tm_state = self.state_table['%c'];" % set_state_match.group(1))
		return 4


	def compile_state_blocks(self):
		for instr_blocks in self.state_table.values():
			instr_blocks[1] = compile("".join(instr_blocks[1]), "<string>", "exec")
			instr_blocks[0] = compile("".join(instr_blocks[0]), "<string>", "exec")

	def calc_checksum(self):
		head_pos = 0
		tm_state = self.state_table[self.start_state]

		for i in xrange(self.cycle_count):
			exec(tm_state[ self.memory_tape.get(head_pos, 0) ])

		## calculate checksum
		return (sum(self.memory_tape.values()))


STATE_DESCR_REGEXES = {
	"start_state": r"Begin in state ([A-Z]+).",
	"cycle_count": r"Perform a diagnostic checksum after ([0-9]+) steps.",

	"cur_state": r"In state ([A-Z]+):",
	"cur_value": r"\s*If the current value is ([0-9]+):",
	"write_val": r"\s*-\s*Write the value ([0-9]+).",
	"move_head": r"\s*-\s*Move one slot to the (left|right).",
	"set_state": r"\s*-\s*Continue with state ([A-Z]+).",
}

TEST_TURING_MACHINE = turing_machine("day25_test.in", STATE_DESCR_REGEXES)
REAL_TURING_MACHINE = turing_machine("day25.in"     , STATE_DESCR_REGEXES)

assert(TEST_TURING_MACHINE.calc_checksum() ==    3)
assert(REAL_TURING_MACHINE.calc_checksum() == 2846)

