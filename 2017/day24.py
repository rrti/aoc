def parse_input(fn):
	with open(fn, 'r') as f:
		components = f.readlines()

		for i in xrange(len(components)):
			components[i] = components[i].strip()
			components[i] = components[i].split("/")
			components[i] = (int(components[i][0]), int(components[i][1]))

		return components


def make_component_table(compon_list):
	compon_table = {}

	for i in xrange(len(compon_list)):
		(a, b) = compon_list[i]

		if (compon_table.get(a, None) == None):
			compon_table[a] = []
		if (compon_table.get(b, None) == None):
			compon_table[b] = []

		## for each component <i> with input/output ports a/b, make
		## <a> map to (i, b) and <b> map to (i, a) s.t. we can look
		## up only matching components when extending the bridge
		compon_table[a].append((i, b))

		if (a == b):
			continue

		compon_table[b].append((i, a))

	return compon_table


def make_bridge_rec(a, b,  cur_comp_idx, max_len_bridge,  compon_list, compon_table, compon_indcs,  _):
	max_bridge_str = 0
	max_bridge_len = 0

	compon_indcs.add(cur_comp_idx)

	## extend bridge with all matching components
	for (nxt_comp_idx, c) in compon_table[b]:
		if (nxt_comp_idx in compon_indcs):
			continue

		## same as compon_indcs but in sorted order
		## bridge_cmps.append(j)
		cur_rec_bridge = make_bridge_rec(b, c,  nxt_comp_idx, max_len_bridge,  compon_list, compon_table, compon_indcs,  _)
		## bridge_cmps.pop()

		max_bridge_str = max(cur_rec_bridge[0], max_bridge_str)
		max_bridge_len = max(cur_rec_bridge[1], max_bridge_len)

	def calc_bridge_strength(component_idcs, component_list):
		s = 0
		for component_index in component_idcs:
			s += component_list[component_index][0]
			s += component_list[component_index][1]
		return s

	## part 2; save the strength of each maximum-length bridge
	## if (len(bridge_cmps) == max_len_bridge[0]):
	##	max_len_bridge[1].append(calc_bridge_strength(bridge_cmps, compon_list))
	if (len(compon_indcs) == max_len_bridge[0]):
		max_len_bridge[2].append(calc_bridge_strength(compon_indcs, compon_list))

	compon_indcs.remove(cur_comp_idx)

	return (max_bridge_str + a + b, max_bridge_len + 1)


def make_bridge(compon_list, max_bridge_len):
	compon_table = make_component_table(compon_list)
	compon_indcs = set()

	## [0] := maximum strength over all lengths
	## [1] := maximum length over all bridges
	max_rec_bridge = [0, 0, None]

	if (max_bridge_len != 0):
		max_bridge_str = 0

		for (comp_idx, b) in compon_table[0]:
			max_rec_bridge[0] = max_bridge_len
			max_rec_bridge[2] = [0]

			## cur_rec_bridge = make_bridge_rec(0, b,  comp_idx, max_rec_bridge,  compon_list, compon_table, compon_indcs,  [comp_idx])
			cur_rec_bridge = make_bridge_rec(0, b,  comp_idx, max_rec_bridge,  compon_list, compon_table, compon_indcs,  None)
			max_bridge_str = max(max_bridge_str, max(max_rec_bridge[2]))

		return (max_bridge_str, max_bridge_len)


	for (comp_idx, b) in compon_table[0]:
		## cur_rec_bridge = make_bridge_rec(0, b,  comp_idx, max_rec_bridge,  compon_list, compon_table, compon_indcs,  [comp_idx])
		cur_rec_bridge = make_bridge_rec(0, b,  comp_idx, max_rec_bridge,  compon_list, compon_table, compon_indcs,  None)

		max_rec_bridge[0] = max(max_rec_bridge[0], cur_rec_bridge[0])
		max_rec_bridge[1] = max(max_rec_bridge[1], cur_rec_bridge[1])

	return (max_rec_bridge[0], max_rec_bridge[1])



## each component can be used only once
## output port of one component must be matched with the input of another
## bridge can end with any component but must start with (0/*); length is
## not relevant (longer bridges may or may not be stronger)
## otherwise known as the longest path problem, which is NP-hard
TEST_COMPONENTS = [
	( 0,  2),
	( 2,  2),
	( 2,  3),
	( 3,  4),
	( 3,  5),
	( 0,  1),
	(10,  1),
	( 9, 10),
]

REAL_COMPONENTS = parse_input("day24.in")

MAX_TEST_BRIDGE_DATA = make_bridge(TEST_COMPONENTS, 0)
MAX_REAL_BRIDGE_DATA = make_bridge(REAL_COMPONENTS, 0)

assert(MAX_TEST_BRIDGE_DATA == (  31,  4))
assert(MAX_REAL_BRIDGE_DATA == (1868, 40))
assert(make_bridge(TEST_COMPONENTS, MAX_TEST_BRIDGE_DATA[1]) == (  19, MAX_TEST_BRIDGE_DATA[1]))
assert(make_bridge(REAL_COMPONENTS, MAX_REAL_BRIDGE_DATA[1]) == (1841, MAX_REAL_BRIDGE_DATA[1]))

