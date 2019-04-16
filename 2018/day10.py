from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		regex = r"position=<\s*(-?[0-9]+),\s*(-?[0-9]+)> velocity=<\s*(-?[0-9]+),\s*(-?[0-9]+)>"
		lines = f.readlines()
		coors = [re_search(regex, line[: -1]) for line in lines]
		return coors

	return []

def handle_input(coors):
	def calc_point_pos(p, t):
		return (p[0] + p[2] * t, p[1] + p[3] * t)

	def frame_sort_func(a, b):
		if (a[1] < b[1]): return -1
		if (a[1] > b[1]): return +1
		return 0

	def calc_frame_size(points, frame):
		xmin =  1000000000
		xmax = -1000000000
		ymin =  1000000000
		ymax = -1000000000

		for i in xrange(len(points)):
			point = calc_point_pos(points[i], frame)

			xmin = min(xmin, point[0])
			xmax = max(xmax, point[0])
			ymin = min(ymin, point[1])
			ymax = max(ymax, point[1])

		return (xmin, ymin, xmax, ymax, frame)

	points = [None] * len(coors)
	## frames = [None] * 20000

	for i in xrange(len(coors)):
		posx = int(coors[i].group(1))
		posy = int(coors[i].group(2))
		velx = int(coors[i].group(3))
		vely = int(coors[i].group(4))
		points[i] = (posx, posy, velx, vely)


	min_time = 0
	max_time = 20000

	## frame-sizes monotonically decrease (points initially move inward) until reaching
	## a minimum, then begin increasing again which makes using a binary-search for the
	## global minimum frame-size possible; much faster than calculating all frame sizes
	## up to some far-future time and picking the min
	## NB: can cheat somewhat and discard most since example text is only 8 rows tall
	while ((max_time - min_time) > 2):
		cur_time = (min_time + max_time) >> 1

		size0 = calc_frame_size(points, cur_time + 0)
		size1 = calc_frame_size(points, cur_time + 1)
		deriv = (size1[3] - size1[1]) - (size0[3] - size0[1])

		## derivative (df / dt) indicates direction to global minimum, which
		## can therefore be found without keeping track of the actual frame
		## size at each candidate time
		if (deriv < 0):
			min_time = cur_time
		else:
			max_time = cur_time

	frame = calc_frame_size(points, (min_time + max_time) >> 1)

	if (True):
		xmin  = frame[0]
		xmax  = frame[2]
		ymin  = frame[1]
		ymax  = frame[3]
		xsize = (xmax - xmin) + 1
		ysize = (ymax - ymin) + 1
		pgrid = [' '] * xsize * ysize

		for point in points:
			pos = calc_point_pos(point, frame[4])
			pgrid[(pos[1] - ymin) * xsize + (pos[0] - xmin)] = '#'

		## could use an OCR lib (like pytesseract) here, but KISS
		print("[dbg] frame=%d xsize=%d ysize=%d" % (frame[4], xsize, ysize))
		for y in xrange(ysize):
			print("\t%s" % "".join(pgrid[y * xsize: (y + 1) * xsize]))

	return ("GPJLLLLH", frame[4])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), ("GPJLLLLH", 10515))

