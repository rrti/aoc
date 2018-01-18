TEST_GEN_PARAMS = (
	(( 65, 16807, (1 << 31) - 1, (1 << 16) - 1, 1),  (8921, 48271, (1 << 31) - 1, (1 << 16) - 1, 1)), ## (A, B); part 1
	(( 65, 16807, (1 << 31) - 1, (1 << 16) - 1, 4),  (8921, 48271, (1 << 31) - 1, (1 << 16) - 1, 8)), ## (A, B); part 2
)
REAL_GEN_PARAMS = (
	((703, 16807, (1 << 31) - 1, (1 << 16) - 1, 1),  ( 516, 48271, (1 << 31) - 1, (1 << 16) - 1, 1)), ## (A, B); part 1
	((703, 16807, (1 << 31) - 1, (1 << 16) - 1, 4),  ( 516, 48271, (1 << 31) - 1, (1 << 16) - 1, 8)), ## (A, B); part 2
)


class generator:
	def __init__(self, params):
		self.seed = params[0]
		self.fact = params[1]
		self.modu = params[2]
		self.mask = params[3]
		self.mult = params[4] - 1

	## LCG's essentially perform modular exponentiation, since:
	##   a_1 = (a_0 * k) % p                                                     = (a_0 * k^1) % p
	##   a_2 = (a_1 * k) % p =     (((a_0 * k) % p) * k) % p                     = (a_0 * k^2) % p
	##   a_3 = (a_2 * k) % p =   (((((a_0 * k) % p) * k) % p) * k) % p           = (a_0 * k^3) % p
	##   a_4 = (a_3 * k) % p = (((((((a_0 * k) % p) * k) % p) * k) % p) * k) % p = (a_0 * k^4) % p
	##   a_n = (a_{n-1} * k) % p
	## however we can only calculate (k ^ n) % p = pow(k, n, p)
	## efficiently so there is no way to take advantage of this
	def exp_next(self, exp): return ((self.seed * (self.fact ** exp)) % self.modu)
	def mask_next(self): return (self.next() & self.mask)
	def next(self):
		while (True):
			self.seed = (self.seed * self.fact) % self.modu

			## mult is a power of two in both challenge parts
			## if ((self.seed % self.mult) == 0):
			if ((self.seed & self.mult) == 0):
				return self.seed

		return 0


def calc_num_matches(num_iters, param_idx):
	num_test_matches = 0
	num_real_matches = 0

	test_generators = (generator(TEST_GEN_PARAMS[param_idx][0]), generator(TEST_GEN_PARAMS[param_idx][1]))
	real_generators = (generator(REAL_GEN_PARAMS[param_idx][0]), generator(REAL_GEN_PARAMS[param_idx][1]))

	for i in xrange(num_iters):
		num_test_matches += (test_generators[0].mask_next() == test_generators[1].mask_next())
		num_real_matches += (real_generators[0].mask_next() == real_generators[1].mask_next())

	return (num_test_matches, num_real_matches)


assert(calc_num_matches(40 * 1000 * 1000, 0) == (588, 594)) ## part 1
assert(calc_num_matches( 5 * 1000 * 1000, 1) == (309, 328)) ## part 2

"""
tg1 = generator(TEST_GEN_PARAMS[0][0])
tg2 = generator(TEST_GEN_PARAMS[0][0])

for i in xrange(10):
	assert(tg1.next() == tg2.exp_next(i + 1))
"""

