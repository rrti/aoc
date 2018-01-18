class node_data:
	def __init__(self, pn, cn, lw):
		assert(type(pn) == str)
		assert(type(cn) == list)
		assert(len(cn) == 0 or type(cn[0]) == str)
		assert(type(lw) == int)

		self.pn = pn ## parent name
		self.cn = cn ## child names
		self.lw = lw ## local weight

	def __repr__(self):
		return ("%s (%d) -> %s" % (self.p, self.w, self.c))

class node_inst:
	def __init__(self, nn, ci, lw):
		assert(type(nn) == str)
		assert(type(ci) == list)
		assert(type(lw) == int)

		self.nn = nn ## node name
		self.ci = ci ## child instances
		self.lw = lw ## local weight
		self.tw =  0 ## total weight



def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		nodes = []

		for line in lines:
			parent = line[0: line.index(' ')]
			weight = line[line.index('(') + 1: line.index(')')]
			childs = []

			## <nc> commas imply <nc + 1> children, last is not followed by ','
			## e.g. "yffcj (90) -> bbmmtud, bqbgocl, kgntkz, mmfwbku, asefoiu"
			if (line.count('>') == 1):
				nc = line.count(',')
				bi = line.index('>')
				ci = 0

				assert(nc > 0)
				while (nc > 0):
					ci = line.index(',', bi + 1)
					cn = line[bi + 2: ci]

					bi = ci
					nc -= 1

					childs.append(cn)

				childs.append(line[bi + 2: -1])

			nodes.append(node_data(parent, childs, int(weight)))

		return nodes



def find_tree_root(node_data_array):
	node_data_table = {}

	## map children (names) to parents (data)
	for pnd in node_data_array:
		for cn in pnd.cn:
			node_data_table[cn] = pnd

	## arbitrarily pick the first data instance
	nd = node_data_array[0]
	nn = nd.pn

	## walk up the child->parent chain, end is root
	while (nn in node_data_table):
		nd = node_data_table[nn]
		nn = nd.pn

	return nd

def find_tree_root_alt(node_data_array):
	node_data_table = {}

	for pnd in node_data_array:
		for cn in pnd.cn:
			assert(type(cn) == str)
			assert(not (cn in node_data_table))
			node_data_table[cn] = pnd.pn

	## find the single unreferenced root node
	for nd in node_data_array:
		if (nd.pn in node_data_table):
			continue

		return nd

	assert(False)
	return None



def make_tree(nd, table, depth = 0):
	ni = node_inst(nd.pn, [None] * len(nd.cn), nd.lw)

	for k in xrange(len(nd.cn)):
		cnn = nd.cn[k] ## child-name (string)
		cnd = table[cnn] ## child-data (object)

		ni.ci[k] = make_tree(cnd, table, depth + 1)

	return ni


## pre-order traversal since trees are not binary
def print_tree(n, depth = 0):
	print("%s%s(%d::%d)" % ('\t' * depth, n.n, n.w, n.t))

	for c in n.c:
		print_tree(c, depth + 1)


def calc_tree_weights(n, depth = 0):
	w = [0] * len(n.ci)

	for k in xrange(len(n.ci)):
		w[k] = calc_tree_weights(n.ci[k], depth + 1)

	## total weight (node itself plus subtree)
	n.tw = n.lw + sum(w)
	return n.tw


def check_tree_imbalance(ni, depth = 0):
	for ci in ni.ci:
		ret = check_tree_imbalance(ci, depth + 1)

		if (ret != None):
			return ret

	## analyze on the way back up s.t. we get the deepest imbalance first
	## challenge guarantees only one imbalance exists in the entire tree;
	## i.e. it contains some deepest parent node <ni> with N > 1 children
	## whose *total* (local plus subtree) weights are different
	for k in xrange(len(ni.ci) - 1):
		ci = ni.ci[k    ]
		cj = ni.ci[k + 1]

		## select the correct child to be locally adjusted independent of order
		abs_dt = abs(ci.tw - cj.tw)
		max_cw = ((ci.tw > cj.tw) and ci.lw) or cj.lw

		if (abs_dt != 0):
			return (max_cw, abs_dt)

	return None



TEST_NODE_DATA_ARR = parse_input("day07_test.in")
REAL_NODE_DATA_ARR = parse_input("day07.in")
TEST_NODE_DATA_TBL = {nd.pn: nd for nd in TEST_NODE_DATA_ARR}
REAL_NODE_DATA_TBL = {nd.pn: nd for nd in REAL_NODE_DATA_ARR}

if (False):
	assert(REAL_NODE_DATA_TBL[ "ggpau"].w ==   91)
	assert(REAL_NODE_DATA_TBL["sphbbz"].w == 1161)
	## manually fix the imbalance to test detection logic
	REAL_NODE_DATA_TBL["sphbbz"].w -= 9

TEST_ROOT_NODE = make_tree(find_tree_root(TEST_NODE_DATA_ARR), TEST_NODE_DATA_TBL)
REAL_ROOT_NODE = make_tree(find_tree_root(REAL_NODE_DATA_ARR), REAL_NODE_DATA_TBL)

calc_tree_weights(REAL_ROOT_NODE)
calc_tree_weights(TEST_ROOT_NODE)
assert(check_tree_imbalance(REAL_ROOT_NODE) == (1161, 9))
assert(check_tree_imbalance(TEST_ROOT_NODE) == (  68, 8))

