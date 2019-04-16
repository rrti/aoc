from time import time
from collections import defaultdict

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		guids = [line[: -1] for line in lines]
		return guids

	return []

def calc_checksum(guid, ddict):
	count2 = 0
	count3 = 0

	mult2 = 1
	mult3 = 1

	ddict.clear()

	for c in guid:
		ddict[c] += 1

	for (key, val) in ddict.items():
		count2 += ((val == 2) * mult2)
		count3 += ((val == 3) * mult3)
		## nullify multipliers after first occurrence of count-{2,3} keys
		mult2 *= (val != 2)
		mult3 *= (val != 3)

	return (count2, count3)

def handle_input(guids):
	ddict = defaultdict(lambda: 0)
	counts = [0, 0]

	guids.sort()

	for guid in guids:
		(count2, count3) = calc_checksum(guid, ddict)

		counts[0] += count2
		counts[1] += count3

	for i in xrange(len(guids) - 1):
		id0 = guids[i + 0]
		id1 = guids[i + 1]
		num = 0
		idx = 0

		## look for index of first differing character; input *should*
		## contain exactly one pair of strings that differ by a single
		## char
		assert(len(id0) == len(id1))
		for j in xrange(len(id0)):
			num +=      (id0[j] != id1[j])
			idx += (j * (id0[j] != id1[j]) * (num == 1))

		if (num != 1):
			continue

		print("\tid0=%s" % (id0[0: idx] + '[' + id0[idx] + ']' + id0[idx + 1: ]))
		print("\tid1=%s" % (id1[0: idx] + '[' + id1[idx] + ']' + id1[idx + 1: ]))
		break

	return (counts[0] * counts[1])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def unit_test():
	ddict = defaultdict()
	guids = ["abcdef", "bababc", "abbcde", "abcccd", "aabcdd", "abcdee", "ababab"]
	counts = [(0, 0), (1, 1), (1, 0), (0, 1), (1, 0), (1, 0), (0, 1)]

	for i in xrange(len(guids)):
		assert(calc_checksum(guids[i], ddict) == counts[i])

	assert(sum([c[0] for c in counts]) == 4)
	assert(sum([c[1] for c in counts]) == 3)
	return (4 * 3)



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), (247 * 16))

