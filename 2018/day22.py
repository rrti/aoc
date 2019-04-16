from collections import defaultdict as ddict
from re import search as re_search
from sys import stdin
from time import time
from Queue import PriorityQueue

##
## the region at 0,0 (the mouth of the cave) has a geologic index of 0
## the region at the coordinates of the target has a geologic index of 0
## if the region's Y coordinate is 0, the geologic index is its X coordinate times 16807
## if the region's X coordinate is 0, the geologic index is its Y coordinate times 48271
## otherwise, the region's geologic index is the result of multiplying the erosion levels of the regions at X-1,Y and X,Y-1
##
## a region's erosion level is its geologic index plus the cave system's depth, all modulo 20183
##    if the erosion level modulo 3 is 0, the region's type is rocky
##    if the erosion level modulo 3 is 1, the region's type is wet
##    if the erosion level modulo 3 is 2, the region's type is narrow
##
##
## in rocky regions, you can use the climbing gear or the torch (you cannot use neither)
## in wet regions, you can use the climbing gear or neither tool (you cannot use the torch)
## in narrow regions, you can use the torch or neither tool (you cannot use the climbing gear)
##
## you start at 0,0 (the mouth of the cave) with the torch equipped
## you can move to an adjacent region (up, down, left, or right; never diagonally)
##   if your currently equipped tool allows you to enter that region
##
## moving to an adjacent region takes one minute
## switching to using the climbing gear, torch, or neither always takes seven minutes
## you can change your currently equipped tool or put both away if your new equipment
## would be valid for your current region
##
## once you reach the target, you need the torch equipped before you can find him in the dark
## the target is always in a rocky region, so if you arrive there with climbing gear equipped,
## you will need to spend seven minutes switching to your torch
##
CELL_TYPE_R = '.'
CELL_TYPE_W = '='
CELL_TYPE_N = '|'

TOOL_TYPE_G = 'G'
TOOL_TYPE_T = 'T'
TOOL_TYPE_N = 'N'

SWAP_COST = 7
MOVE_COST = 1

REGION_TYPES = (CELL_TYPE_R, CELL_TYPE_W, CELL_TYPE_N)
NEXT_STATES = [None] * (1 + 2 * 2 + 2 * 2)



class search_state:
	def __init__(self, xpos, ypos, tool, cost, heur = 0):
		self.xpos = xpos
		self.ypos = ypos
		self.tool = tool
		self.cost = cost ## g
		self.heur = heur ## h
	def __lt__(self, s):
		return ((self.cost + self.heur) < (s.cost + s.heur))
	def __eq__(self, s):
		return (self.xpos == s.xpos and self.ypos == s.ypos and self.tool == s.tool)
	def __repr__(self):
		return ("<x=%d y=%d tool=%c" % (self.xpos, self.ypos, self.tool))
	def make_key(self):
		return (self.xpos, self.ypos, self.tool)

def gen_next_states(state, cave):
	assert(isinstance(state, search_state))

	indx = 0
	xpos = state.xpos
	ypos = state.ypos
	tool = state.tool
	cost = state.cost

	can_enter_rocky  = (tool == TOOL_TYPE_G or tool == TOOL_TYPE_T)
	can_enter_water  = (tool == TOOL_TYPE_G or tool == TOOL_TYPE_N)
	can_enter_narrow = (tool == TOOL_TYPE_T or tool == TOOL_TYPE_N)

	## tool-switching moves
	if (cave[ypos][xpos] == CELL_TYPE_R):
		assert(tool == TOOL_TYPE_G or tool == TOOL_TYPE_T)
		NEXT_STATES[indx] = (xpos, ypos, ((tool == TOOL_TYPE_G) and TOOL_TYPE_T) or TOOL_TYPE_G, cost + 0 + SWAP_COST)
	if (cave[ypos][xpos] == CELL_TYPE_W):
		assert(tool == TOOL_TYPE_G or tool == TOOL_TYPE_N)
		NEXT_STATES[indx] = (xpos, ypos, ((tool == TOOL_TYPE_G) and TOOL_TYPE_N) or TOOL_TYPE_G, cost + 0 + SWAP_COST)
	if (cave[ypos][xpos] == CELL_TYPE_N):
		assert(tool == TOOL_TYPE_T or tool == TOOL_TYPE_N)
		NEXT_STATES[indx] = (xpos, ypos, ((tool == TOOL_TYPE_T) and TOOL_TYPE_N) or TOOL_TYPE_T, cost + 0 + SWAP_COST)

	assert(xpos < len(cave[0]))
	assert(ypos < len(cave   ))

	indx += 1

	## vertical moves
	for j in xrange(-1, 1 + 1, 2):
		assert(j != 0)

		if ((ypos + j) < 0):
			continue
		if ((ypos + j) >= len(cave)):
			break

		if (cave[ypos + j][xpos] == CELL_TYPE_R  and can_enter_rocky):
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_G, cost + MOVE_COST + (tool != TOOL_TYPE_G) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_T, cost + MOVE_COST + (tool != TOOL_TYPE_T) * SWAP_COST); indx += 1
			continue
		if (cave[ypos + j][xpos] == CELL_TYPE_W  and can_enter_water):
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_G, cost + MOVE_COST + (tool != TOOL_TYPE_G) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_N, cost + MOVE_COST + (tool != TOOL_TYPE_N) * SWAP_COST); indx += 1
			continue
		if (cave[ypos + j][xpos] == CELL_TYPE_N and can_enter_narrow):
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_T, cost + MOVE_COST + (tool != TOOL_TYPE_T) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos, ypos + j, TOOL_TYPE_N, cost + MOVE_COST + (tool != TOOL_TYPE_N) * SWAP_COST); indx += 1
			continue

	## horizontal moves
	for i in xrange(-1, 1 + 1, 2):
		assert(i != 0)

		if ((xpos + i) < 0):
			continue
		if ((xpos + i) >= len(cave[0])):
			break

		if (cave[ypos][xpos + i] == CELL_TYPE_R  and can_enter_rocky):
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_G, cost + MOVE_COST + (tool != TOOL_TYPE_G) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_T, cost + MOVE_COST + (tool != TOOL_TYPE_T) * SWAP_COST); indx += 1
			continue
		if (cave[ypos][xpos + i] == CELL_TYPE_W  and can_enter_water):
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_G, cost + MOVE_COST + (tool != TOOL_TYPE_G) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_N, cost + MOVE_COST + (tool != TOOL_TYPE_N) * SWAP_COST); indx += 1
			continue
		if (cave[ypos][xpos + i] == CELL_TYPE_N and can_enter_narrow):
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_T, cost + MOVE_COST + (tool != TOOL_TYPE_T) * SWAP_COST); indx += 1
			NEXT_STATES[indx] = (xpos + i, ypos, TOOL_TYPE_N, cost + MOVE_COST + (tool != TOOL_TYPE_N) * SWAP_COST); indx += 1
			continue

	return (NEXT_STATES, indx)



def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()

		## value of width is a minor empirically determined hack which removes
		## the need to generate and memoize a potentially infinite cave on the
		## fly (the formal but much slower approach)
		depth = re_search(r"depth: ([0-9]+)", lines[0])
		width = re_search(r"width: ([0-9]+)", lines[1])
		target = re_search(r"target: ([0-9]+)\s*,\s*(([0-9]+))", lines[2])

		return ((int(width.group(1)), int(depth.group(1))), (int(target.group(1)), int(target.group(2))))

	return ((0, 0), (0, 0))

def handle_input(((width, depth), (target_x, target_y))):
	print("[dbg] width=%d depth=%d target=<x=%d,y=%d>" % (width, depth, target_x, target_y))
	assert((width % 16) == 0)

	geo_indices = [[  0] * (width + 1) for y in xrange(depth + 1)]
	eros_levels = [[  0] * (width + 1) for y in xrange(depth + 1)]
	map_regions = [[' '] * (width + 1) for y in xrange(depth + 1)]

	## also serves as the closed-set
	state_costs = ddict(lambda: 1000000000)
	state_queue = PriorityQueue()

	src_state = search_state(0, 0, TOOL_TYPE_T, 0)
	tgt_state = search_state(target_x, target_y, TOOL_TYPE_T, state_costs[(target_x, target_y)])


	def state_sort_func(a, b):
		if (a[3] < b[3]): return -1
		if (a[3] > b[3]): return +1
		return 0

	def calc_erosion_level(geo_index, cave_depth):
		return ((geo_index + cave_depth) % 20183)
	def calc_risk(xmax, ymax):
		risk = 0
		for y in xrange(0, ymax + 1):
			for x in xrange(0, xmax + 1):
				risk += (eros_levels[y][x] % 3)
		return risk

	for y in xrange(depth):
		geo_indices[y][0] = y * 48271
		eros_levels[y][0] = calc_erosion_level(geo_indices[y][0], depth)
		map_regions[y][0] = REGION_TYPES[ eros_levels[y][0] % 3 ]
	for x in xrange(width):
		geo_indices[0][x] = x * 16807
		eros_levels[0][x] = calc_erosion_level(geo_indices[0][x], depth)
		map_regions[0][x] = REGION_TYPES[ eros_levels[0][x] % 3 ]

	assert(geo_indices[0][0] == 0)

	for y in xrange(1, depth):
		for x in xrange(1, width):
			a = calc_erosion_level(geo_indices[y - 1][x], depth)
			b = calc_erosion_level(geo_indices[y][x - 1], depth)

			geo_indices[y][x] = a * b * (x != target_x or y != target_y)
			eros_levels[y][x] = calc_erosion_level(geo_indices[y][x], depth)

			map_regions[y][x] = REGION_TYPES[ eros_levels[y][x] % 3 ]


	assert(geo_indices[       0][       0] == 0) ## cave mouth is always rocky
	assert(geo_indices[target_y][target_x] == 0) ## target is always rocky

	if (False):
		for y in xrange(depth):
			print("%s" % "".join(map_regions[y]))

	if (False):
		assert(map_regions[0][0] == CELL_TYPE_R) ## test-input cave (x=0,y=0) is rocky
		assert(map_regions[0][1] == CELL_TYPE_W) ## test-input cave (x=1,y=0) is wet
		assert(map_regions[1][0] == CELL_TYPE_R) ## test-input cave (x=0,y=1) is rocky
		assert(map_regions[1][1] == CELL_TYPE_N) ## test-input cave (x=1,y=1) is narrow
		assert(calc_risk(target_x, target_y) == 114)


	state_queue.put(src_state)

	while (state_queue.qsize() > 0):
		cur_state = state_queue.get()
		nxt_states = gen_next_states(cur_state, map_regions)

		## lazy way to implement Dijkstra best-first search,
		## not needed when using a priority queue of states
		## nxt_states[0].sort(state_sort_func)


		if (False):
			while (stdin.readline() != "\n"):
				pass
			print("[dbg] cur_state=%s nxt_states=%s" % (cur_state, nxt_states[0]))


		if (cur_state == tgt_state):
			tgt_state.cost = cur_state.cost
			break


		for i in xrange(nxt_states[1]):
			nxt_state = nxt_states[0][i]
			state_key = (nxt_state[0], nxt_state[1], nxt_state[2])

			if (nxt_state[3] >= state_costs[state_key]):
				continue

			state_costs[state_key] = nxt_state[3]
			## NB: using a Manhattan-distance heuristic just makes the search slower
			state_queue.put(search_state(nxt_state[0], nxt_state[1], nxt_state[2], nxt_state[3]))


	return (calc_risk(target_x, target_y), tgt_state.cost)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), ( 114,  45))
run(parse_input(__file__[: -2] + "in"     ), (5637, 969))

