def calc_manhattan_dist(x1, y1,  x2, y2): return (abs(x1 - x2) + abs(y1 - y2))
def calc_manhattan_dist_c(c1, c2): return (calc_manhattan_dist(c1[0], c1[1], c2[0], c2[1]))
	

def value_to_coors(n):
	assert(n > 0)

	if (n == 1):
		return (0, 0)

	i = n - 2
	j = 1

	## stackoverflow.com/questions/3706219/algorithm-for-iterating-over-an-outward-spiral-on-a-discrete-2d-grid-from-the-or
	## jump backward along (the corners of) the four spiral arms until i is in range
	## corner indices are 2,4,6,8, (+4) 12,16,20,24, (+6) 30,36,42,48, (+8) ..., etc
	while (True):
		if (i < (2 * j)):
			return (j, -(j - 1) + i)
		if (i < (4 * j)):
			return ((j - 1) - (i - 2 * j), j)
		if (i < (6 * j)):
			return (-j, (j - 1) - (i - 4 * j))
		if (i < (8 * j)):
			return (-(j - 1) + (i - 6 * j), -j)

		i -= (8 * j)
		j += 1

	assert(False)
	return (-1, -1)

def expand_fill_spiral_grid(num):
	def expand_grid(grid):
		## turn the grid 90 degrees clockwise, then add a row of zeros
		##
		## >>> L = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
		## >>> zip(*L[: :  1])   [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
		## >>> zip(*L[: : -1])   [(7, 4, 1), (8, 5, 2), (9, 6, 3)]
		##
		## last step just turns tuples into lists again
		grid = zip(*grid[: : -1])
		grid = [list(i) for i in grid]

		return grid + [[0] * len(grid[0])]

	def fill_spiral(grid):
		assert(len(grid) >= 2)

		zero_row = grid[-1]
		prev_row = grid[-2]

		## replace zeros with the sum of their non-zero neighbours
		while (0 in zero_row):
			index = zero_row.index(0)

			if ((index + 0) < len(prev_row)):
				zero_row[index] += prev_row[index + 0]

			if ((index + 1) < len(prev_row)):
				zero_row[index] += prev_row[index + 1]

			if (index > 0):
				zero_row[index] += prev_row[index - 1]
				zero_row[index] += zero_row[index - 1]

		return grid


	grid = [[1]]

	## faster solution for part 2
	while (grid[-1][-1] < num):
		grid = expand_grid(grid)
		grid = fill_spiral(grid)

	return (grid[-1][0])



def gen_square(size):
	assert((size & 1) == 1)

	t = {}
	s = [None] * size
	k = size / 2

	for j in xrange(-k, k + 1):	
		s[j + k] = [None] * size

		for i in xrange(-k, k + 1):
			## t[(i, j)] = calc_manhattan_dist(0, 0, i, j)
			s[j + k][i + k] = (i, j, calc_manhattan_dist(0, 0, i, j))

	return (s, t)

def calc_square_size(num):
	square_size = 1
	center_dist = 0

	while (num > (square_size * square_size)):
		square_size += 2
		center_dist += 1

	## calculates the index of the square in which <num> can be found
	## this puts an upper bound on the center distance but is not the
	## actual value (square <i> has sides of length <2*i-1>)
	##
	## square_indx = (square_size / 2) + 1
	## square_base = max(0, square_size - 2) * max(0, square_size - 2) + 1
	## square_next =    (   square_size    ) *    (   square_size    ) + 1
	## square_diff = num - square_base
	return square_size



def gen_spiral(tgt_value, ccw = 1):
	assert(ccw == 0 or ccw == 1)

	## generator sequence is [up, left, down, right]; repeated ad-infinitum
	## step-sizes (starting at the square with value 2) increment every two
	## spiral rotations:
	##
	##   1,2,2,3  (U,L,D,R; CCW  2 to 10)
	##   3,4,4,5  (U,L,D,R; CCW 10 to 26)
	##   5,6,6,7  (U,L,D,R; CCW 26 to 50)
	##
	##     37  36   35  34  33   32   31
	##     38  17   16  15  14   13   30
	##
	##     39  18    5   4   3   12   29
	##     40  19    6   1   2   11   28
	##     41  20    7   8   9   10   27
	##
	##     42  21   22  23  24   25   26
	##     43  44   45  46  47   48   49   50
	##
	## square 1: area=1x1= 1, values up to  1 (dist <= 0)
	## square 2: area=3x3= 9, values up to  9 (dist <= 2)
	## square 3: area=5x5=25, values up to 25 (dist <= 4)
	## square 4: area=7x7=49, values up to 49 (dist <= 6)
	## square 5: area=9x9=81, values up to 81 (dist <= 8)
	##
	## first value of i-th square (1=0*0+1, 2=1*1+1, 10=3*3+1,
	## 26=5*5+1, 50=7*7+1, ...) is always next to bottom-right
	## corner of previous square, corners are on the diagonals
	##
	init_coor = [(-1, 0), (+1, 0)] ## CW, CCW
	step_dirs = [
		[(0, +1), (+1, 0), (0, -1), (-1, 0)], ## CW
		[(0, +1), (-1, 0), (0, -1), (+1, 0)], ## CCW
	]

	xpos = init_coor[ccw][0]
	ypos = init_coor[ccw][1]
	dirs = step_dirs[ccw]

	step_size = 1   ## current step-size
	num_steps = 0   ## steps taken along dir

	dir_index = 0   ## current spiral direction
	cur_value = 2   ## value at current square

	## data for part 2
	ngb_sums = {(0, 0): 1}
	ngb_vecs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
	ngb_sum = -1

	def calc_ngb_sum(_sums, _vecs, xp, yp):
		s = 0

		## iterate only over candidate neighbors rather than all table entries added so far
		for ngb in _vecs:
			c = (xp + ngb[0], yp + ngb[1])
			s += _sums.get(c, 0)

		return s


	while (cur_value < tgt_value):
		## part 2
		if (ngb_sum < 0):
			pos_sum = calc_ngb_sum(ngb_sums, ngb_vecs, xpos, ypos)
			ngb_sums[ (xpos, ypos) ] = pos_sum

			if (pos_sum > tgt_value):
				ngb_sum = pos_sum

		xpos += dirs[dir_index][0]
		ypos += dirs[dir_index][1]
		num_steps += 1
		cur_value += 1


		"""
		turn = (num_steps >= step_size)
		num_steps *= (1 - turn)
		dir_index += turn
		dir_index %= 4
		step_size += ((dir_index == 1) * turn)
		step_size += ((dir_index == 3) * turn)
		continue
		"""

		## change of direction every <step_size> squares; increment
		## the step-size during up-left and down-right transitions
		## ~100ms faster than the branch-free version above
		if (num_steps < step_size):
			continue

		num_steps = 0
		dir_index += 1
		dir_index %= 4
		step_size += (dir_index == 1)
		step_size += (dir_index == 3)

	return (calc_manhattan_dist(0, 0, xpos, ypos), ngb_sum)


assert(gen_spiral(    12, 1) == (  3,     23))
assert(gen_spiral(    23, 1) == (  2,     25))
assert(gen_spiral(  1024, 1) == ( 31,   1968))
assert(gen_spiral(368078, 1) == (371, 369601))

assert(calc_manhattan_dist_c(value_to_coors(    12), (0, 0)) ==   3)
assert(calc_manhattan_dist_c(value_to_coors(    23), (0, 0)) ==   2)
assert(calc_manhattan_dist_c(value_to_coors(  1024), (0, 0)) ==  31)
assert(calc_manhattan_dist_c(value_to_coors(368078), (0, 0)) == 371)

assert(expand_fill_spiral_grid(368078) == 369601)

