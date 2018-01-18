def parse_input(fn):
	with open(fn) as f:
		moves = f.readlines()
		moves = moves[0].split(",")
		return moves


def state_to_string(state): return ("".join(state))
def permute_state(state, moves, table, iter_num):
	def spin(s, x):
		i = len(s) - x
		b = s[i:  ]
		a = s[0: i]

		for j in xrange(len(a)): s[j + len(b)] = a[j]
		for j in xrange(len(b)): s[j         ] = b[j]

	def swap(s, a, b):
		s[a], s[b] = s[b], s[a]

	for move in moves:
		char = move[0]

		if (char == 's'):
			spin(state, int(move[1: ]))
		else:
			k = move.index('/')
			a = move[    1: k]
			b = move[k + 1:  ]

			if (char == 'x'): swap(state,         int(a),         int(b))
			if (char == 'p'): swap(state, state.index(a), state.index(b))

		if (state_to_string(state) in table):
			return False

	## save state after entire sequence of moves has completed
	table[state_to_string(state)] = iter_num
	return True


def permute_state_loop(state, moves, table, num_iters):
	num_calls = 0
	state_num = 0

	## reaches the "pkgnhomelfdibjac" state again after 61 permute_state() calls
	## i.e. state #0 (post-call) equals state #60 (post-call) for a period length
	## of 60; the state after N iterations will thus be equal to (N - 1) % period
	for iter_num in xrange(num_iters):
		if (not permute_state(state, moves, table, iter_num)):
			num_calls = iter_num + 1
			state_num = (num_iters - 1) % (num_calls - 1)
			## part 2
			## assert(state_to_string(state) == REAL_GOAL_STATES[0])
			assert(num_calls == 61)
			assert(state_num == 39)
			break

	for perm_state in table:
		if (table[perm_state] == state_num):
			return (state_to_string(perm_state))

	assert(False)
	return ""


TEST_STATE = [chr(i + ord('a')) for i in xrange( 5)]
REAL_STATE = [chr(i + ord('a')) for i in xrange(16)]
TEST_MOVES = ["s1", "x3/4", "pe/b"]
REAL_MOVES = parse_input("day16.in")

TEST_GOAL_STATES = ("baedc", )
REAL_GOAL_STATES = ("pkgnhomelfdibjac", "pogbjfihclkemadn")


assert(permute_state_loop(TEST_STATE, TEST_MOVES, {},                  1) == TEST_GOAL_STATES[0])
assert(permute_state_loop(REAL_STATE, REAL_MOVES, {}, 1000 * 1000 * 1000) == REAL_GOAL_STATES[1])

