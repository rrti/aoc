class point_bin:
	def __init__(self): self.points = []

	def add_point(self, p): self.points.append(p)
	def get_point(self, i): return self.points[i]

	def get_size(self): return (len(self.points))

class point_bin_grid:
	def __init__(self, num_bins, bin_dims):
		self.num_bins = num_bins
		self.bin_dims = bin_dims

		self.bins = [point_bin() for i in xrange(num_bins[0] * num_bins[1])]

	## assumes point coordinates are in [0, num_bins * bin_dims]
	def calc_bin_coors(self, p):
		x = max(0, min(self.num_bins[0] - 1, int(p[0] / self.bin_dims[0])))
		y = max(0, min(self.num_bins[1] - 1, int(p[1] / self.bin_dims[1])))
		return (x, y)


	def get_idx_bin(self, idx):
		assert(idx < len(self.bins))
		return self.bins[idx]

	def get_bin(self, c):
		assert((c[0] * c[1]) < len(self.bins))
		return self.bins[c[1] * self.num_bins[0] + c[0]]

	## NB:
	##   it is possible to construct data sets such that points of the
	##   largest-distance pair are not both in an edge bin (regardless
	##   of distance metric), which can only be solved by making edges
	##   N >= 2 bins thick
	##   the exact value of N depends on cell-size, overall point-grid
	##   effectiveness is also decreased when points are not uniformly
	##   distributed
	def get_edge_bin_indices(self):
		idcs = {}
		bins = self.bins

		nbx = self.num_bins[0]
		nby = self.num_bins[1]

		## for each row: work L2R from col 0 and R2L from col N-1
		for row_idx in xrange(0, nby):
			min_col_idx = 0
			max_col_idx = nbx - 1

			while (bins[row_idx * nbx + min_col_idx].get_size() == 0 and min_col_idx < max_col_idx):
				min_col_idx += 1

			while (bins[row_idx * nbx + max_col_idx].get_size() == 0 and max_col_idx > min_col_idx):
				max_col_idx -= 1

			min_col_idx_c = min(min_col_idx + 1, nbx - 1)
			max_col_idx_c = max(max_col_idx - 1,       0)

			if (bins[row_idx * nbx + min_col_idx  ].get_size() != 0): idcs[row_idx * nbx + min_col_idx  ] = 1
			if (bins[row_idx * nbx + min_col_idx_c].get_size() != 0): idcs[row_idx * nbx + min_col_idx_c] = 1

			if (bins[row_idx * nbx + max_col_idx  ].get_size() != 0): idcs[row_idx * nbx + max_col_idx  ] = 1
			if (bins[row_idx * nbx + max_col_idx_c].get_size() != 0): idcs[row_idx * nbx + max_col_idx_c] = 1

		## for each col: work T2B from row 0 and B2T from row N-1
		for col_idx in xrange(0, nbx):
			min_row_idx = 0
			max_row_idx = nby - 1

			while (bins[min_row_idx * nbx + col_idx].get_size() == 0 and min_row_idx < max_row_idx):
				min_row_idx += 1

			while (bins[max_row_idx * nbx + col_idx].get_size() == 0 and max_row_idx > min_row_idx):
				max_row_idx -= 1

			min_row_idx_c = min(min_row_idx + 1, nby - 1)
			max_row_idx_c = max(max_row_idx - 1,       0)

			if (bins[min_row_idx   * nbx + col_idx].get_size() != 0): idcs[min_row_idx   * nbx + col_idx] = 1
			if (bins[min_row_idx_c * nbx + col_idx].get_size() != 0): idcs[min_row_idx_c * nbx + col_idx] = 1

			if (bins[max_row_idx   * nbx + col_idx].get_size() != 0): idcs[max_row_idx   * nbx + col_idx] = 1
			if (bins[max_row_idx_c * nbx + col_idx].get_size() != 0): idcs[max_row_idx_c * nbx + col_idx] = 1


		return (idcs.keys())




def exec_move_list(move_list, move_dirs):
	points = []

	xpos = 0
	ypos = 0

	for move in move_list:
		if (move in move_dirs):
			xpos += move_dirs[move][0]
			ypos += move_dirs[move][1]
		else:
			points.append((xpos, ypos))

	return points


def calc_point_bounds(points, bounds):
	## expand bounding-box around each marker
	for point in points:
		bounds[0] = min(bounds[0], point[0])
		bounds[1] = min(bounds[1], point[1])
		bounds[2] = max(bounds[2], point[0])
		bounds[3] = max(bounds[3], point[1])
		## part 1; maximum distance of any marker from origin
		bounds[4] = max(bounds[4], abs(point[0]) + abs(point[1]))

	return bounds


def calc_max_pair_dist_nogrid(points):
	max_pair_dist = 0
	num_cmp_pairs = 0

	for m1 in points:
		for m2 in points:
			max_pair_dist = max(max_pair_dist, abs(m1[0] - m2[0]) + abs(m1[1] - m2[1]))
			num_cmp_pairs += 1

	return max_pair_dist


def calc_max_pair_dist(points, bounds, num_bins, bin_size, test_case):
	assert(num_bins[0] > 0)
	assert(num_bins[1] > 0)
	assert(bin_size[0] > 0)
	assert(bin_size[1] > 0)

	pb_grid = point_bin_grid(num_bins, bin_size)

	if (test_case):
		for point in points:
			## grid origin is top-left but test-case wants it bottom-left
			bin_coors = pb_grid.calc_bin_coors((point[0] - bounds[0] * 0, (num_bins[1] * bin_size[1]) - point[1]))
			point_bin = pb_grid.get_bin(bin_coors)

			point_bin.add_point(point)
	else:
		for point in points:
			bin_coors = pb_grid.calc_bin_coors((point[0] - bounds[0], point[1] - bounds[1]))
			point_bin = pb_grid.get_bin(bin_coors)

			point_bin.add_point(point)


	edge_bin_indcs = pb_grid.get_edge_bin_indices()
	num_edge_indcs = len(edge_bin_indcs)

	max_pair_dist = 0
	num_cmp_pairs = 0

	for a in xrange(num_edge_indcs):
		edge_bin_idx_i = edge_bin_indcs[a]
		edge_bin_i = pb_grid.get_idx_bin(edge_bin_idx_i)

		## start at a + 0 iff a single bin is used; otherwise unlikely
		## the largest-distance pair will be found within a single bin
		for b in xrange(a + (num_edge_indcs != 1), num_edge_indcs):
			edge_bin_idx_j = edge_bin_indcs[b]
			edge_bin_j = pb_grid.get_idx_bin(edge_bin_idx_j)

			for i in xrange(edge_bin_i.get_size()):
				pi = edge_bin_i.get_point(i)

				for j in xrange(edge_bin_j.get_size()):
					pj = edge_bin_j.get_point(j)

					max_pair_dist = max(max_pair_dist, abs(pi[0] - pj[0]) + abs(pi[1] - pj[1]))
					num_cmp_pairs += 1

	return max_pair_dist


def parse_input(fn):
	with open(fn, 'r') as f:
		moves_string = f.read()
		moves_string = moves_string.strip("\n")
		return (moves_string.split(", "))


def run(move_list, move_dirs, coor_bounds, test_case):
	if (not test_case):
		points = exec_move_list(move_list, move_dirs)
		bounds = calc_point_bounds(points, coor_bounds)

		num_bins = (15 * 1, 15 * 1)
		bin_size = (max(1, (bounds[2] - bounds[0]) / num_bins[0]), max(1, (bounds[3] - bounds[1]) / num_bins[1]))

		max_dist = calc_max_pair_dist(points, bounds, num_bins, bin_size, False)
		## max_dist = calc_max_pair_dist_nogrid(points)
	else:
		## hand-crafted distribution; requires a two-bin boundary layer
		points = [(11, 29), (39, 11), (35, 25), (15, 11), ( 9, 21), (19, 31)]
		bounds = calc_point_bounds(points, coor_bounds)

		num_bins = ( 4,  4)
		bin_size = (10, 10)

		max_dist = calc_max_pair_dist(points, bounds, num_bins, bin_size, True)

	return (bounds[4], max_dist)


MOVE_DIRS = {
	"Right": ( 1,  0),
	"Left" : (-1,  0),
	"Up"   : ( 0,  1),
	"Down" : ( 0, -1),
}

COOR_BOUNDS = [
	+1000000, ## xmin
	+1000000, ## ymin
	-1000000, ## xmax
	-1000000, ## ymax
	0
]

assert(run(parse_input("day00.in"), MOVE_DIRS, COOR_BOUNDS[:], False) == (86, 137))
assert(run(parse_input("day00.in"), MOVE_DIRS, COOR_BOUNDS[:],  True) == (60,  46))

