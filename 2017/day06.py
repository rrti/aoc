## convert configuration to a base-10 bigint
def calc_bank_id(banks):
	v = 0
	n = len(banks)
	p = 1
	for i in xrange(n):
		d = banks[n - 1 - i]
		v += (d * p)
		p *= 10
	return v


def run_realloc_cycle(banks, table, cycle):
	max_bank_idx = 0
	max_block_cnt = banks[max_bank_idx]
	num_banks = len(banks)

	## find fullest bank
	for i in xrange(1, num_banks):
		num_blocks = banks[i]

		if (num_blocks > max_block_cnt):
			max_block_cnt = num_blocks
			max_bank_idx = i

	## redistribute blocks
	num_blocks = banks[max_bank_idx]
	cur_bank_idx = max_bank_idx + 1
	banks[max_bank_idx] = 0

	while (num_blocks > 0):
		banks[cur_bank_idx % num_banks] += 1
		cur_bank_idx += 1
		num_blocks -= 1

	cur_bank_id = calc_bank_id(banks)

	## configuration seen before, return cycle-length (part 2)
	if (cur_bank_id in table):
		return (cycle - table[cur_bank_id])

	## store bank configuration for current cycle (part 1)
	table[cur_bank_id] = cycle
	return -1


def run(banks):
	cycle_len = -1
	cycle_cnt =  0

	table = {}

	while (cycle_len < 0):
		cycle_cnt += 1
		cycle_len = run_realloc_cycle(banks, table, cycle_cnt)

	return (cycle_cnt, cycle_len)

assert(run([0, 2, 7, 0]) == (5, 4))
assert(run([2, 8, 8, 5, 4, 2, 3, 1, 5, 5, 1, 2, 15, 13, 5, 14]) == (3156, 1610))

