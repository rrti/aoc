from collections import defaultdict as ddict
from re import search as re_search
from time import time


class tree_node:
	def __init__(self, parent = None):
		self.parent = parent
		self.cnodes = []
		self.string = ""

	def print_rec(self, path = "", depth = 0):
		if (depth == 0):
			path = self.string
		print("%s<node=\"%s\" path=\"%s\" #children=%d>" % ("\t" * depth, self.string, path, len(self.cnodes)))
		for child in self.cnodes:
			child.print_rec(path + child.string, depth + 1)

	def get_all_leafs(self, leafs):
		if (len(self.cnodes) == 0):
			leafs.append(self)
			return

		for c in self.cnodes:
			c.get_all_leafs(leafs)


def parse_input(fn):
	with open(fn, 'r') as f:
		return (f.readline())[0: -1]

	return []

def handle_input(regex):
	def parse_regex_exp(regex_string):
		def parse_regex_rec(regex, node, index, depth):
			if (index >= len(regex)):
				return index

			next_index = index
			regex_char = regex[index]
			leaf_nodes = []

			node.get_all_leafs(leaf_nodes)

			if (regex_char == '('):
				## for every leaf, add a child and continue parsing from it
				for leaf_node in leaf_nodes:
					leaf_node.cnodes.append(tree_node(leaf_node))
					next_index = max(next_index, parse_regex_rec(regex, leaf_node.cnodes[-1], index + 1, depth + 1))

				return (parse_regex_rec(regex, node, next_index, depth))

			if (regex_char == '|'):
				## for every leaf, add a child to its parent and continue parsing from it
				for leaf_node in leaf_nodes:
					leaf_node.parent.cnodes.append(tree_node(leaf_node.parent))
					next_index = max(next_index, parse_regex_rec(regex, leaf_node.parent.cnodes[-1], index + 1, depth + 1))

				return (parse_regex_rec(regex, node, next_index, depth))

			if (regex_char == ')'):
				return (parse_regex_rec(regex, node.parent, index + 1, depth))

			## regular character, append to all leafs
			for leaf_node in leaf_nodes:
				leaf_node.string += regex_char

			return (parse_regex_rec(regex, node, index + 1, depth + 1))

		root_node = tree_node(None)
		## manually expand every possible path through the string
		parse_regex_rec(regex_string[1: -1], root_node, 0, 0)
		## debug
		## root_node.print_rec()
		return root_node


	def parse_regex(r):
		ps = [] ## path stack
		wm = {} ## world map
		dm = ddict(lambda: 1000000000) ## distance map

		cx = 0
		cy = 0
		cd = 0 ## distance traveled from origin

		xmin =  1000000000
		xmax = -1000000000
		ymin =  1000000000
		ymax = -1000000000

		wm[(cx + 0, cy + 0)] = '.'
		wm[(cx + 1, cy + 1)] = '#'
		wm[(cx + 1, cy - 1)] = '#'
		wm[(cx - 1, cy + 1)] = '#'
		wm[(cx - 1, cy - 1)] = '#'
		dm[(cx + 0, cy + 0)] = cd

		## skip ^ and $
		for i in xrange(1, len(r) - 1):
			if (r[i] == '('):
				ps.append((i, cx, cy, cd))
				continue
			if (r[i] == '|'):
				cx = ps[-1][1]
				cy = ps[-1][2]
				cd = ps[-1][3]
				continue
			if (r[i] == ')'):
				cx = ps[-1][1]
				cy = ps[-1][2]
				cd = ps[-1][3]
				ps.pop()
				continue

			px = cx
			py = cy

			## step along direction
			cx += ((r[i] == 'E') * 2)
			cx -= ((r[i] == 'W') * 2)
			cy += ((r[i] == 'S') * 2)
			cy -= ((r[i] == 'N') * 2)
			cd += 1

			xmin = min(xmin, cx)
			ymin = min(ymin, cy)
			xmax = max(xmax, cx)
			ymax = max(ymax, cy)

			## mark horizontal and vertical doors
			wm[(px + ((cx - px) >> 1), py + ((cy - py) >> 1))] = (((cx - px) != 0) and '|') or '-'
			## mark current tile
			wm[(cx + 0, cy + 0)] = '.' ##, d)
			## mark known walls
			wm[(cx + 1, cy + 1)] = '#'
			wm[(cx + 1, cy - 1)] = '#'
			wm[(cx - 1, cy + 1)] = '#'
			wm[(cx - 1, cy - 1)] = '#'
			## update distance; take the minimum in case this
			## tile is being revisited through a shorter path
			dm[(cx + 0, cy + 0)] = min(cd, dm[(cx, cy)])

		if (False):
			## initialize grid; add two tiles in each dimension for borders
			wg = [ ['#' for x in xrange(xmax - xmin + 1 + 2)] for y in xrange(ymax - ymin + 1 + 2)]

			## copy explored tiles
			for xy in wm:
				rx = xy[0] - xmin
				ry = xy[1] - ymin
				wg[ry + 1][rx + 1] = wm[xy]

			## mark starting location
			wg[(0 - ymin) + 1][(0 - xmin) + 1] = 'X'

			for row in wg:
				print("%s" % ("".join(row)))

		## maximum distance from origin, number of tiles at least 1000 distance from origin
		return (max(dm.values()), sum([1 * (d >= 1000) for d in dm.values()]))

	assert(regex[ 0] == '^')
	assert(regex[-1] == '$')
	print("[dbg] cnt(\")(\")=%d" % regex.count(")("))
	## adjacent groups are not handled correctly in general
	## would have to accumulate every location reached from
	## a group or take all possible paths through the regex
	## the actual input data causes maximum recursion depth
	## to be exceeded when using this approach however
	## assert(regex.find(")(") == -1)
	##
	## parse_regex_exp(parse_input(__file__[: -2] + "in.test1"))
	## parse_regex_exp(parse_input(__file__[: -2] + "in.test5"))
	## parse_regex_exp(parse_input(__file__[: -2] + "in.test6"))
	## parse_regex_exp(parse_input(__file__[: -2] + "in.test7"))
	## parse_regex_exp(parse_input(__file__[: -2] + "in"      )) ## fails
	return (parse_regex(regex))

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

## max is 2 here due to adjacent groups, not 1
## run(parse_input(__file__[: -2] + "in.test5"), (   2,    0))
run(parse_input(__file__[: -2] + "in.test0"), (   3,    0))
run(parse_input(__file__[: -2] + "in.test1"), (  10,    0))
run(parse_input(__file__[: -2] + "in.test2"), (  18,    0))
run(parse_input(__file__[: -2] + "in.test3"), (  23,    0))
run(parse_input(__file__[: -2] + "in.test4"), (  31,    0))
run(parse_input(__file__[: -2] + "in"      ), (3879, 8464))

