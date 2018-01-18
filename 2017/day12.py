def parse_input(fn):
	with open(fn, 'r') as f:
		real_edge_data = f.readlines()
		real_edge_list = [real_edge_data[i].strip() for i in xrange(len(real_edge_data))]

		return real_edge_list


def parse_edge_list(edges):
	graph = [None] * len(edges)

	for i in xrange(len(edges)):
		edge = edges[i].split(" <-> ")
		head = edge[0]
		tail = edge[1].split(", ")

		graph[int(head)] = [int(v) for v in tail]

	return graph


def traverse_edge_list_bfs(graph, nodes, start):
	queue = [start]
	## passed in so we can identify all groups later
	## nodes = {}

	head = 0

	"""
	## popping the front element from a Python list is
	## expensive (needs a deque or actual LL), so just
	## advance an index
	while (len(queue) > 0):
		node = queue[0]
		queue = queue[1: ]
	"""

	while (head < len(queue)):
		node = queue[head]
		head += 1

		if (node in nodes):
			continue

		## use the starting-node as group-marker s.t.
		## number of unique values is the group-count
		nodes[node] = start

		for ngb in graph[node]:
			queue.append(ngb)

	return nodes


def count_groups(nodes):
	groups = {}

	for node in nodes:
		group = nodes[node]
		groups[group] = 1

	return (len(groups))


TEST_EDGE_LIST = [
	"0 <-> 2",
	"1 <-> 1",
	"2 <-> 0, 3, 4",
	"3 <-> 2, 4",
	"4 <-> 2, 3, 6",
	"5 <-> 6",
	"6 <-> 4, 5",
]

TEST_GRAPH = parse_edge_list(        TEST_EDGE_LIST )
REAL_GRAPH = parse_edge_list(parse_input("day12.in"))
TEST_NODES = traverse_edge_list_bfs(TEST_GRAPH, {}, 0)
REAL_NODES = traverse_edge_list_bfs(REAL_GRAPH, {}, 0)

def run(nodes, graph):
	num_nodes = len(nodes)
	num_edges = len(graph)

	for i in xrange(1, num_edges):
		nodes = traverse_edge_list_bfs(REAL_GRAPH, nodes, i)

	return (num_nodes, count_groups(nodes))

assert(run(TEST_NODES, TEST_GRAPH) == (  6,   2))
assert(run(REAL_NODES, REAL_GRAPH) == (130, 189))

