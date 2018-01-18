##  initial fixed 3x3 pattern (010/001/111=2/1/7)
GRID_STR = ".#./..#/###"

## example 2x2 and 3x3 expansion rules
RULE_STRS = ["../.# => ##./#../...", ".#./..#/### => #..#/..../..../#..#"]


def print_grid(g):
	sg_size = 3 - ((len(g) & 1) == 0)
	num_sgs = len(g) / sg_size

	s = ""

	for i in xrange(len(g)):
		if (i > 0 and (i % sg_size) == 0):
			s += "\n\n"

		s += "\t"

		for j in xrange(len(g[i])):
			if (j > 0 and (j % sg_size) == 0):
				s += "  "

			s += g[i][j]

		s += "\n"

	print("%s" % s)


def count_pixels(g, c = '#'):
	return (sum(g[i][j] == c for i in xrange(len(g)) for j in xrange(len(g))))


def parse_input(fn):
	with open(fn, 'r') as f:
		raw_rules = f.readlines()
		for i in xrange(len(raw_rules)):
			raw_rules[i] = raw_rules[i].strip("\n")
		return raw_rules

def make_rules_dict(rules_list):
	rules_dict = {}

	for i in xrange(len(rules_list)):
		rule = rules_list[i].split(" => ")
		head = rule[0]
		tail = rule[1]

		rules_dict[head] = tail

		## pregenerate rule transformations; duplicates are filtered by dict
		rule_transform_grids = get_rule_transform_grids(string_to_grid(head))

		for rule_transform_grid in rule_transform_grids:
			rules_dict[grid_to_string(rule_transform_grid)] = tail

	return rules_dict



## convert a "../.#" formatted string to a grid (list of lists of chars); easier to transform
def string_to_grid(s):
	assert(type(s) == str)
	rows = s.split("/")
	grid = [list(row) for row in rows]
	return grid

def grid_to_string(g):
	assert(type(g   ) == list)
	assert(type(g[0]) == list)

	s = ""
	t = ("", "/")
	n = len(g) - 1

	for i in xrange(n + 1):
		r = g[i]
		## no slash terminating last row
		s += ("".join(r))
		s += t[i < n]

	return s


def get_rule_transform_grids(rule_grid):
	assert(type(rule_grid) == list)

	tgs = []
	rtg = rule_grid

	for i in xrange(4):
		rtg = rotate_grid_cw(rtg)
		mgh = mirror_grid_h(rtg)
		mgv = mirror_grid_v(rtg)

		tgs.append(rtg)
		tgs.append(mgh)
		tgs.append(mgv)

	return tgs

def rotate_grid_cw(g):
	assert(type(g   ) == list)
	assert(type(g[0]) == list)
	## 90-degree clockwise rotation
	rg = zip(*g[: : -1])
	rg = [list(i) for i in rg]
	return rg

def mirror_grid_v(g):
	assert(type(g   ) == list)
	assert(type(g[0]) == list)

	mg = [ None for i in xrange(len(g)) ]
	mg[len(g) / 2] = g[len(g) / 2][:]

	for i in xrange(len(g) / 2):
		j = len(g) - i - 1

		mg[j] = g[i][:]
		mg[i] = g[j][:]

	return mg

def mirror_grid_h(g):
	assert(type(g   ) == list)
	assert(type(g[0]) == list)

	mg = [ None for i in xrange(len(g)) ]

	## flip each row horizontally
	for i in xrange(len(g)):
		mg[i] = g[i][:]
		mg[i].reverse()

	return mg


def get_grid_rule(s, rules):
	assert(type(s) == str)
	return (rules.get(s, None))

def match_grid_rule(g, rules, depth = 0):
	assert(type(g   ) == list)
	assert(type(g[0]) == list)

	s = grid_to_string(g)
	r = get_grid_rule(s, rules)

	## all possible rules should have been pregenerated
	assert(r != None)
	return r


def split_grid(g):
	## split grid into i*j subgrids of size 2x2 or 3x3
	assert(type(g   ) == list)
	assert(type(g[0]) == list)

	sub_grids = []

	sg_size = 3 - ((len(g) & 1) == 0)
	num_sgs = len(g) / sg_size

	assert((num_sgs * sg_size) == len(g))

	if (num_sgs == 1):
		sub_grids.append([ r[:] for r in g ])
	else:
		for i in xrange(num_sgs):
			for j in xrange(num_sgs):
				a = i * sg_size
				b = j * sg_size
				sg = [ [0] * sg_size for k in xrange(sg_size) ]

				## fill sub-grid
				for p in xrange(a, a + sg_size):
					for q in xrange(b, b + sg_size):
						sg[p - a][q - b] = g[p][q]

				sub_grids.append(sg)

	## NB: if a subgrid occurs multiple times, only need to evolve it *once*
	return (sub_grids, num_sgs, sg_size)

def merge_grids(eg, num_sgs, sg_size):
	mg = [ [0] * num_sgs * sg_size for i in xrange(num_sgs * sg_size) ]

	for i in xrange(num_sgs):
		for j in xrange(num_sgs):
			## split() appends grids in row-major order
			g = eg[i * num_sgs + j]

			a = i * sg_size
			b = j * sg_size

			for p in xrange(sg_size):
				for q in xrange(sg_size):
					mg[a + p][b + q] = g[p][q]

	return mg



def run(num_iters, grid_str, rule_strs):
	pxl_counts = [0] * num_iters

	cur_grid = string_to_grid(grid_str)
	prv_grid = None

	## rules_dict = make_rules_dict(rule_strs)
	rules_dict = make_rules_dict(parse_input("day21.in"))

	for n in xrange(num_iters):
		sub_grids = split_grid(cur_grid)
		exp_grids = []

		for sub_grid in sub_grids[0]:
			grid_rule = match_grid_rule(sub_grid, rules_dict)
			rule_grid = string_to_grid(grid_rule)

			exp_grids.append(rule_grid)

		prv_grid = cur_grid
		cur_grid = merge_grids(exp_grids, sub_grids[1], sub_grids[2] + 1)

		pxl_counts[n] = count_pixels(cur_grid)
		print("[iter=%d][pixels=%d]" % (n, pxl_counts[n]))

	return (pxl_counts[4], pxl_counts[17])

assert(run(18, GRID_STR, RULE_STRS) == (203, 3342470))

