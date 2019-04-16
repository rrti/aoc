from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		state = re_search(r"initial state: ([#.]+)", lines[0][: -1])
		rules = [re_search(r"([#.]+) => ([#.]+)", line[: -1]) for line in lines[2: ]]

		return (state, rules)

	return (None, None)

def handle_input((state, rules)):
	def rule_match(array0, array1, rule, index):
		head = rule[0]
		tail = rule[1]

		assert(len(head) == 5)
		assert(len(tail) == 1)

		for i in xrange(-2, 2 + 1):
			if (array0[index + i] != head[2 + i]):
				return False

		array1[index] = tail[0]
		return True

	def calc_pot_sum(array, zero_idx, min_idx, max_idx, idx_ofs):
		pot_sum = 0
		for j in xrange(min_idx, max_idx + 1):
			pot_sum += ((idx_ofs + j - zero_idx) * (array[j] == '#'))
		return pot_sum


	state = state.group(1)
	rules = [(rule.group(1), rule.group(2)) for rule in rules]
	arrays = [ ['.'] * 100001, ['.'] * 100001 ]
	cache = set()

	cur_array_idx = 0
	nxt_array_idx = 1

	num_gens = 0
	max_gens = 500
	zero_idx = len(arrays[cur_array_idx]) >> 1
	rule_len = len(rules[0][0]) >> 1
	min_idx = zero_idx - rule_len
	max_idx = zero_idx + rule_len + len(state)
	pot_sum = [0, 0]

	## initialize write-buffer from state
	for i in xrange(len(state)):
		arrays[cur_array_idx][zero_idx + i] = state[i]

	## perform enough iterations to make the pattern repeat, but not too many
	while (num_gens < max_gens):
		for j in xrange(min_idx, max_idx + 1):
			arrays[nxt_array_idx][j] = '.'

		for j in xrange(min_idx, max_idx + 1):
			for k in xrange(len(rules)):
				if (rule_match(arrays[cur_array_idx], arrays[nxt_array_idx], rules[k], j)):
					break

		if (num_gens == (20 - 1)):
			pot_sum[0] = calc_pot_sum(arrays[nxt_array_idx], zero_idx, min_idx, max_idx, 0)

		## detect steady-state condition
		pot_arr = arrays[nxt_array_idx][min_idx: max_idx + 1]
		pot_str = "".join(pot_arr[ pot_arr.index('#'): ])

		if (pot_str in cache):
			print("[dbg] gen=%d min=%d max=%d cnt('#')=%d idx('#')=%d str=%s" % (i, min_idx, max_idx, pot_arr.count('#'), pot_arr.index('#'), pot_str))
			break

		cache.add(pot_str)


		## [min_idx = zero_idx - (rule_len/2)][min_idx + 1][zero_idx][...state...][max_idx - 1][max_idx = zero_idx + state_len + (rule_len/2)]
		a = (arrays[nxt_array_idx][min_idx - 0] == '#') * 2
		b = (arrays[nxt_array_idx][min_idx + 1] == '#') * 1
		c = (arrays[nxt_array_idx][max_idx + 0] == '#') * 2
		d = (arrays[nxt_array_idx][max_idx - 1] == '#') * 1
		min_idx -= max(a, b)
		max_idx += max(c, d)
		num_gens += 1


		## flip buffers
		cur_array_idx = 1 - cur_array_idx
		nxt_array_idx = 1 - nxt_array_idx


	## part 2; based on observation of steady-state pattern
	## number of #'s remains constant after gen 162 (as does
	## min_idx), while max_idx increases by 1 each iteration
	## because entire pattern shifts right
	if (len(state) > 25):
		abs_pot_idx = arrays[cur_array_idx].index('#')
		rel_pot_idx = abs_pot_idx - zero_idx
		end_pot_idx = rel_pot_idx + (50 * 1000000000 - num_gens)

		rep_str = "#.......#...........#.......#.......#.....#......#......#.......#......#.....#.......#.......#..............#.......#.....#.....#......#.....#......#......#.......#.....#"
		pot_str = "".join(arrays[cur_array_idx][abs_pot_idx: abs_pot_idx + len(rep_str)])
		assert(pot_str == rep_str)

		pot_sum[1] = calc_pot_sum(arrays[cur_array_idx], abs_pot_idx, abs_pot_idx, abs_pot_idx + len(pot_str) - 1, end_pot_idx)

	return (pot_sum[0], pot_sum[1])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), ( 325,             0))
run(parse_input(__file__[: -2] + "in"     ), (1987, 1150000000358))

