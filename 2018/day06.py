from collections import defaultdict as ddict
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		regex = r"([0-9]+),\s*([0-9]+)"
		lines = f.readlines()
		coors = [re_search(regex, line[: -1]) for line in lines]
		return coors

	return []

def handle_input(coors):
	xmin =  10000
	xmax = -10000
	ymin =  10000
	ymax = -10000
	pts = []

	if (True):
		## NB:
		##   "safe" points can lie outside bounding-box, e.g. when input is [(1, 1)]
		##   in this case the safe area will be a diamond with footprint 20001x20001
		for i in xrange(len(coors)):
			pts.append((int(coors[i].group(1)), int(coors[i].group(2)), i)) ## x,y,id

			xmin = min(xmin, pts[-1][0])
			xmax = max(xmax, pts[-1][0])
			ymin = min(ymin, pts[-1][1])
			ymax = max(ymax, pts[-1][1])
	else:
		pts.append((1, 1, 0))

		xmin = -xmin
		xmax = -xmin
		ymin = -ymin
		ymax = -ymax

	xsize = (xmax - xmin) + 1
	ysize = (ymax - ymin) + 1

	area_grid = [(99999999, -1)] * xsize * ysize
	safe_grid = [0] * xsize * ysize

	## each coordinate has its own area associated with it
	## grid_areas = [0] * (len(coors) + 1)
	grid_areas = ddict(lambda: 0)
	grid_edges = set()

	max_cell = 0
	max_area = 0
	max_smhd = ((len(coors) < 10) and 32) or 10000

	for y in xrange(ymin, ymax + 1):
		rely = y - ymin

		for x in xrange(xmin, xmax + 1):
			relx = x - xmin
			smhd = 0

			## TODO:
			##   no need to check *all* points, just the closest in each quadrant?
			##   should probably start with a seed coordinate at (0, 0) and expand
			for pt in pts:
				dx = relx - (pt[0] - xmin)
				dy = rely - (pt[1] - ymin)

				## Manhattan-distance from grid (x,y) to point
				pmhd = abs(dx) + abs(dy)
				smhd += pmhd

				if (pmhd > area_grid[rely * xsize + relx][0]):
					continue
				if (pmhd < area_grid[rely * xsize + relx][0]):
					area_grid[rely * xsize + relx] = (pmhd, pt[2])
					continue

				## coordinate equidistant to multiple points, no valid id
				area_grid[rely * xsize + relx] = (pmhd, len(coors))

			safe_grid[rely * xsize + relx] = int(smhd < max_smhd)

	## exclude edge-cells since these are part of infinite areas which do not count
	for y in xrange(ymin, ymax + 1):
		rely = y    - ymin
		relx = xmax - xmin

		grid_edges.add(area_grid[rely * xsize +    0][1])
		grid_edges.add(area_grid[rely * xsize + relx][1])
	for x in xrange(xmin, xmax + 1):
		relx = x    - xmin
		rely = ymax - ymin

		grid_edges.add(area_grid[   0 * xsize + relx][1])
		grid_edges.add(area_grid[rely * xsize + relx][1])

	## calculate footprint of each internal area
	## only cells on the grid edges can be skipped directly, all
	## others have to be checked for membership of infinite areas
	for y in xrange(ymin + 1, ymax + 1 - 1):
		rely = y - ymin

		for x in xrange(xmin + 1, xmax + 1 - 1):
			relx = x - xmin
			cell = area_grid[rely * xsize + relx][1]

			grid_areas[cell] += int(not (cell in grid_edges))

	## find uncontested area with largest footprint
	for cell in xrange(len(coors)):
		cur_area = grid_areas[cell]

		if (cur_area <= max_area):
			continue

		max_cell = cell
		max_area = cur_area

	## forgo floodfill, only a single contiguous "safe" area should exist
	return (max_area, sum(safe_grid))

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  17,    16))
run(parse_input(__file__[: -2] + "in"     ), (5532, 36216))

