def parse_input(fn):
	with open(fn, 'r') as f:
		path_rows = f.readlines()
		real_path = [""] * (len(path_rows) + 2)

		## add two blank top and bottom rows s.t. ypos +/- 1 is always valid
		## (rows are already padded by spaces on both ends, no reason not to)
		real_path[ 0] = (' ' * (len(path_rows[0]) - 1))
		real_path[-1] = (' ' * (len(path_rows[0]) - 1))

		for i in xrange(len(path_rows)):
			real_path[i + 1] = path_rows[i].strip("\n")

			assert(real_path[i + 1][ 0] == ' ')
			assert(real_path[i + 1][-1] == ' ')
			assert(len(path_rows[i]) == len(path_rows[0]))

		return real_path


def follow_path(path):
	hist = []
	muls = (-1, 1)

	xmax = len(path[0])
	ymax = len(path   )
	## start in *second* row; initial direction is down
	ypos = 1
	xpos = path[ypos].find('|')
	ydir = 1
	xdir = 0
	step = 0

	while (path[ypos][xpos] != ' '):
		char = path[ypos][xpos]
		turn = (char == '+')

		## change direction from vertical to horizontal or vv
		## no sign-flip for down<->right and up<->left turns
		dx = abs(ydir) * muls[ path[ypos    ][xpos - 1] == ' ' ]
		dy = abs(xdir) * muls[ path[ypos - 1][xpos    ] == ' ' ]

		## same but more verbose
		## dx  = 0
		## dy  = 0
		## dx += ((ydir != 0) * (path[ypos    ][xpos + 1] != ' '))
		## dx -= ((ydir != 0) * (path[ypos    ][xpos - 1] != ' '))
		## dy += ((xdir != 0) * (path[ypos + 1][xpos    ] != ' '))
		## dy -= ((xdir != 0) * (path[ypos - 1][xpos    ] != ' '))

		## if not a turn, keep going in previous direction
		xdir = xdir * (1 - turn) + dx * turn
		ydir = ydir * (1 - turn) + dy * turn

		## collect letters
		if (char.isalpha()):
			hist.append(char)

		## space marks end of the line; all lines are left- and
		## right-padded by spaces so out-of-bound positions can
		## can not occur
		assert((abs(xdir) + abs(ydir)) == 1)
		assert((xpos >= 0) and (xpos < xmax))
		assert((ypos >= 0) and (ypos < ymax))

		xpos += xdir
		ypos += ydir
		step += 1

	assert(path[ypos][xpos] == ' ')
	return (step, "".join(hist))


REAL_PATH = parse_input("day19.in")
TEST_PATH = [
	"                ",
	"     |          ",
	"     |  +--+    ",
	"     A  |  C    ",
	" F---|--|-E---+ ",
	"     |  |  |  D ",
	"     +B-+  +--+ ",
	"                ",
]

assert(follow_path(TEST_PATH) == (   38,     "ABCDEF"))
assert(follow_path(REAL_PATH) == (17302, "LXWCKGRAOY"))

