def is_anagram_alt(w1, w2):
	if (len(w1) != len(w2)):
		return False

	## each character must occur the same number of times
	## in both words for w1 to be an anagram of w2 (or vv)
	## can just sort both words alphabetically and compare
	t = {}

	for c in w1:
		if (c in t):
			continue

		counts = (w1.count(c), w2.count(c))

		if (counts[0] != counts[1]):
			return False

		t[c] = counts

	return True

def is_anagram(w1, w2):
	if (len(w1) != len(w2)):
		return False

	## l1 = list(w1); l1.sort()
	## l2 = list(w2); l2.sort()
	return (sorted(w1) == sorted(w2))


def check_anagrams_noop(table, word, index): return False
def check_anagrams_impl(table, word, index):
	for w in table:
		## do not check word against itself
		if (table[w][1] == index):
			continue

		if (is_anagram(w, word)):
			return True

	return False


def valid_passphrase(pp, check_anagrams):
	t = {}
	i = 0 ## word index

	for w in pp:
		## if not yet in table, map word to its count and index
		if (w in t):
			return False

		t[w] = (1, i)

		if (check_anagrams(t, w, i)):
			return False

		i += 1

	return True


def parse_input(fn):
	with open(fn, 'r') as f:
		lines = f.readlines()
		sents = [None] * len(lines)
		index = 0

		for line in lines:
			## strip newline from last word
			sent = line.split(" ")
			word = sent[-1]

			sent[-1] = word[0: len(sent[-1]) - 1]
			sents[index] = sent

			index += 1

		return sents


def run_checks():
	## part 1 (only duplicates disallowed)
	assert(    valid_passphrase("aa bb cc dd ee".split(" "), check_anagrams_noop))
	assert(not valid_passphrase("aa bb cc dd aa".split(" "), check_anagrams_noop))
	assert(    valid_passphrase("aa bb cc dd aaa".split(" "), check_anagrams_noop))

	## part 2 (anagrams also disallowed)
	assert(    valid_passphrase("abcde fghij".split(" "), check_anagrams_impl))
	assert(not valid_passphrase("abcde xyz ecdab".split(" "), check_anagrams_impl))
	assert(    valid_passphrase("a ab abc abd abf abj".split(" "), check_anagrams_impl))
	assert(    valid_passphrase("iiii oiii ooii oooi oooo".split(" "), check_anagrams_impl))
	assert(not valid_passphrase("oiii ioii iioi iiio".split(" "), check_anagrams_impl))
	return True

def run_filter():
	pass_phrases = parse_input("day04.in")
	valid_counts = [0, 0]

	for pp in pass_phrases:
		valid_counts[0] += valid_passphrase(pp, check_anagrams_noop)
		valid_counts[1] += valid_passphrase(pp, check_anagrams_impl)

	return valid_counts

assert(run_checks())
assert(run_filter() == [337, 231])

