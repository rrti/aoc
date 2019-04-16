from time import time

def digits(n):
	r = [n % 10]
	while ((n / 10) > 0):
		n /= 10
		r.append(n % 10)
	r.reverse()
	return r

def handle_input(n):
	ndigits = digits(n)

	indices = [0, 1] ## two Elves
	recipes = [3, 7]
	outputs = [[], -1]

	elf_scores = [0, 0]
	sum_digits = [0, 0]

	num_digits = len(ndigits)
	num_recipes = 2

	for i in xrange(1000000000):
		elf_scores[0] = recipes[ indices[0] ]
		elf_scores[1] = recipes[ indices[1] ]

		recipe_sum = sum(elf_scores)

		## sum will always be <= 18, save allocations
		## sum_digits = digits(recipe_sum)

		sum_digits[0] = (recipe_sum / 10) % 10
		sum_digits[1] = (recipe_sum     ) % 10


		if (sum_digits[0] == 0):
			recipes.append(sum_digits[1])
		else:
			recipes.append(sum_digits[0])
			recipes.append(sum_digits[1])

		num_recipes = len(recipes)

		indices[0] += (1 + elf_scores[0])
		indices[1] += (1 + elf_scores[1])
		indices[0] %= num_recipes
		indices[1] %= num_recipes

		if (num_recipes < num_digits):
			continue

		## average run-time ~21 seconds, slice is faster than digit-by-digit comparison
		if (recipes[i - num_digits: i] != ndigits):
			continue

		outputs[1] = i - num_digits
		break

	## save the n-th through (n+10)-th score digits
	for i in xrange(n, n + 10):
		outputs[0].append(chr(recipes[i] + ord('0')))

	return ("".join(outputs[0]), outputs[1])

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(     5, ("0124515891",         9)) ## score digits [     5:     15] are  01245* after        9 recipes
run(     9, ("5158916779",        13)) ## score digits [     9:     19] are  51589* after       13 recipes
run(    18, ("9251071085",        48)) ## score digits [    18:     28] are  92510* after       48 recipes
run(  2018, ("5941429882",     86764)) ## score digits [  2018:   2028] are  59414* after    86764 recipes
run(509671, ("2810862211",  20227889)) ## score digits [509671: 509681] are 509671* after 20227889 recipes

