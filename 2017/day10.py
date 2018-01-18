def ring_swap(t, a, b): elem_swap(t, a % len(t), b % len(t))
def elem_swap(t, a, b): t[a], t[b] = t[b], t[a]
"""
def elem_swap(t, a, b):
	v    = t[a]
	t[a] = t[b]
	t[b] = v
"""


def reverse_array_range(t, i, n):
	assert(type(t) == list)

	for j in xrange(n / 2):
		ring_swap(t, (i + j), (i + (n - 1) - j))

	return t


def make_byte_array(raw_chars, pad_bytes = [17, 31, 73, 47, 23]):
	assert(type(raw_chars) == str)

	bytes = [0] * (len(raw_chars) + len(pad_bytes))

	for i in xrange(len(raw_chars)): bytes[                 i] = ord(raw_chars[i])
	for i in xrange(len(pad_bytes)): bytes[len(raw_chars) + i] =     pad_bytes[i]

	return bytes


def sparse_to_dense_hash(state):
	dense_hash = [0] * 16

	for i in xrange(16):
		k = i * 16
		h = 0
		for j in xrange(k, k + 16):
			h ^= state[j]
		dense_hash[i] = h

	return dense_hash


def hash_to_hex_str(hash_bytes):
	## marginally slower
	## return ("".join("%02x" % byte for byte in hash_bytes))
	s = ""
	for byte in hash_bytes:
		s += ("%02x" % byte)
	return s


def calc_byte_hash(state, bytes, rounds):
	assert(type(state) == list)
	assert(type(bytes) == list)
	assert(max(bytes) <= len(state))

	cur_index = 0
	skip_size = 0

	## reset each call
	for i in xrange(len(state)):
		state[i] = i

	for k in xrange(rounds):
		for i in xrange(len(bytes)):
			reverse_array_range(state, cur_index % len(state), bytes[i])

			## index wraps around in calls to reverse()
			cur_index += (bytes[i] + skip_size)
			skip_size += 1

	if (rounds != 64):
		return (state[0] * state[1])

	assert(len(state) == 256)
	return (sparse_to_dense_hash(state))


REAL_STATE = [0] * 256
TEST_STATE = [0] * 5

## part 1
TEST_BYTE_ARR = [3, 4, 1, 5]
REAL_BYTE_ARR = [31, 2, 85, 1, 80, 109, 35, 63, 98, 255, 0, 13, 105, 254, 128, 33]
## part 2
TEST_INPUT_STR = "1,2,3"
REAL_INPUT_STR = "31,2,85,1,80,109,35,63,98,255,0,13,105,254,128,33"


assert(reverse_array_range([3, 4, 2, 1   ], 0, 4) == [1, 2, 4, 3   ])
assert(reverse_array_range([3, 4, 2, 1   ], 3, 1) == [3, 4, 2, 1   ])
assert(reverse_array_range([4, 3, 0, 1, 2], 1, 5) == [3, 4, 2, 1, 0])

assert(calc_byte_hash(TEST_STATE, TEST_BYTE_ARR, 1) ==   12)
assert(calc_byte_hash(REAL_STATE, REAL_BYTE_ARR, 1) == 6952)

assert(hash_to_hex_str(calc_byte_hash(REAL_STATE, make_byte_array(            ""), 64)) == "a2582a3a0e66e6e86e3812dcb672a272")
assert(hash_to_hex_str(calc_byte_hash(REAL_STATE, make_byte_array(    "AoC 2017"), 64)) == "33efeb34ea91902bb2f59c9920caa6cd")
assert(hash_to_hex_str(calc_byte_hash(REAL_STATE, make_byte_array(TEST_INPUT_STR), 64)) == "3efbe78a8d82f29979031a4aa0b16a9d")
assert(hash_to_hex_str(calc_byte_hash(REAL_STATE, make_byte_array(       "1,2,4"), 64)) == "63960835bcdc130f0b66d7ff4f6a5a8e")
assert(hash_to_hex_str(calc_byte_hash(REAL_STATE, make_byte_array(REAL_INPUT_STR), 64)) == "28e7c4360520718a5dc811d3942cf1fd")

