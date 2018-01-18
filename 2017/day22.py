## set large enough to simulate an "infinite" grid
INF_GRID_SIZE = 10000000000

CELL_STATE_C = '.' ## clean
CELL_STATE_I = '#' ## infected
CELL_STATE_W = 'w' ## weakened
CELL_STATE_F = 'f' ## flagged


def parse_input(fn):
	with open(fn, 'r') as f:
		rows = f.readlines()

		ydim = len(rows)
		xdim = len(rows[0]) - 1
		grid = {}

		## store the grid implicitly with a hash-table of infected cells
		for row in xrange(ydim):
			for col in xrange(xdim):
				if (rows[row][col] == CELL_STATE_I):
					grid[row * INF_GRID_SIZE + col] = CELL_STATE_I

		return (grid, xdim, ydim)


def run_part1(grid, num_iters, num_cols, num_rows):
	num_infs = 0

	## start in the center of the initial grid region
	xpos = num_cols / 2
	ypos = num_rows / 2
	xdir = 0 
	ydir = 1 ## up (!)

	num_cols = INF_GRID_SIZE
	num_rows = INF_GRID_SIZE

	if (len(grid) == 0):
		grid[(ypos    ) * num_cols + (xpos - 1)] = CELL_STATE_I
		grid[(ypos - 1) * num_cols + (xpos + 1)] = CELL_STATE_I

	for i in xrange(num_iters):
		cell = grid.get(ypos * num_cols + xpos, CELL_STATE_C)

		xd = xdir
		yd = ydir

		if (cell == CELL_STATE_C):
			## clean cell, infect and turn left
			grid[ypos * num_cols + xpos] = CELL_STATE_I

			xdir = -yd
			ydir =  xd
			num_infs += 1
		else:
			## infected cell, clean and turn right
			del grid[ypos * num_cols + xpos]

			ydir = -xd
			xdir =  yd

		xpos += xdir
		ypos -= ydir

	return num_infs

def run_part2(grid, num_iters, num_cols, num_rows):
	num_infs = 0

	xpos = num_cols / 2
	ypos = num_rows / 2
	xdir = 0 
	ydir = 1

	num_cols = INF_GRID_SIZE
	num_rows = INF_GRID_SIZE

	if (len(grid) == 0):
		grid[(ypos    ) * num_cols + (xpos - 1)] = CELL_STATE_I
		grid[(ypos - 1) * num_cols + (xpos + 1)] = CELL_STATE_I

	for i in xrange(num_iters):
		cell = grid.get(ypos * num_cols + xpos, CELL_STATE_C)

		xd = xdir
		yd = ydir

		if (cell == CELL_STATE_C):
			grid[ypos * num_cols + xpos] = CELL_STATE_W

			xdir = -yd
			ydir =  xd
		elif (cell == CELL_STATE_W):
			grid[ypos * num_cols + xpos] = CELL_STATE_I
			num_infs += 1
		elif (cell == CELL_STATE_I):
			grid[ypos * num_cols + xpos] = CELL_STATE_F

			ydir = -xd
			xdir =  yd
		elif (cell == CELL_STATE_F):
			del grid[ypos * num_cols + xpos]

			xdir = -xdir
			ydir = -ydir

		xpos += xdir
		ypos -= ydir

	return num_infs


grid_data = parse_input("day22.in")

assert(run_part1(                 {},    70,            9,            8) ==   41)
assert(run_part1(                 {}, 10000,            9,            8) == 5587)
assert(run_part1(grid_data[0].copy(), 10000, grid_data[1], grid_data[2]) == 5433)

assert(run_part2(                 {},      100, grid_data[1], grid_data[2]) ==      26)
assert(run_part2(                 {}, 10000000, grid_data[1], grid_data[2]) == 2511944)
assert(run_part2(grid_data[0].copy(), 10000000, grid_data[1], grid_data[2]) == 2512599)

