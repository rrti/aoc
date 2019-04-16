from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		## "#id @ %d,%d: %dx%d"
		regex = r"#([0-9]+)\s*@\s*([0-9]+),([0-9]+)\s*:\s*([0-9]+)x([0-9]+)"
		mlist = [re_search(regex, line[: -1]) for line in f.readlines()]
		rects = [(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))) for m in mlist]
		return rects

	return []

def handle_input(rects):
	xsize = 1000
	ysize = 1000

	grid = [0] * xsize * ysize

	num_overlaps =  0
	free_rect_id = -1

	for rect in rects:
		rpx = rect[1]
		rpy = rect[2]
		rsx = rect[3]
		rsy = rect[4]

		for y in xrange(rsy):
			for x in xrange(rsx):
				## assert((rpy + y) < ysize)
				## assert((rpx + x) < xsize)
				##
				## if cell-value is currently at 1, then this rectangle
				## is the first to cause any overlap at (x, y) and cell
				## should be counted
				##
				## a separate pass over every cell would be inefficient
				## since there are (far) more grid cells than rectangles
				grid_cell_idx = (rpy + y) * xsize + (rpx + x)
				num_overlaps += (grid[grid_cell_idx] == 1)
				grid[grid_cell_idx] += 1

	for rect in rects:
		rpx = rect[1]
		rpy = rect[2]
		rsx = rect[3]
		rsy = rect[4]
		cnt = 0

		## count how many cells within this rectangle were only covered once
		## if this number matches its total area, no other rectangle had any
		## overlap
		for y in xrange(rsy):
			for x in xrange(rsx):
				cnt += (grid[(rpy + y) * xsize + (rpx + x)] == 1)

		if (cnt == (rsx * rsy)):
			free_rect_id = rect[0]
			break

	return (num_overlaps, free_rect_id)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), (105047, 658))

