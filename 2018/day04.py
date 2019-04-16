from collections import defaultdict as ddict
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		## "[1518-10-03 00:47] (Guard #487 begins shift)|(falls asleep)|(wakes up)"
		rexprs = (
			r"\[([0-9]+-[0-9]+-[0-9]+)\s*([0-9]+:[0-9]+)\]\s*",
			r"Guard\s*#([0-9]+)\s*begins\s*shift"
		)

		mlist = [(re_search(rexprs[0], line[: -1]), re_search(rexprs[1], line[: -1]), line[19]) for line in f.readlines()]
		items = [None] * len(mlist)

		for i in xrange(len(mlist)):
			tup = mlist[i]
			ymd = tup[0].group(1) ## year-month-day
			hrm = tup[0].group(2) ## hour:minute
			ymd = ymd.split('-')
			hrm = hrm.split(':')

			if (tup[1] != None):
				assert(tup[2] == 'G')
				items[i] = (int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hrm[0]), int(hrm[1]),  's', int(tup[1].group(1)), tup[2])
			else:
				assert(tup[2] == 'f' or tup[2] == 'w')
				items[i] = (int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hrm[0]), int(hrm[1]),  tup[2], -1, tup[2])

		def item_sort_func(a, b):
			m = 100 * 100
			n = m * m
			i = (a[0] * n) + (a[1] * m * 100) + (a[2] * m) + (a[3] * 100) + a[4]
			j = (b[0] * n) + (b[1] * m * 100) + (b[2] * m) + (b[3] * 100) + b[4]
			if (i < j): return -1
			if (i > j): return +1
			return 0

		## sort by linearized date-time
		items.sort(item_sort_func)
		return items

	return []

def handle_input(items):
	guard_sleep_times = ddict(lambda: 0) ## {guard: sum(sleep-time<guard>)}
	guards_to_minutes = ddict(lambda: ddict(lambda: 0)) ## {guard: {minute: sum(minute-count<guard>)}}
	minutes_to_guards = ddict(lambda: ddict(lambda: 0)) ## {minute: {guard: sleep-count for minute}}
	## minutes_to_guards = [ddict(lambda: 0) for i in xrange(60)]

	current_guard_id  = -1
	laziest_guard_ids = [-1, -1]
	current_guard_sst = 0 ## starting minute of current guard's most recent sleep

	a = 0 ## maximum (cumulative) sleep-time over all guards
	b = 0 ## maximum (cumulative) sleep-time per minute over all guards
	c = 0 ## minute at which laziest guard spends most time asleep
	d = 0
	e = 0

	for item in items:
		if (item[5] == 's'):
			current_guard_id = item[6]
		elif (item[5] == 'f'):
			current_guard_sst = item[4]
		elif (item[5] == 'w'):
			## guards never sleep for more than 59 minutes
			guard_sleep_times[current_guard_id] += (item[4] - current_guard_sst)

			for k in xrange(item[4] - current_guard_sst):
				guards_to_minutes[current_guard_id][current_guard_sst + k] += 1
				minutes_to_guards[current_guard_sst + k][current_guard_id] += 1

	## find guard that spent the most cumulative minutes asleep
	for guard_id in guard_sleep_times:
		if (guard_sleep_times[guard_id] > a):
			a = guard_sleep_times[guard_id]
			laziest_guard_ids[0] = guard_id

	## and the minute that guard spends asleep the most
	for sleep_minute_num in guards_to_minutes[ laziest_guard_ids[0] ]:
		if (guards_to_minutes[ laziest_guard_ids[0] ][sleep_minute_num] > d):
			c = sleep_minute_num
			d = guards_to_minutes[ laziest_guard_ids[0] ][sleep_minute_num]

	## find guard most frequently asleep on the same minute
	for minute_num in minutes_to_guards:
		for guard_id in minutes_to_guards[minute_num]:
			if (minutes_to_guards[minute_num][guard_id] > b):
				e = minute_num
				b = minutes_to_guards[minute_num][guard_id]
				laziest_guard_ids[1] = guard_id

	return (laziest_guard_ids[0] * c, laziest_guard_ids[1] * e)

def handle_input_timed(inp):
	return (time(), handle_input(inp), time())



def run(inp, out):
	ret = handle_input_timed(inp)
	assert(ret[1] == out)
	print("[%s] dt=%fs" % (__file__, ret[2] - ret[0]))

run(parse_input(__file__[: -2] + "in.test"), (  10 * 24,   99 * 45))
run(parse_input(__file__[: -2] + "in"     ), (2917 * 25, 1489 * 33))

