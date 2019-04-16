from collections import defaultdict as ddict
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		coords = [re_search(r"(-?[0-9]+),\s*(-?[0-9]+),\s*(-?[0-9]+),\s*(-?[0-9]+)", line) for line in f.readlines()]
		points = [(int(c.group(1)), int(c.group(2)), int(c.group(3)), int(c.group(4))) for c in coords]

		return points

	return []

def handle_input(points):
	def calc_point_dist(a, b):
		dx = a[0] - b[0]
		dy = a[1] - b[1]
		dz = a[2] - b[2]
		dw = a[3] - b[3]
		return (abs(dx) + abs(dy) + abs(dz) + abs(dw))

	def pop_left(L):
		p = L[0]
		L.reverse()
		L.pop()
		L.reverse()
		return p



	class point_cluster:
		def __init__(self, p):
			self.points = []

			self.init_bb()
			self.grow_bb(p)

		def init_bb(self):
			self.bb_mins = [ 1000000000,  1000000000,  1000000000,  1000000000]
			self.bb_maxs = [-1000000000, -1000000000, -1000000000, -1000000000]

		def test_bb(self, p, r):
			for i in xrange(len(p)):
				if ((self.bb_mins[i] - p[i]) > r):
					return False
				if ((p[i] - self.bb_maxs[i]) > r):
					return False

			return True

		def grow_bb(self, p):
			self.points.append(p)

			## keep a bounding-box per constellation to quickly reject points
			for i in xrange(len(p)):
				self.bb_mins[i] = min(self.bb_mins[i], p[i])
				self.bb_maxs[i] = max(self.bb_maxs[i], p[i])

		def expand(self, p, r):
			if (not self.test_bb(p, r)):
				return False

			for point in self.points:
				if (calc_point_dist(p, point) <= r):
					self.grow_bb(p)
					return True

			return False

	class hash_grid:
		def __init__(self, points):
			self.cells = ddict(lambda: set())

			self.xmin = 1000000000; self.xmax = -1000000000
			self.ymin = 1000000000; self.ymax = -1000000000
			self.zmin = 1000000000; self.zmax = -1000000000
			self.wmin = 1000000000; self.wmax = -1000000000

			for p in points:
				self.xmin = min(p[0], self.xmin); self.xmax = max(p[0], self.xmax)
				self.ymin = min(p[1], self.ymin); self.ymax = max(p[1], self.ymax)
				self.zmin = min(p[2], self.zmin); self.zmax = max(p[2], self.zmax)
				self.wmin = min(p[3], self.wmin); self.wmax = max(p[3], self.wmax)

			## cell-dimensions along each axis
			## points spaced more than 1 cell apart (i.e. at least
			## 4 Manhattan distance units) can never form clusters
			self.xdim = max(4, (self.xmax - self.xmin) / 4)
			self.ydim = max(4, (self.ymax - self.ymin) / 4)
			self.zdim = max(4, (self.zmax - self.zmin) / 4)
			self.wdim = max(4, (self.wmax - self.wmin) / 4)

			for p in points:
				self.insert_point(p)

		def insert_point(self, p):
			self.cells[self.get_grid_index(p)].add(p)
		def remove_point(self, p):
			self.cells[self.get_grid_index(p)].remove(p)

		def get_grid_cell(self, p):
			return self.cells[self.get_grid_index(p)]
		def get_grid_index(self, p):
			xi = (p[0] - self.xmin) / self.xdim
			yi = (p[1] - self.ymin) / self.ydim
			zi = (p[2] - self.zmin) / self.zdim
			wi = (p[3] - self.wmin) / self.wdim
			return (xi, yi, zi, wi)

		def get_ngb_points(self, p, r):
			ngbs = []

			assert(r <= 4)

			## O(3*3*3*3)=O(81) to visit all neighbors in 4D
			for x in xrange(-1, 1 + 1):
				xi = ((p[0] - self.xmin) / self.xdim) + x

				for y in xrange(-1, 1 + 1):
					yi = ((p[1] - self.ymin) / self.ydim) + y

					for z in xrange(-1, 1 + 1):
						zi = ((p[2] - self.zmin) / self.zdim) + z

						for w in xrange(-1, 1 + 1):
							wi = ((p[3] - self.wmin) / self.wdim) + w
							ki = (xi, yi, zi, wi)

							for ngb in self.cells[ki]:
								if (calc_point_dist(p, ngb) <= r):
									ngbs.append(ngb)

			return ngbs



	if (True):
		point_cloud = set(points)
		point_grid = hash_grid(points)
		point_clusts = []

		while (len(point_cloud) > 0):
			## BFS-expand each cluster around a random starting point
			point_queue = [point_cloud.pop()]
			point_clust = []

			## reinsert into point-set; this simplifies the inner loop
			point_cloud.add(point_queue[0])
			point_grid.remove_point(point_queue[0])

			while (len(point_queue) > 0):
				cur_point = pop_left(point_queue)

				point_clust.append(cur_point)
				point_cloud.remove(cur_point)

				assert(not (cur_point in point_grid.get_grid_cell(cur_point)))

				ngb_points = point_grid.get_ngb_points(cur_point, 3)
				point_queue += ngb_points

				## remove each found neighbor from its grid-cell
				for ngb_point in ngb_points:
					point_grid.remove_point(ngb_point)

			point_clusts.append(point_clust)

		return (len(point_clusts), 0)

	else:
		point_cloud = set(points)
		point_clusts = [point_cluster(point_cloud.pop())]

		## basic approach does not work because cluster-expansion
		## depends on point iteration order, need multiple passes
		while (len(point_cloud) > 0):
			c = None

			for point_clust in point_clusts:
				p = None
				s = []

				for point in point_cloud:
					if (point_clust.expand(point, 3)):
						s.append(point)

				if (len(s) > 0):
					c = point_clust
					for p in s:
						point_cloud.remove(p)

			## if no point was added to any cluster, spawn a new one
			if (c == None):
				assert(len(point_cloud) > 0)
				point_clusts.append(point_cluster(point_cloud.pop()))

		return (len(point_clusts), 0)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test1"), (  2, 0))
run(parse_input(__file__[: -2] + "in.test2"), (  4, 0))
run(parse_input(__file__[: -2] + "in.test3"), (  3, 0))
run(parse_input(__file__[: -2] + "in.test4"), (  8, 0))
run(parse_input(__file__[: -2] + "in"      ), (373, 0))

