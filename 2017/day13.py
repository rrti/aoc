## <depth, range>; scanner periods are given by range * 2 - 1
TEST_FIREWALL_DICT = {
	0: 3,
	1: 2,
	4: 4,
	6: 4,
}

REAL_FIREWALL_DICT = {
	0: 3,
	1: 2,
	2: 9,
	4: 4,
	6: 4,
	8: 6,
	10: 6,
	12: 8,
	14: 5,
	16: 6,
	18: 8,
	20: 8,
	22: 8,
	24: 6,
	26: 12,
	28: 12,
	30: 8,
	32: 10,
	34: 12,
	36: 12,
	38: 10,
	40: 12,
	42: 12,
	44: 12,
	46: 12,
	48: 14,
	50: 14,
	52: 8,
	54: 12,
	56: 14,
	58: 14,
	60: 14,
	64: 14,
	66: 14,
	68: 14,
	70: 14,
	72: 14,
	74: 12,
	76: 18,
	78: 14,
	80: 14,
	86: 18,
	88: 18,
	94: 20,
	98: 18,
}


## Python lists are ~400ms faster to iterate than dicts
TEST_FIREWALL = TEST_FIREWALL_DICT.items()
REAL_FIREWALL = REAL_FIREWALL_DICT.items()

## sorting in ascending order of range saves ~180ms due to early-outs
TEST_FIREWALL.sort(key = lambda layer: layer[1])
REAL_FIREWALL.sort(key = lambda layer: layer[1])


def calc_packet_severity(fw):
	pkt_score = 0

	for (d, r) in fw:
		## or explicitly 2 * r - 2; note that bitshifts are slower
		m = 2 * (r - 1)
		k = ((d % m) == 0)

		pkt_score += ((d * r) * k)

	return pkt_score


def calc_min_packet_delay(fw):
	pkt_delay = 0
	hit_count = 1

	## TODO:
	##   use Chinese Remainer Theorem; firewall layer <i>
	##   is entered on cycle <i+d> given packet delay <d>
	##   the period length of a scanner with range <r> is
	##   just 2*r - 1; we want a value for d s.t. for all
	##   scanner periods p, gdc(i+d,p)=1
	##
	if (False):
		layer_idx = 0
		layer_cnt = len(fw)

		while (layer_idx < layer_cnt):
			(d, r) = fw[layer_idx]

			k = pkt_delay + d
			m = 2 * (r - 1)
			## "expr * const" is ~290ms slower than "const * expr"
			## m = (r - 1) * 2

			if ((k % m) == 0):
				layer_idx  = 0
				pkt_delay += 1
			else:
				layer_idx += 1

			## ~700ms slower than branching, modulo-operation stalls
			## z = ((k % m) != 0)
			##
			## layer_idx *= (    z)
			## pkt_delay += (1 - z)
			## layer_idx += (    z)

	else:

		while (hit_count != 0):
			hit_count = 0

			for (d, r) in fw:
				k = pkt_delay + d
				m = 2 * (r - 1)

				if ((k % m) == 0):
					hit_count = 1
					break

			## "var == const" incurs a ~200ms penalty
			pkt_delay += (1 == hit_count)

	return pkt_delay


## part 1
assert(calc_packet_severity(TEST_FIREWALL) ==   24)
assert(calc_packet_severity(REAL_FIREWALL) == 1704)
## part 2
assert(calc_min_packet_delay(TEST_FIREWALL) ==      10)
assert(calc_min_packet_delay(REAL_FIREWALL) == 3970918)

