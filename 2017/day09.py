def score_stream(s):
	group_stack = [] ## {'s
	gbage_stack = [] ## <'s

	index = 0
	score = 0
	total = 0
	nncgc = 0

	while (index < len(s)):
		c = s[index]

		assert(len(gbage_stack) <= 1)

		## add current score to total and reset if at end of a stream but not end of string
		total += (score * (len(group_stack) == 0 and len(gbage_stack) == 0))
		score *= (    1 - (len(group_stack) == 0 and len(gbage_stack) == 0))
		## count the number of (non-cancelled) garbage characters
		nncgc += ((len(gbage_stack) > 0) and c != '!' and c != '>')

		## within garbage, {}< have no meaning
		## a character directly following ! also has none
		## and is simply escaped, but only inside garbage
		## must either advance index by 2 and continue or
		## add 1 here and again below
		if (c == '!'):
			index += (len(gbage_stack) > 0)

		elif (c == '{'):
			if (len(gbage_stack) == 0):
				group_stack.append(index)

			## current nesting determines score per group
			score += (len(group_stack) * (len(gbage_stack) == 0))
		elif (c == '}'):
			if (len(gbage_stack) == 0):
				assert(len(group_stack) > 0)
				group_stack.pop()

		elif (c == '<'):
			## grow stack only if not already inside garbage
			## we could also just skip ahead to the next '>'
			## but that makes part two more difficult
			if (len(gbage_stack) == 0):
				gbage_stack.append(index)

		elif (c == '>'):
			assert(len(gbage_stack) > 0)
			gbage_stack.pop()

		## any non-semantic character
		index += 1

	assert(len(group_stack) == 0)
	assert(len(gbage_stack) == 0)
	return (total + score, nncgc)


def check_streams(streams):
	total_stream = ""
	total_score = 0

	for test_stream in streams:
		total_stream += test_stream[0]
		local_score = score_stream(test_stream[0])
		total_score += local_score[0]
		assert(local_score[0] == test_stream[1])

	assert(total_score == 50)
	assert(score_stream(         total_stream)[0] == 50)
	assert(score_stream("<>"                 )[1] ==  0)
	assert(score_stream("<random characters>")[1] == 17)
	assert(score_stream("<<<<>"              )[1] ==  3)
	assert(score_stream("<{!>}>"             )[1] ==  2)
	assert(score_stream("<!!>"               )[1] ==  0)
	assert(score_stream("<!!!>>"             )[1] ==  0)
	assert(score_stream("<{o\"i!a,<{i<a>"    )[1] == 10)
	return True


TEST_STREAMS = [
	("{}"                           , 1                    ),
	("{{{}}}"                       , 1 + 2 + 3            ),
	("{{},{}}"                      , 1 + 2 + 2            ),
	("{{{},{},{{}}}}"               , 1 + 2 + 3 + 3 + 3 + 4),
	("{<a>,<a>,<a>,<a>}"            , 1                    ),
	("{{<ab>},{<ab>},{<ab>},{<ab>}}", 1 + 2 + 2 + 2 + 2    ),
	("{{<!!>},{<!!>},{<!!>},{<!!>}}", 1 + 2 + 2 + 2 + 2    ),
	("{{<a!>},{<a!>},{<a!>},{<ab>}}", 1 + 2                ),

	("<{!>}>"         , 0),
	("<<<<>"          , 0),
	("<!!>"           , 0),
	("<!!!>>"         , 0),
	("<{o\"i!a,<{i<a>", 0),
]

TEST_SCORES = (
	(sum(v[0]) for v in TEST_STREAMS),
	(sum(v[1]) for v in TEST_STREAMS),
)


assert(check_streams(TEST_STREAMS))

with open("day09.in", 'r') as f:
	assert(score_stream(f.read()) == (8337, 4330))

