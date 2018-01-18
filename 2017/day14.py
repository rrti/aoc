from day10 import *

NUM_GRID_ROWS = 128
NUM_GRID_COLS = 128

TEST_HEX_STRING = "a0c2017" ## "1010 0000 1100 0010 0000 0001 0111 0000"; 9 one-bits
TEST_KEY_STRING = "flqrgnkx-%d" ## use a format-string; saves a few concatenations
REAL_KEY_STRING = "uugsqrei-%d"

TEST_BIT_GRID = [0] * NUM_GRID_ROWS * NUM_GRID_COLS
REAL_BIT_GRID = [0] * NUM_GRID_ROWS * NUM_GRID_COLS


def grid_floodfill(bit_grid):
	stack = []
	group = -1

	## no diagonal connections
	ngb_offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]

	for row in xrange(NUM_GRID_ROWS):
		for col in xrange(NUM_GRID_COLS):
			## (inefficiently) flood-fill all 4-connected regions
			if (bit_grid[row * NUM_GRID_ROWS + col] != 1):
				continue

			stack.append((row, col))

			while (len(stack) > 0):
				coors = stack.pop()
				g_row = coors[0]
				g_col = coors[1]

				bit_grid[g_row * NUM_GRID_ROWS + g_col] = group

				for ngb_ofs in ngb_offsets:
					ngb_row = max(0, min(127, g_row + ngb_ofs[0]))
					ngb_col = max(0, min(127, g_col + ngb_ofs[1]))

					if (bit_grid[ngb_row * NUM_GRID_ROWS + ngb_col] != 1):
						continue

					stack.append((ngb_row, ngb_col))

			group -= 1

	if (False):
		gs = ""

		for row in xrange(NUM_GRID_ROWS / 8):
			for col in xrange(NUM_GRID_COLS / 8):
				gs += (" %02d " % abs(bit_grid[row * NUM_GRID_ROWS + col]))

			gs += "\n"

		print gs

	return (abs(group) - 1)


def calc_used_bits(hex_string):
	num_used = 0

	for c in hex_string:
		nibble = int(c, 16)

		for bit_indx in xrange(4):
			bit_mask  = 1 << bit_indx
			num_used += ((nibble & bit_mask) != 0)

	return num_used


def calc_used_squares(key_string, bit_grid):
	num_used = 0
	num_blks = 0

	for row in xrange(NUM_GRID_ROWS):
		byte_array = make_byte_array(key_string % row)
		hash_bytes = calc_byte_hash(REAL_STATE, byte_array, 64)

		assert(len(hash_bytes) == 16)

		## no need for hex-string conversion here
		## num_used += calc_used_bits(hash_to_hex_str(hash_bytes))

		for col in xrange(NUM_GRID_COLS / 8):
			byte = hash_bytes[col]
		
			for bit_indx in xrange(8):
				bit_mask  = 1 << bit_indx
				num_used += ((byte & bit_mask) != 0)

				## wrong way around; places least-significant bit on the left
				## bit_grid[row * NUM_GRID_ROWS + col * 8 + bit_indx] = int((byte & bit_mask) != 0)
				bit_grid[row * NUM_GRID_ROWS + col * 8 + (8 - bit_indx - 1)] = int((byte & bit_mask) != 0)

	return (num_used, grid_floodfill(bit_grid))


assert(calc_used_bits(TEST_HEX_STRING) == 9)
assert(calc_used_squares(TEST_KEY_STRING, TEST_BIT_GRID) == (8108, 1242))
assert(calc_used_squares(REAL_KEY_STRING, REAL_BIT_GRID) == (8194, 1141))

