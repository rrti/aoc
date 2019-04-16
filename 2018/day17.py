from collections import defaultdict as ddict
from re import search as re_search
from sys import stdin
from time import time

CELL_OBST = '#' ## clay/rock/etc
CELL_FLOW = '|'
CELL_SAND = '.'
CELL_POOL = '~'

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		exprs = (r"x=([0-9]+),\s*y=([0-9]+)\.\.([0-9]+)", r"y=([0-9]+),\s*x=([0-9]+)\.\.([0-9]+)")
		obsts = []

		for line in lines:
			col = re_search(exprs[0], line[: -1])
			row = re_search(exprs[1], line[: -1])

			## line must be either a row or a column, not both and not neither
			assert(col == None or row == None)
			assert(col != None or row != None)

			obsts.append((col, row))

		return obsts

	return []



def print_level(level, cells, tabs = ""):
	print("\n\n\n\n")
	if (len(level[0]) > 100):
		for row_idx in xrange(len(cells)):
			## cut off right-edge columns
			## print("%s%s" % (tabs, ("".join(cells[row_idx]))[0: len(level[0]) - 4]))
			## cut off left-edge columns
			## print("%s%s" % (tabs, ("".join(cells[row_idx]))[4: len(level[0])]))
			## show everything
			print("%s%s" % (tabs, ("".join(cells[row_idx]))[0: len(level[0])]))
	else:
		for row_idx in xrange(len(cells)):
			## show all columns
			print("%s[%04d] %s" % (tabs, row_idx, ("".join(cells[row_idx]))))
	print("")

def make_test_level_1(obsts):
	return [
		['.', '.', '.', '+', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '#', '#', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '.', '.', '.', '.', '.'],
	]

def make_test_level_2(obsts):
	return [
		['.', '.', '.', '.', '.', '+', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '#', '#', '#', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '#', '#', '#', '#', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '.'],
	]

def make_test_level_3(obsts):
	return [
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '+', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
		['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.'],
		['.', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '.'],
	]


def make_level(obsts):
	xcoor_offs = 1
	level_xmin =  1000000000
	level_xmax = -1000000000
	level_ymin =  1000000000
	level_ymax = -1000000000

	obst_rows = []
	obst_cols = []

	for obst in obsts:
		col = obst[0]
		row = obst[1]

		if (col != None):
			xpos = int(col.group(1))
			ymin = int(col.group(2))
			ymax = int(col.group(3))

			level_xmin = min(level_xmin, xpos)
			level_xmax = max(level_xmax, xpos)
			level_ymin = min(level_ymin, ymin)
			level_ymax = max(level_ymax, ymax)

			obst_cols.append((xpos, ymin, ymax))
		else:
			ypos = int(row.group(1))
			xmin = int(row.group(2))
			xmax = int(row.group(3))

			level_xmin = min(level_xmin, xmin)
			level_xmax = max(level_xmax, xmax)
			level_ymin = min(level_ymin, ypos)
			level_ymax = max(level_ymax, ypos)

			obst_rows.append((ypos, xmin, xmax))

	## factor in the spring for ysize; shift all obstacles down and right by 1 cell
	level_xsize =     (level_xmax - level_xmin) + 1 + 2
	level_ysize = 1 + (level_ymax - level_ymin) + 1

	level_grid = [ [CELL_SAND for x in xrange(level_xsize)] for y in xrange(level_ysize) ]
	level_grid[0][500 - level_xmin + xcoor_offs] = '+'

	for col in obst_cols:
		xpos = col[0] - level_xmin
		ymin = col[1] - level_ymin
		ymax = col[2] - level_ymin

		for y in xrange(ymin, ymax + 1):
			level_grid[y + 1][xpos + xcoor_offs] = CELL_OBST

	for row in obst_rows:
		ypos = row[0] - level_ymin
		xmin = row[1] - level_xmin
		xmax = row[2] - level_xmin

		for x in xrange(xmin, xmax + 1):
			level_grid[ypos + 1][x + xcoor_offs] = CELL_OBST

	return level_grid



def hole_scan(level, cells, x, y, j):
	n = len(level[0])

	obst_lhs =     0 ## minimum index
	obst_rhs = n - 1 ## maximum index
	hole_lhs = None
	hole_rhs = None

	## locate boundary obstacles (if any) left and right of (x, y)
	for i in xrange(n):
		if ((x - i) < 0):
			break
		if (level[y][x - i] == CELL_OBST):
			obst_lhs = x - i
			break
	for i in xrange(n):
		if ((x + i) >= n):
			break
		if (level[y][x + i] == CELL_OBST):
			obst_rhs = x + i
			break

	## scan for "holes" (cells through which water can flow down) from center outwards in both directions
	## the lhs and rhs obstacle-coords must be INCLUSIVE since these holes can also occur in edge-columns
	for i in xrange(x, obst_rhs + 1, +1):
		assert(i >= 0)
		if (cells[y + j][i] == CELL_SAND or cells[y + j][i] == CELL_FLOW):
			hole_rhs = (i, y + j)
			break

	for i in xrange(x, obst_lhs - 1, -1):
		assert(i >= 0)
		if (cells[y + j][i] == CELL_SAND or cells[y + j][i] == CELL_FLOW):
			hole_lhs = (i, y + j)
			break

	return (hole_lhs, hole_rhs)



def trace_water(level, cells, src_x, src_y):
	queue = []

	ysize = len(level)
	xsize = len(level[0])

	iters = -1
	diffs = -1

	dbg_outer = False
	dbg_inner = False

	## propagate water through level in multiple passes
	## outer loop terminates when no cells change state
	## during a pass
	while (diffs != 0):
		coors = ddict(lambda: 0)
		queue = [(src_x, src_y + 1)]


		iters += 1
		diffs = 0

		while (len(queue) > 0):
			if (dbg_inner):
				print_level(level, cells)
				print("\t[dbg] #queue=%d queue=%s" % (len(queue), queue))
				while (stdin.readline() != "\n"):
					pass

			## depth-first search with infinite-cycle prevention
			coor = queue[-1]
			xcoor = coor[0]
			ycoor = coor[1]

			queue.pop()

			if (xcoor <      0): continue
			if (xcoor >= xsize): continue
			if (ycoor <      0): continue
			if (ycoor >= ysize): continue

			coors[coor] += 1
			if (coors[coor] > 1):
				continue


			curr_cell   =                                           level[ycoor    ][xcoor]
			next_cell_y = ((ycoor >= (ysize - 1)) and curr_cell) or cells[ycoor + 1][xcoor]


			## water tiles can never be added to the queue
			assert(curr_cell != CELL_POOL)
			## obstacles can enter it, but should just be skipped
			if (curr_cell == CELL_OBST):
				continue

			if (next_cell_y == CELL_SAND or next_cell_y == CELL_FLOW):
				## drop down empty space or along a previous water-trail
				assert(xcoor != src_x or ycoor != src_y)

				diffs += (cells[ycoor][xcoor] != CELL_FLOW)
				cells[ycoor][xcoor] = CELL_FLOW

				queue.append((xcoor, ycoor + 1))
				continue

			if (next_cell_y == CELL_OBST or next_cell_y == CELL_POOL):
				## expand left and right
				(hole_lhs, hole_rhs) = hole_scan(level, cells, xcoor, ycoor, 1)

				if (hole_lhs == None and hole_rhs == None):
					diffs += (cells[ycoor][xcoor] != CELL_POOL)
					cells[ycoor][xcoor] = CELL_POOL

					if (xcoor > (        0) and cells[ycoor][xcoor - 1] != CELL_POOL): queue.append((xcoor - 1, ycoor))
					if (xcoor < (xsize - 1) and cells[ycoor][xcoor + 1] != CELL_POOL): queue.append((xcoor + 1, ycoor))
					continue

				if (hole_lhs != None):
					assert(hole_lhs[0] >= 0)
					assert(hole_lhs[0] <= xcoor)

					## fill span left-to-right from coor (x,y) to nearest obstacle
					if (hole_rhs == None):
						for x in range(xcoor, xsize, 1):
							assert(x >= 0)
							if (level[ycoor][x] == CELL_OBST):
								break

							diffs += (cells[ycoor][x] != CELL_FLOW)
							cells[ycoor][x] = CELL_FLOW

					## fill span right-to-left from hole (x,y) to coor (x,y)
					for x in xrange(xcoor, hole_lhs[0] - 1, -1):
						assert(x >= 0)
						diffs += (cells[ycoor][x] != CELL_FLOW)
						cells[ycoor][x] = CELL_FLOW

					queue.append((hole_lhs[0], hole_lhs[1]))

				if (hole_rhs != None):
					assert(hole_rhs[0] >= 0)
					assert(hole_rhs[0] >= xcoor)

					## fill span right-to-left from coor (x,y) to nearest obstacle
					if (hole_lhs == None):
						for x in range(xcoor, -1, -1):
							assert(x >= 0)
							if (level[ycoor][x] == CELL_OBST):
								break

							diffs += (cells[ycoor][x] != CELL_FLOW)
							cells[ycoor][x] = CELL_FLOW

					## fill span left-to-right from coor (x,y) to hole (x,y)
					for x in xrange(xcoor, hole_rhs[0] + 1):
						assert(x >= 0)
						diffs += (cells[ycoor][x] != CELL_FLOW)
						cells[ycoor][x] = CELL_FLOW

					queue.append((hole_rhs[0], hole_rhs[1]))

				continue


		if (dbg_outer):
			print_level(level, cells)
			print("[dbg] iters=%d diffs=%d #queue=%d" % (iters, diffs, len(queue)))
			while (stdin.readline() != "\n"):
				pass


	overflow_water_count = 0
	standing_water_count = 0

	for row in cells:
		overflow_water_count += row.count(CELL_FLOW)
		standing_water_count += row.count(CELL_POOL)

	return (overflow_water_count, standing_water_count)




def handle_input(obsts):
	level = make_level(obsts)
	## level = make_test_level_1([])
	## level = make_test_level_2([])
	## level = make_test_level_3([])

	cells = [[ level[y][x] for x in xrange(len(level[0]))] for y in xrange(len(level))]
	tiles = trace_water(level, cells, level[0].index('+'), 0)

	return (tiles[0] + tiles[1], tiles[1])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test1"), (   57,    29))
run(parse_input(__file__[: -2] + "in.test2"), (52800, 45210))
run(parse_input(__file__[: -2] + "in.test3"), (38451, 28142))
run(parse_input(__file__[: -2] + "in"      ), (29063, 23811))

