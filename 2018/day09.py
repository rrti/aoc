from re import search as re_search
from time import time

TESTS = [
	## (number of players, number of marbles, maximum score)
	(  9,    25      ,         32),
	( 10,  1618      ,       8317),
	( 13,  7999      ,     146373),
	( 17,  1104      ,       2764),
	( 21,  6111      ,      54718),
	( 30,  5807      ,      37305),
	(423, 71944      ,     418237),
	(423, 71944 * 100, 3505711612),
]


def parse_input(fn):
	with open(fn, 'r') as f:
		rexp = r"([0-9]+) players; last marble is worth ([0-9]+) points"
		line = f.readlines()[0]
		data = re_search(rexp, line[: -1])
		return data

	return []

def handle_input(data):
	return (play_game_soultaker(int(data.group(1)), int(data.group(2))))



def play_game_soultaker(players, marbles):
	cur_marble = 0

	scores = [0] * players
	## indices into circle for a given marble's {prede,suc}cessor
	## marbles are represented as a circular array rather than LL
	prev_list = [0] * marbles
	next_list = [0] * marbles

	for nxt_marble in xrange(1, marbles):
		## print
		## print cur_marble, nxt_marble
		## print prev_list
		## print next_list

		if ((nxt_marble % 23) == 0):
			for _ in xrange(7):
				cur_marble = prev_list[cur_marble]

			player = (nxt_marble - 1) % players
			scores[player] += (cur_marble + nxt_marble)

			nxt_marble = next_list[cur_marble]
			cur_marble = prev_list[cur_marble]
		else:
			cur_marble = next_list[cur_marble]
			tmp_marble = next_list[cur_marble]

			next_list[nxt_marble] = tmp_marble
			prev_list[tmp_marble] = nxt_marble

		next_list[cur_marble] = nxt_marble
		prev_list[nxt_marble] = cur_marble

		cur_marble = nxt_marble

	return max(scores)



def play_game_ll(num_players, num_marbles):
	class ll_node:
		def __init__(self, data, prev, next):
			self.data = data
			self.prev = prev
			self.next = next

	scores = [0] * num_players
	llhead = ll_node(0, None, None)
	llnode = llhead
	## circularity
	llnode.prev = llhead
	llnode.next = llhead

	player_idx = 0
	num_iters = 0

	def print_list(node):
		head = node
		data = []
		while (node != None):
			data += [node.data]
			node = node.next
			if (node == head):
				break

		print("%s" % str(data))

	while (num_iters < num_marbles):
		nxt_marble = num_iters + 1

		if ((nxt_marble % 23) == 0):
			## the marble 7 marbles counter-clockwise from the current marble is
			## removed from the circle and also added to the current player's score;
			## the marble located immediately clockwise of the marble that was removed
			## becomes the new current marble"
			for i in xrange(7):
				llnode = llnode.prev

			scores[player_idx] += nxt_marble
			scores[player_idx] += llnode.data

			a = llnode.prev
			b = llnode.next
			a.next = b
			b.prev = a
			llnode = b
		else:
			## "place the lowest-numbered remaining marble into the circle between
			## the marbles that are 1 and 2 marbles clockwise of the current marble"
			a = llnode.next
			b = llnode.next.next
			c = ll_node(nxt_marble, a, b)
			a.next = c
			b.prev = c
			llnode = c

		player_idx = (player_idx + 1) % num_players
		num_iters += 1

	return max(scores)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run_tests(st = True, rt = True):
	if (st):
		t0 = time()

		## NB: players=17 marbles=1104 returns score=2720 without the "+1"
		for test in TESTS:
			assert(play_game_soultaker(test[0], test[1] + 1) == test[2])

		print("[run_tests(st)] dt=%fs" % (time() - t0))

	if (rt):
		t0 = time()

		## roughly a factor 10 slower than the circular-array version
		for test in TESTS:
			assert(play_game_ll(test[0], test[1]) == test[2])

		print("[run_tests(rt)] dt=%fs" % (time() - t0))

def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), (418237))
run_tests()

