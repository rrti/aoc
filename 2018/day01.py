from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		freqs = [int(line[: -1]) for line in lines]
		return freqs

	return []

def handle_input(freqs):
	sum_freq = 0
	cur_iter = 0

	freq_set = set([sum_freq])

	while (cur_iter >= 0):
		for f in freqs:
			sum_freq += f

			if (sum_freq in freq_set):
				return (sum(freqs), sum_freq)

			freq_set.add(sum_freq)

	## unreachable
	assert(False)
	return (-1, -1)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in"), (500, 709))

