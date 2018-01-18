TEST_SHEET = (
	[[5, 1, 9, 5], [   7, 5, 3], [2, 4, 6, 8]],
	[[5, 9, 2, 8], [9, 4, 7, 3], [3, 8, 6, 5]],
)

REAL_SHEET = [
	[3458, 3471,  163, 1299,  170, 4200, 2425,  167, 3636, 4001, 4162,  115, 2859,  130, 4075, 4269],
	[2777, 2712,  120, 2569, 2530, 3035, 1818,   32,  491,  872,  113,   92, 2526,  477,  138, 1360],
	[2316,   35,  168,  174, 1404, 1437, 2631, 1863, 1127,  640, 1745,  171, 2391, 2587,  214,  193],
	[ 197, 2013,  551, 1661,  121,  206,  203,  174, 2289,  843,  732, 2117,  360, 1193,  999, 2088],
	[3925, 3389,  218, 1134,  220,  171, 1972,  348, 3919, 3706,  494, 3577, 3320,  239,  120, 2508],
	[ 239,  947, 1029, 2024,  733,  242,  217, 1781, 2904, 2156, 1500, 3100,  497, 2498, 3312,  211],
	[ 188, 3806, 3901,  261,  235, 3733, 3747, 3721,  267, 3794, 3814, 3995, 3004,  915, 4062, 3400],
	[ 918,   63, 2854, 2799,  178,  176, 1037,  487,  206,  157, 2212, 2539, 2816, 2501,  927, 3147],
	[ 186,  194,  307,  672,  208,  351,  243,  180,  619,  749,  590,  745,  671,  707,  334,  224],
	[1854, 3180, 1345, 3421,  478,  214,  198,  194, 4942, 5564, 2469,  242, 5248, 5786, 5260, 4127],
	[3780, 2880,  236,  330, 3227, 1252, 3540,  218,  213,  458,  201,  408, 3240,  249, 1968, 2066],
	[1188,  696,  241,   57,  151,  609,  199,  765, 1078,  976, 1194,  177,  238,  658,  860, 1228],
	[ 903,  612,  188,  766,  196,  900,   62,  869,  892,  123,  226,   57,  940,  168,  165,  103],
	[ 710, 3784,   83, 2087, 2582, 3941,   97, 1412, 2859,  117, 3880,  411,  102, 3691, 4366, 4104],
	[3178,  219,  253, 1297, 3661, 1552, 8248,  678,  245, 7042,  260,  581, 7350,  431, 8281, 8117],
	[ 837,   80,   95,  281,  652,  822, 1028, 1295,  101, 1140,   88,  452,   85,  444,  649, 1247]
]

PRIME_NUMS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61)


for r in TEST_SHEET[0]: r.sort(reverse = True)
for r in TEST_SHEET[1]: r.sort(reverse = True)
for r in REAL_SHEET   : r.sort(reverse = True)



def lt_comp(a, b): return (max(-1, min(1, a - b)))
def gt_comp(a, b): return (max(-1, min(1, b - a)))

def bfind(a, v, comp):
	min_idx = 0
	max_idx = len(a)

	assert(comp == lt_comp or comp == gt_comp)

	while ((max_idx - min_idx) > 1):
		cur_idx = (min_idx + max_idx) >> 1
		cur_val = a[cur_idx]
		val_cmp = comp(v, cur_val)

		if (val_cmp == -1):
			max_idx = cur_idx
			continue
		if (val_cmp == +1):
			min_idx = cur_idx
			continue

		break

	cur_idx = (min_idx + max_idx) >> 1

	if (comp(v, a[cur_idx]) == 0):
		return cur_idx

	## allow recovering the "would-be" index
	return (-cur_idx - 1)

def test_bfind(row):
	## rows are sorted in descending order, so either reverse or use gt_comp
	row.reverse()
	row.append(7000)

	assert(bfind(row,  114, lt_comp) < 0)
	assert(bfind(row, 4300, lt_comp) < 0)

	cnt = 0

	for val in row:
		idx = bfind(row, val, lt_comp)
		cnt += (row[idx] == val)

	return (cnt == len(row))



def calc_max_diff_alt(sheet_row):
	## double the work, half the code
	## return (max(sheet_row) - min(sheet_row))

	min_val = +10000000000000
	max_val = -10000000000000

	for i in xrange(len(sheet_row)):
		min_val = min(min_val, sheet_row[i])
		max_val = max(max_val, sheet_row[i])

	return (max_val - min_val)

## assumes row has already been sorted
def calc_max_diff(sheet_row):
	return (sheet_row[0] - sheet_row[-1])



def calc_even_div(sheet_row, prime_nums):
	row_len = len(sheet_row)

	if (False):
		for i in xrange(row_len):
			a = sheet_row[i]
			z = 2 + (a & 1)

			for j in xrange(a & 1, len(prime_nums)):
				z = prime_nums[j]

				if ((a % z) == 0):
					break

			min_fac = min(z, a / z)
			max_fac = max(z, a / z)

			## slower, linear search wins for small arrays
			max_fac_idx = abs(bfind(sheet_row, max_fac, gt_comp))
			min_fac_idx = abs(bfind(sheet_row, min_fac, gt_comp))

			assert(max_fac_idx <= min_fac_idx)

			for j in xrange(max_fac_idx, min(row_len, min_fac_idx + 1)):
				b = sheet_row[j]
				c = a / b

				if (b > max_fac):
					break
				if (a == (b * c)):
					return c
	else:
		for i in xrange(row_len):
			a = sheet_row[i]
			z = 2 + (a & 1)

			## for any number a, its factors are located in the range [min_fac, a / min_fac]
			min_fac = min(z, a / z)
			max_fac = max(z, a / z)

			for j in xrange(row_len):
				b = sheet_row[row_len - 1 - j]
				c = a / b

				if (b > max_fac):
					break
				if (a == (b * c)):
					return c

	return 0


def calc_max_diff_checksum(sheet_vals):
	return (sum(calc_max_diff(sheet_row) for sheet_row in sheet_vals))

def calc_even_div_checksum(sheet_vals, prime_nums):
	return (sum(calc_even_div(sheet_row, prime_nums) for sheet_row in sheet_vals))


assert(test_bfind(REAL_SHEET[0][:]))

assert(calc_even_div(TEST_SHEET[1][0], PRIME_NUMS) == 4)
assert(calc_even_div(TEST_SHEET[1][1], PRIME_NUMS) == 3)
assert(calc_even_div(TEST_SHEET[1][2], PRIME_NUMS) == 2)

assert(calc_max_diff_checksum(TEST_SHEET[0]         ) ==    18)
assert(calc_max_diff_checksum(REAL_SHEET            ) == 51139) ## part 1
assert(calc_even_div_checksum(REAL_SHEET, PRIME_NUMS) ==   272) ## part 2

