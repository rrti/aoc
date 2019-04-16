from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		world = [line[: -1] for line in lines]
		return world

	return []

def handle_input(world):
	grid_cache = dict()
	grid_states = [
		[list(row) for row in world],
		[list(row) for row in world]
	]
	res_values = []

	r_index = 0
	w_index = 1

	OA_CELL = '.' ## open acre
	WA_CELL = '|' ## wooded acre (tree)
	LY_CELL = '#' ## lumberyard

	def calc_resource_value(state):
		num_wa = 0
		num_ly = 0

		for y in xrange(len(world)):
			for x in xrange(len(world[0])):
				num_wa += (state[y][x] == WA_CELL)
				num_ly += (state[y][x] == LY_CELL)

		return (num_wa * num_ly)

	for n in xrange(1000000000):
		r_state = grid_states[r_index]
		w_state = grid_states[w_index]

		if (False):
			print("\n\n[dbg][pre-%d] r_index=%d w_index=%d  nrows=%d cols=%d" % (n, r_index, w_index, len(world), len(world[0])))
			for row in r_state:
				print("%s" % "".join(row))

		for y in xrange(len(world)):
			for x in xrange(len(world[0])):
				num_ngb_oa = 0
				num_ngb_wa = 0
				num_ngb_ly = 0

				for j in xrange(-1, 1 + 1):
					yj = y + j

					if (yj < (             0)): continue
					if (yj > (len(world) - 1)): continue

					for i in xrange(-1, 1 + 1):
						xi = x + i

						if (xi < (                0)): continue
						if (xi > (len(world[0]) - 1)): continue

						if (i == 0 and j == 0):
							continue

						num_ngb_oa += (r_state[yj][xi] == OA_CELL)
						num_ngb_wa += (r_state[yj][xi] == WA_CELL)
						num_ngb_ly += (r_state[yj][xi] == LY_CELL)

				## "An open acre will become filled with trees if three or more adjacent acres contained trees."
				## "An acre filled with trees will become a lumberyard if three or more adjacent acres were lumberyards."
				## "An acre containing a lumberyard will remain a lumberyard if it was adjacent to at least
				## one other lumberyard and at least one acre containing trees. Otherwise, it becomes open."
				w_state[y][x] = r_state[y][x]

				if (r_state[y][x] == OA_CELL and (num_ngb_wa >= 3)):
					w_state[y][x] = WA_CELL
				if (r_state[y][x] == WA_CELL and (num_ngb_ly >= 3)):
					w_state[y][x] = LY_CELL
				if (r_state[y][x] == LY_CELL):
					w_state[y][x] = ((num_ngb_ly >= 1 and num_ngb_wa >= 1) and LY_CELL) or OA_CELL

		if (False):
			print("\n[post-%d] r_index=%d w_index=%d" % (n, r_index, w_index))
			for row in w_state:
				print("%s" % "".join(row))


		## res_values.append(calc_resource_value(grid_states[r_index]))
		res_values.append(calc_resource_value(grid_states[w_index]))

		## stringify the write-state
		flat_state = [w_state[y][x] for y in xrange(len(world)) for x in xrange(len(world[0]))]
		state_repr = "".join(flat_state)

		## repeat-state is reached after 445 iters (first seen at iter 417) with resource-value 207000
		## cycle-length is 445 - 417 = 28 for given input; starting at 417 determine how many times we
		## we can step ahead by 28 without exceeding iteration-limit N=1000000000, then in which state
		## of the cycle this process would end up
		##
		##          1000000000 -       417  = 999999583
		##           999999583 /        28  = 35714270
		##   417 +    35714270 *        28  = 999999977
		##   417 + (1000000000 - 999999977) = 440
		##
		if (state_repr in grid_cache):
			period_start  = grid_cache[state_repr][0]
			period_length = n - period_start
			period_steps  = (1000000000 - period_start) / period_length
			period_offset = 1000000000 - (period_start + period_steps * period_length)
			wanted_state  = period_start + period_offset

			## need to subtract 1 if appending value of grid_states[w_index] above
			return (res_values[10 - 1], res_values[wanted_state - 1])

		grid_cache[state_repr] = (n, res_values[-1])

		## flip buffers
		r_index = 1 - r_index
		w_index = 1 - w_index

	assert(False)
	return (0, 0)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  1147,      0)) ## test-state value decays
run(parse_input(__file__[: -2] + "in"     ), (481290, 180752))

