from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		line = f.readlines()[0]
		poly = line[: -1]
		return poly

	return []

def handle_input_part1_ll(polymer):
	class ll_node:
		def __init__(self, indx, char, next):
			self.indx = indx
			self.char = char
			self.next = next

	def gen_polymer(node):
		poly = ""

		while (node != None):
			poly += node.char
			node = node.next

		return poly

	llnodes = [ll_node(i, polymer[i], None) for i in xrange(len(polymer))]

	## build linked-list of character nodes
	for i in xrange(len(llnodes) - 1):
		llnodes[i].next = llnodes[i + 1]

	min_indx = 0
	## number of annihilating pairs found
	num_anns = 1

	while (num_anns > 0):
		num_anns = 0

		prv_node = None
		cur_node = llnodes[min_indx]

		while (cur_node != None):
			nxt_node = cur_node.next

			if (nxt_node == None):
				break

			## if ((abs(ord(cur_node.char) - ord(nxt_node.char))) == 32):
			if ((ord(cur_node.char) ^ ord(nxt_node.char)) == 32):
				num_anns += 1

				if (prv_node != None):
					prv_node.next = nxt_node.next
				else:
					## keep skipping pairs until we get to one that
					## does not annihilate and lets us set prv_node
					min_indx += 2

				## jump ahead to nxt_node.next, *much* too slow to
				## remove only one annihilating pair per iteration
				cur_node = nxt_node.next
				continue

			prv_node = cur_node
			cur_node = nxt_node

	return (gen_polymer(llnodes[min_indx]))

def handle_input_part1(polymer):
	stack = []

	for c in polymer:
		stack.append(c)

		while (len(stack) >= 2 and (ord(stack[-2]) ^ ord(stack[-1])) == 32):
			stack.pop()
			stack.pop()

	return ("".join(stack))

def handle_input_part2(polymer):
	min_length = len(polymer)

	for i in xrange(26):
		lc_char = chr(ord('a') + i     )
		uc_char = chr(ord('a') + i - 32)

		ret_polymer = handle_input_part1(polymer.replace(lc_char, '').replace(uc_char, ''))
		min_length = min(min_length, len(ret_polymer))

	return min_length

def handle_input_timed(fun, inp):
	return (time(), fun(inp), time())



def run(inp, out):
	## output polymer is too long to insert verbatim; just compare lengths
	## assert(len(handle_input_part1(inp)) == out[1])
	## assert(   (handle_input_part2(inp)) == out[2])
	##
	## use output of part 1 as input for part 2 to speed up reactions
	## note that the stack-based version is orders of magnitude faster
	ret_part1 = handle_input_timed(handle_input_part1, inp)
	ret_part2 = handle_input_timed(handle_input_part2, ret_part1[1])

	assert(len(ret_part1[1]) == out[1])
	assert(   (ret_part2[1]) == out[2])
	print("[%s] dt=%fs" % (__file__, ret_part2[2] - ret_part1[0]))

run(parse_input(__file__[: -2] + "in.test"), ("dabCBAcaDA",    10,    4))
run(parse_input(__file__[: -2] + "in"     ), (          "", 11720, 4956))

