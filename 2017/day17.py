class list_node:
	def __init__(self, prev, next, item = None):
		self.prev = prev
		self.next = next
		self.item = item

class linked_list:
	def __init__(self, node = None):
		self.head = node
		self.tail = node
		self.size = (node != None)

	def find_node(self, val):
		n = self.head

		for i in xrange(self.size):
			if (n.item == val):
				return n
			n = n.next

		return None

	def print_nodes(self, hdr = ""):
		print("[%s][size=%d]" % (hdr, self.size))

		n = self.head

		## list might be circular, do not use "while (n != None)" here
		for i in xrange(self.size):
			print '\t', n.item
			n = n.next




def add_ring_buffer_value(ring, node,  cnt, val):
	ring.size += 1

	## start from the previous returned node; O(cnt) versus O(len^2)
	for i in xrange(cnt):
		node = node.next

	if (node == ring.tail):
		## expand the ring
		new_node = list_node(ring.tail, ring.head, val)

		ring.head.prev = new_node
		ring.tail.next = new_node

		ring.tail = new_node
	else:
		new_node = list_node(node, node.next, val)

		node.next.prev = new_node
		node.next      = new_node

	return new_node


def test_ring(ring, step = 3):
	## [step=3]
	##   0
	##   0  1
	##   0  2  1
	##   0  2  3  1
	##   0  2 (4) 3  1
	##   0 (5) 2  4  3  1
	##   0  5  2  4  3 (6) 1
	##   0  5 (7) 2  4  3  6  1
	##   0  5  7  2  4  3 (8) 6  1
	##   0 (9) 5  7  2  4  3  8  6  1
	##
	node = ring.tail

	for i in xrange(9):
		node = add_ring_buffer_value(ring, node,  step, i + 1)
		ring.print_nodes()


def run_part1(size, step):
	ring = linked_list(list_node(None, None, 0))
	node = ring.tail

	ring.head.prev = ring.tail
	ring.tail.next = ring.head

	for i in xrange(size):
		node = add_ring_buffer_value(ring, node, step, i + 1)

	node = ring.find_node(size)

	assert(node      != None)
	assert(node.next != None)
	return (node.next.item)


## way too slow to be useful
def run_part2(size, step):
	ring = linked_list(list_node(None, None, 0))
	node = ring.tail

	ring.head.prev = ring.tail
	ring.tail.next = ring.head

	for i in xrange(size):
		node = add_ring_buffer_value(ring, node, step, i + 1)

	node = ring.find_node(0)

	assert(node      != None)
	assert(node.next != None)
	return (node.next.item)

def run_part2_alt(size, step):
	## no need for a buffer here, we just care about the
	## value that gets written to the position/cell/node
	## at index 1 (i.e. head.next)
	## note that still takes ~11 seconds
	idx = 0
	ret = 0

	## i+1 is the "current" buffer length
	for i in xrange(size):
		idx += step
		idx %= (i + 1)
		idx += 1

		mul = (idx == 1)
		ret = ((i + 1) * mul) + (ret * (1 - mul))

	return ret


assert(run_part1    (            2017, 376) ==      777)
assert(run_part2_alt(50 * 1000 * 1000, 376) == 39289581)

