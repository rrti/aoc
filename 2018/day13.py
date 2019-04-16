from collections import defaultdict as ddict
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		track = [ line[: -1] for line in lines]
		return track

	return []

def handle_input(track):
	cart_objs = []
	move_dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)] ## u,r,d,l
	dir_indcs = {'^': 0, 'v': 2, '<': 3, '>': 1}

	r_coll_coor = (-1, -1)
	r_cart_coor = (-1, -1)

	## "Each time a cart has the option to turn (by arriving at any intersection),
	## it turns left the first time, goes straight the second time, turns right the
	## third time, and then repeats those directions starting again with left the
	## fourth time, straight the fifth time, and so on."
	##
	## "Carts all move at the same speed; they take turns moving a single step at
	## a time. They do this based on their current location: carts on the top row
	## move first (acting from left to right), then carts on the second row move
	## (again from left to right), then carts on the third row, and so on. Once
	## each cart has moved one step, the process repeats; each of these loops is
	## called a tick.
	##
	class cart:
		def __init__(self, cart_num, cart_pos, dir_indx, isec_ctr = 0):
			self.cart_num = cart_num
			self.cart_pos = cart_pos

			self.isec_ctr = isec_ctr
			self.dir_indx = dir_indx

			## left first time, straight second time, right third time
			self.turn_funcs = ddict(
				lambda: (self.noop, self.noop, self.noop),
				[
					('+' , (self.turn_l, self.turn_x, self.turn_r)),
					('/' , (self.turn  , self.turn  , self.turn  )),
					('\\', (self.turn  , self.turn  , self.turn  ))
				]
			)

		def __lt__(self, c):
			if (self.cart_pos[1] < c.cart_pos[1]): return  True
			if (self.cart_pos[1] > c.cart_pos[1]): return False
			return (self.cart_pos[0] < c.cart_pos[0])
		def __repr__(self):
			return ("<id=%d pos=<%d,%d> dir=<%+d,%+d> ctr=%d" % (self.cart_num, self.cart_pos[0], self.cart_pos[1], move_dirs[self.dir_indx][0], move_dirs[self.dir_indx][1], self.isec_ctr))

		def get_pos(self): return (self.cart_pos[0], self.cart_pos[1])
		def get_dir(self): return move_dirs[self.dir_indx]

		def turn_x(self, tp, k = 0):
			assert(tp == '+')
			self.dir_indx += k
			self.dir_indx %= len(move_dirs)
			self.isec_ctr += 1
			self.isec_ctr %= 3
		def turn_l(self, tp): self.turn_x(tp, -1)
		def turn_r(self, tp): self.turn_x(tp, +1)

		def turn(self, tp):
			assert(tp == '/' or tp == '\\')

			## if moving right or left, '\' track-piece forces a RH turn (idx + 1)
			## if moving down or up, '\' track-piece forces a LH turn (idx - 1)
			move_dir = self.get_dir()
			turn_mul = (move_dir[0] != 0) * 2 - 1

			self.dir_indx += ((tp == '\\') * turn_mul)
			self.dir_indx -= ((tp ==  '/') * turn_mul)
			self.dir_indx %= len(move_dirs)

		def noop(self, _): pass
		def move(self):
			self.cart_pos[0] += move_dirs[self.dir_indx][0]
			self.cart_pos[1] += move_dirs[self.dir_indx][1]

		def tick(self, track):
			cp = self.cart_pos
			tp = track[ cp[1] ][ cp[0] ]

			## cart must always stay on track
			assert(tp != ' ')

			self.turn_funcs[tp][self.isec_ctr](tp)
			self.move()

			return (self.get_pos())

	def tick_carts(track, carts):
		## collision logic is (or should be) order-independent, but KISS
		carts.sort()

		dead_carts = []
		dead_indcs = set()
		coll_dict = ddict(lambda: [])

		for i in xrange(len(carts)):
			coll_dict[ carts[i].get_pos() ].append(i)

		for i in xrange(len(carts)):
			## cart is going to move out of cell it previously occupied, so mark as free
			## this can not handle situations where cart A moves onto a cell while cart B
			## moves out of it, i.e. does not assume collisions only occur when two carts
			## move onto the same cell
			## thus it catches "swap"-type collisions, for example the following scenario
			##   [t=984] cart 16 ticks, moves from (96, 53) onto (97, 53) occupied by cart 9
			##     [(96, 53) is now free; (97, 53) contains both carts]
			##   [t=984] cart 9 ticks, moves from (97, 53) onto (96, 53) where cart 16 came from
			## technically cart 9 no longer has to be ticked here, since it will be removed
			## along with cart 16 after tick_carts returns and can no longer participate in
			## other collisions
			## coll_dict[ carts[i].get_pos() ].remove(i)

			if (i in dead_indcs):
				continue

			cart_coor = carts[i].tick(track)
			coll_list = coll_dict[cart_coor]

			## NB: dead_carts will contain duplicates if four carts arrive at the same intersection on the same tick
			if (len(coll_list) >= 1):
				dead_carts.append((coll_list[-1], cart_coor))
				dead_carts.append((i, cart_coor))

				dead_indcs.add(coll_list[-1])
				dead_indcs.add(i)

			coll_list.append(i)

		return dead_carts

	def find_carts(track, carts, dirs):
		for row_idx in xrange(len(track)):
			row_str = track[row_idx]

			## find initial cart locations
			for dir_key in dirs.keys():
				col_idx = -1

				while (True):
					col_idx = row_str.find(dir_key, col_idx + 1)

					if (col_idx == -1):
						break

					carts.append(cart(len(carts), [col_idx, row_idx], dirs[dir_key], 0))

	def remove_dead_carts(carts, dead_carts):
		k = 0

		for dead_cart in dead_carts:
			carts[ dead_cart[0] ] = None

		for j in xrange(len(carts)):
			if (carts[j] == None):
				continue

			carts[k] = carts[j]
			k += 1

		while (len(carts) > k):
			carts.pop()

	find_carts(track, cart_objs, dir_indcs)

	for i in xrange(15000):
		dead_carts = tick_carts(track, cart_objs)

		assert((len(dead_carts) % 2) == 0)

		for dead_cart in dead_carts:
			coll_coor = dead_cart[1]

			## save coordinates of very first collision
			if (r_coll_coor[0] < 0):
				r_coll_coor = coll_coor

			print("[dbg][tick=%d] removing dead cart %d at coor (%d, %d) (#carts=%d)" % (i, cart_objs[dead_cart[0]].cart_num, coll_coor[0], coll_coor[1], len(cart_objs)))

		remove_dead_carts(cart_objs, dead_carts)

		if (len(cart_objs) == 1):
			## save coordinates of last surviving cart
			r_cart_coor = cart_objs[0].get_pos()
			break

	return (r_coll_coor, r_cart_coor)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test1"), (( 7,  3), (-1, -1))) ##  2 carts, 0 survivors
run(parse_input(__file__[: -2] + "in.test2"), (( 2,  0), ( 6,  4))) ##  9 carts, 1 survivor
run(parse_input(__file__[: -2] + "in.test3"), (( 8,  4), ( 4,  4))) ##  5 carts, 1 survivor
run(parse_input(__file__[: -2] + "in"      ), ((38, 72), (68, 27))) ## 17 carts, 1 survivor

