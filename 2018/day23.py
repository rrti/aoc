from Queue import PriorityQueue
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		bots = []

		for line in f.readlines():
			m = re_search(r"pos=<(-?[0-9]+),(-?[0-9]+),(-?[0-9]+)>,\s*r=([0-9]+)", line)
			x = int(m.group(1))
			y = int(m.group(2))
			z = int(m.group(3))
			r = int(m.group(4))

			bots.append((x, y, z, r))

		return bots

	return []

def handle_input(bots):
	## radii are much too large to rasterize into an explicit grid
	## coordinates range from ~-20M to ~+20M but space is sparsely
	## filled by only 1000 bots
	## one approach would be to repeatedly sweep the space using an
	## exponentially-decreasing radius; each sweep fully covers the
	## space and is guaranteed to come within a distance <r> of the
	## maximum-coverage coordinate
	xmin =  1000000000
	xmax = -1000000000
	ymin =  1000000000
	ymax = -1000000000
	zmin =  1000000000
	zmax = -1000000000

	rmax = 0
	imax = 0

	def calc_manhattan_dist(a, b):
		dx = a[0] - b[0]
		dy = a[1] - b[1]
		dz = a[2] - b[2]
		return (abs(dx) + abs(dy) + abs(dz))

	## find number of bots visible by bot with number <bot_index>
	def calc_bots_in_range(bot_array, bot_index):
		bot = bot_array[bot_index]

		num = 0

		for i in xrange(len(bot_array)):
			num += (calc_manhattan_dist(bot_array[i], bot) <= bot[3])

		return num

	"""
	def calc_pos_coverage(bot_array, pos):
		n = 0

		for i in xrange(len(bots)):
			n += (calc_manhattan_dist(bot_array[i], pos) <= bot_array[i][3])

		return n

	def coor_in_range(bot, x, y, z):
		return ((abs(bot[0] - x) + abs(bot[1] - y) + abs(bot[2] - z)) <= bot[3])

	def coor_in_range(bot, x, y, z):
		center_dist = abs(bot[0] - x) + abs(bot[1] - y) + abs(bot[2] - z)
		radius_dist = center_dist - bot[3]
		return (radius_dist <= 0)
	"""

	def next_power_of_two(n):
		i = 0
		while (n > 0):
			i += 1
			n >>= 1
		return (1 << i)

	def calc_max_coverage_coor(xmin, ymin, zmin, xmax, ymax, zmax, rmax):
		def bot_clips_bbox(bot, bbox_xmin, bbox_ymin, bbox_zmin, bbox_xmax, bbox_ymax, bbox_zmax):
			## test if this bot's octahedral sensor-volume
			## intersects the bbox {x,y,z}min - {x,y,z}max
			assert(bbox_xmin <= bbox_xmax)
			assert(bbox_ymin <= bbox_ymax)
			assert(bbox_zmin <= bbox_zmax)

			dist = 0

			dist += (bbox_xmin - bot[0]) * (bot[0] < bbox_xmin)
			dist += (bot[0] - bbox_xmax) * (bot[0] > bbox_xmax)

			dist += (bbox_ymin - bot[1]) * (bot[1] < bbox_ymin)
			dist += (bot[1] - bbox_ymax) * (bot[1] > bbox_ymax)

			dist += (bbox_zmin - bot[2]) * (bot[2] < bbox_zmin)
			dist += (bot[2] - bbox_zmax) * (bot[2] > bbox_zmax)

			return (dist <= bot[3])

		def pq_add(pq, bbox_xmin, bbox_ymin, bbox_zmin, cur_bbox_size):
			bbox_xmax = bbox_xmin + cur_bbox_size - 1
			bbox_ymax = bbox_ymin + cur_bbox_size - 1
			bbox_zmax = bbox_zmin + cur_bbox_size - 1

			num_bots_in_bbox = 0

			for bot in bots:
				num_bots_in_bbox += bot_clips_bbox(bot, bbox_xmin, bbox_ymin, bbox_zmin, bbox_xmax, bbox_ymax, bbox_zmax)

			if (num_bots_in_bbox == 0):
				return False

			## find Manhattan distance from origin to the closest corner of the bounding-box
			## box with largest number of bots clipping it should be processed first, negate
			## the count since PQ is constructed as a min-heap
			## in case of ties, PQ will yield the box with smallest origin distance and size
			## (ordering by size first and distance second also works and is slightly faster
			## on the given input)
			## this processing order ensures the problem is solved when reaching a 1x1x1 box
			## since 1) no larger box can intersect more bot sensor-volumes, and 2) no other
			## 1x1x1 box intersecting as many sensor-volumes can be closer to the origin
			##
			min_orig_dist_x = min(abs(bbox_xmin), abs(bbox_xmax))
			min_orig_dist_y = min(abs(bbox_ymin), abs(bbox_ymax))
			min_orig_dist_z = min(abs(bbox_zmin), abs(bbox_zmax))
			min_orig_dist   = min_orig_dist_x + min_orig_dist_y + min_orig_dist_z

			##!! pq.put((-num_bots_in_bbox, min_orig_dist, cur_bbox_size, bbox_xmin, bbox_ymin, bbox_zmin))
			pq.put((-num_bots_in_bbox, cur_bbox_size, min_orig_dist, bbox_xmin, bbox_ymin, bbox_zmin))
			return True

		## determine size of the power-of-two bounding cube
		max_size = max(xmax - xmin, ymax - ymin, zmax - zmin, rmax)
		bbox_size = next_power_of_two(max_size)

		bbox_queue = PriorityQueue()

		pq_add(bbox_queue, xmin, ymin, zmin, bbox_size)

		while (bbox_queue.qsize() > 0):
			##!! (num_bots, orig_dist, bb_size, x, y, z) = bbox_queue.get()
			(num_bots, bb_size, orig_dist, x, y, z) = bbox_queue.get()

			if (bb_size == 1):
				return ((x, y, z), orig_dist, -num_bots)

			bb_size >>= 1

			## insert top-left corner coordinates of each child bounding-box
			pq_add(bbox_queue, x          , y          , z          , bb_size)
			pq_add(bbox_queue, x          , y          , z + bb_size, bb_size)
			pq_add(bbox_queue, x          , y + bb_size, z          , bb_size)
			pq_add(bbox_queue, x          , y + bb_size, z + bb_size, bb_size)
			pq_add(bbox_queue, x + bb_size, y          , z          , bb_size)
			pq_add(bbox_queue, x + bb_size, y          , z + bb_size, bb_size)
			pq_add(bbox_queue, x + bb_size, y + bb_size, z          , bb_size)
			pq_add(bbox_queue, x + bb_size, y + bb_size, z + bb_size, bb_size)

		return ((0, 0, 0), 0, 0)


	## find bot with largest sensor radius
	for i in xrange(len(bots)):
		bot = bots[i]

		xmin = min(xmin, bot[0])
		ymin = min(ymin, bot[1])
		zmin = min(zmin, bot[2])
		xmax = max(xmax, bot[0])
		ymax = max(ymax, bot[1])
		zmax = max(zmax, bot[2])

		if (bot[3] > rmax):
			rmax = bot[3]
			imax = i

	n = calc_bots_in_range(bots, imax)
	c = calc_max_coverage_coor(xmin, ymin, zmin, xmax, ymax, zmax, rmax)

	print("[dbg::1] max_sensor_radius=%d bot_index=%d bots_in_range=%d" % (rmax, imax, n))
	print("[dbg::2] max_coverage_coor=%s origin_distance=%d bots_in_range=%d" % (c[0], c[1], c[2]))
	return (n, c[1])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  6,       36))
run(parse_input(__file__[: -2] + "in"     ), (599, 94481130))

