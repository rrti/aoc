from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		line = f.readlines()[0]
		data = line.split(' ')
		return [int(i) for i in data]

	return []

def handle_input(header_data):
	class node:
		def __init__(self, parent_node, num_children, num_metadata):
			self.parent = parent_node
			self.children = [None] * num_children
			self.metadata = [None] * num_metadata

		def calc_metadata_sum(self, recursive = True):
			metadata_sum = sum(self.metadata)

			if (recursive):
				for child in self.children:
					metadata_sum += child.calc_metadata_sum()

			return metadata_sum

		def calc_license_value(self):
			license_value = 0

			if (len(self.children) == 0):
				return (self.calc_metadata_sum(False))

			for child_index in self.metadata:
				if (child_index > 0 and (child_index - 1) < len(self.children)):
					license_value += self.children[child_index - 1].calc_license_value()

			return license_value

	def parse_header(parent_node, header_data, data_index):
		num_children = header_data[data_index[0]    ]
		num_metadata = header_data[data_index[0] + 1]

		## do not need the parent reference or the tree structure itself, but KISS
		tree_node = node(parent_node, num_children, num_metadata)
		data_index[0] += 2

		for i in xrange(num_children):
			tree_node.children[i] = parse_header(tree_node, header_data, data_index)

		## extract metadata for this node *after* recursively parsing all children
		for i in xrange(num_metadata):
			tree_node.metadata[i] = header_data[data_index[0] + i]

		data_index[0] += num_metadata
		return tree_node

	data_indx = [0]
	root_node = parse_header(None, header_data, data_indx)

	return (root_node.calc_metadata_sum(), root_node.calc_license_value())

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  138,    66))
run(parse_input(__file__[: -2] + "in"     ), (44893, 27433))

