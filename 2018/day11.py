from time import time

TESTS = [
	## serial-num, cell(p1), sqr-size(p1), max-pwr(3x3),  cell(p2), sqr-size(p2), max-pwr(NxN)
	## (   8, (  3,   5), 3,  ?,                     ),
	## (  57, (122,  79), 3,  ?,                     ),
	## (  39, (217, 196), 3,  ?,                     ),
	## (  71, (101, 153), 3,  ?,                     ),
	(  18, ( 33,  45), 3, 29,  ( 90, 269), 16, 113),
	(  42, ( 21,  61), 3, 30,  (232, 251), 12, 119),
	(6392, ( 20,  58), 3, 30,  (233, 268), 13,  83),
]


def make_summed_area_table(grid, xsize, ysize):
	table = [0] * xsize * ysize
	table[0] = grid[0]

	for y in xrange(1, ysize): table[y * xsize + 0] = grid[y * xsize + 0] + table[(y - 1) * xsize +     0]
	for x in xrange(1, xsize): table[0 * xsize + x] = grid[0 * xsize + x] + table[(    0) * xsize + x - 1]

	for y in xrange(1, ysize):
		for x in xrange(1, xsize):
			top = table[(y - 1) * xsize + (x    )]
			lft = table[(y + 0) * xsize + (x - 1)]
			dia = table[(y - 1) * xsize + (x - 1)]

			table[y * xsize + x] = grid[y * xsize + x] + top + lft - dia

	return table


def calc_rectangle_area(table, xsize, x, y, w, h):
	brx = x + w
	bry = y + h

	tl = table[  y * xsize +   x] ## A
	tr = table[  y * xsize + brx] ## B
	bl = table[bry * xsize +   x] ## C
	br = table[bry * xsize + brx] ## D

	return (br + tl - tr - bl)

def calc_rectangle_area_test():
	test_rect = (2, 3, 4, 4) ## x0,y0, x1,y1 (inclusive)
	grid_test = [
		31,  2,  4, 33,  5, 36,
		12, 26,  9, 10, 29, 25,
		13, 17, 21, 22, 20, 18,
		24, 23, 15, 16, 14, 19,
		30,  8, 28, 27, 11,  7,
		 1, 35, 34,  3, 32,  6,
	]

	## calc_rect_area(table, x0 - 1, y0 - 1, x1 - x0, y1 - y0) gives the area of grid sub-rectangle (x0, y0, x1, y1)
	## calc_rect_area(table, 1, 2, 3, 2) sums the area of [15, 16, 14; 28, 27, 11] at (x=2, y=3) with size (w=3, h=2)
	##
	## NB: how should rectangles with x0=0 and/or y0=0 be handled?
	test_table = make_summed_area_table(grid_test, 6, 6)

	rx = test_rect[0] - 1
	ry = test_rect[1] - 1
	rw = (test_rect[2] - test_rect[0]) + 1
	rh = (test_rect[3] - test_rect[1]) + 1

	assert(calc_rectangle_area(test_table, 6,  rx, ry, rw, rh) == 111)


def handle_input(test):
	serial_number = test[0]

	max_sqr_coor = [(0, 0), (0, 0)]
	max_sqr_pwr = -1000000000
	max_sqr_size = 0

	xsize = 300
	ysize = 300

	grid = [0] * xsize * ysize

	for y in xrange(ysize):
		for x in xrange(xsize):
			rack_id = (x + 1) + 10

			pwr_lvl  = rack_id * (y + 1)
			pwr_lvl += serial_number
			pwr_lvl *= rack_id

			grid[y * xsize + x] = ((pwr_lvl / 100) % 10) - 5

	if (True):
		table = make_summed_area_table(grid, xsize, ysize)

		for s in xrange(1, 300 + 1):
			cur_sqr_pwr = 0
			sqr_pwr_sum = 0

			for y in xrange(1, ysize - s):
				for x in xrange(1, xsize - s):
					cur_sqr_pwr = calc_rectangle_area(table, xsize, x - 1, y - 1, s, s)

					if (cur_sqr_pwr > max_sqr_pwr):
						max_sqr_pwr = cur_sqr_pwr
						max_sqr_size = s
						max_sqr_coor[1] = (x + 1, y + 1)

			if (s == test[2]):
				max_sqr_coor[0] = max_sqr_coor[1]

			## print("[dbg] s=%d msc={%s,%s} mss=%d msp=%d" % (s, max_sqr_coor[0], max_sqr_coor[1], max_sqr_size, max_sqr_pwr))

		return (max_sqr_coor[0], max_sqr_coor[1], max_sqr_size)


	for s in xrange(1, 300 + 1):
		cur_sqr_pwr = 0
		sqr_pwr_sum = 0

		## copy initial sub-square data of size SxS
		for y in xrange(0, s):
			for x in xrange(0, s):
				cur_sqr_pwr += grid[y * xsize + x]
				sqr_pwr_sum += grid[y * xsize + x]

		## NB: does not execute a single iteration for s=300
		for y in xrange(ysize - s):
			rt_sum = 0
			rb_sum = 0

			## copy top and bottom sub-square row
			## for j in xrange(s):
			##   RT[j] = grid[(y +     0) * xsize + j]
			##   RB[j] = grid[(y + s - 0) * xsize + j]
			## rt_sum = sum(RT)
			## rb_sum = sum(RB)
			for j in xrange(s):
				rt_sum += grid[(y +     0) * xsize + j]
				rb_sum += grid[(y + s - 0) * xsize + j]


			for x in xrange(xsize - s):
				cl_sum = 0
				cr_sum = 0

				## copy left and right sub-square col
				## for i in xrange(s):
				##   CL[i] = grid[(y + i) * xsize + (x +     0)]
				##   CR[i] = grid[(y + i) * xsize + (x + s - 0)]
				## cl_sum = sum(CL)
				## cr_sum = sum(CR)
				for i in xrange(s):
					cl_sum += grid[(y + i) * xsize + (x +     0)]
					cr_sum += grid[(y + i) * xsize + (x + s - 0)]


				if (cur_sqr_pwr > max_sqr_pwr):
					max_sqr_pwr = cur_sqr_pwr
					max_sqr_size = s
					max_sqr_coor[1] = (x + 1, y + 1)

				## shift sub-square right one column
				cur_sqr_pwr -= cl_sum
				cur_sqr_pwr += cr_sum

			## shift sub-square down one row
			cur_sqr_pwr = sqr_pwr_sum
			cur_sqr_pwr -= rt_sum
			cur_sqr_pwr += rb_sum
			sqr_pwr_sum = cur_sqr_pwr

		if (s == test[2]):
			max_sqr_coor[0] = max_sqr_coor[1]

		## print("[dbg] s=%d msc={%s,%s} mss=%d msp=%d" % (s, max_sqr_coor[0], max_sqr_coor[1], max_sqr_size, max_sqr_pwr))

	return (max_sqr_coor[0], max_sqr_coor[1], max_sqr_size)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

for test in TESTS:
	calc_rectangle_area_test()
	run(test, (test[1], test[4], test[5]))

