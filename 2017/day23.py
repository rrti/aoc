from day18 import *


def run_solo_novm(b, c, k):
	n = ((c - b) / k) + 1
	p = 0

	## counts the non-prime numbers in [min_value=b, max_value=c, step_size=k]
	##   g := current value being tested for primality
	##   e := g % d (emulated by inner-most loop of assembly code, no mod instr)
	##   f := 1 if g is prime, 0 otherwise
	##   n := number of values in interval [b,c]
	##   p := number of primes in interval [b,c]
	g = b

	while (g <= c):
		f = 1
		d = 2

		while ((d * d) <= g):
			e = g % d

			if (e == 0):
				f = 0
				break

			d += 1

		p += (f == 1)
		g += k

	return (n - p)


assert(run_progs(parse_input("day23.in"), (1, 0, 1, 0, '*')) == 5929)
## assert(run_progs(parse_input("day23.in"), (1, 0, 1, 1, 'h')) == 907)

assert(run_solo_novm( 2               , 18                       ,  1) ==  10)
assert(run_solo_novm( 2               , 19                       ,  1) ==  10)
assert(run_solo_novm(79 * 100 + 100000, 79 * 100 + 100000 + 17000, 17) == 907)
assert(run_solo_novm(81 * 100 + 100000, 81 * 100 + 100000 + 17000, 17) == 909)

