from collections import defaultdict as ddict
from re import search as re_search
from time import time

def parse_input(fn):
	with open(fn, 'r') as f:
		regex = r"Step ([A-Z]) must be finished before step ([A-Z]) can begin."
		lines = f.readlines()
		rules = [re_search(regex, line[: -1]) for line in lines]
		return rules

	return []

def all_parents_done(sub_task, tasks, edges_cp):
	num_parents_done = 0
	for parent in edges_cp[sub_task]:
		num_parents_done += (tasks[parent] == 1)
	return (num_parents_done == len(edges_cp[sub_task]))

def all_workers_idle(task_slaves, time_step):
	num_workers_done = 0
	for task_slave in task_slaves:
		num_workers_done += (1 - task_slave.has_task())
	return (num_workers_done == len(task_slaves))


def handle_input_part1(rules):
	edges_pc = ddict(lambda: [])
	edges_cp = ddict(lambda: {})

	task_names = ddict()
	task_queue = []
	task_order = ""

	for rule in rules:
		task_names[rule.group(1)] = 0
		task_names[rule.group(2)] = 0

		## parent -> [children]
		edges_pc[rule.group(1)] += [rule.group(2)]
		## child -> {parents}
		edges_cp[rule.group(2)][rule.group(1)] = 1

	## find task(s) with no parents
	for task in task_names:
		if (len(edges_cp[task]) == 0):
			task_queue.append(task)

	task_queue.sort()

	## check root-tasks
	for root_task in task_queue:
		assert(all_parents_done(root_task, task_names, edges_cp))


	while (len(task_queue) > 0):
		task_order += task_queue[0]

		cur_task = task_queue[0]
		sub_tasks = edges_pc[cur_task]
		## mark current task as done
		task_names[cur_task] = 1

		## expansion order is essentially BFS, but can not use indices
		## still unnecessary to copy the entire queue owing to sorting
		## alternative: lexicographically ordered priority-queue?
		## task_queue = task_queue[1: ]
		task_queue[0] = task_queue[-1]
		task_queue.pop()

		for sub_task in sub_tasks:
			if (all_parents_done(sub_task, task_names, edges_cp)):
				task_queue.append(sub_task)

		task_queue.sort()

	return task_order



def handle_input_part2(rules):
	class slave:
		def __init__(self, guid, task):
			self.guid = guid
			self.task = task ## (task_id, task_time + task_ttl)
		def __repr__(self):
			return ("<id=%d task_name='%s' done_time=%d>" % (self.guid, self.task[0], self.task[1]))
		def set_task(self, task_name, task_time):
			self.task = (task_name, task_time)
		def is_busy(self, time):
			return (time < self.task[1])
		def has_task(self):
			return (self.task[0] != '.')

	edges_pc = ddict(lambda: [])
	edges_cp = ddict(lambda: {})

	## test/live worker-count for part 2
	num_task_slaves = ((len(rules) < 10) and 2) or 5
	min_task_time = 60 * (num_task_slaves == 5)

	task_names = ddict()
	task_queue = []
	task_slaves = [slave(i, ('.', 0)) for i in xrange(num_task_slaves)]
	task_order = []

	for rule in rules:
		task_names[rule.group(1)] = 0
		task_names[rule.group(2)] = 0

		## parent -> [children]
		edges_pc[rule.group(1)] += [rule.group(2)]
		## child -> {parents}
		edges_cp[rule.group(2)][rule.group(1)] = 1

	for rule in rules:
		edges_pc[rule.group(1)].sort()

	## find task(s) with no parents
	for task in task_names:
		if (len(edges_cp[task]) == 0):
			task_queue.append(task)

	task_queue.sort()

	for root_task in task_queue:
		assert(all_parents_done(root_task, task_names, edges_cp))


	def update_slaves(task_slaves, task_queue, task_order, time_step):
		num_slaves_updated = 0

		for task_slave in task_slaves:
			if (not task_slave.has_task()):
				continue
			if (task_slave.is_busy(time_step)):
				continue

			## mark slave's current task as done
			slave_task = task_slave.task[0]
			task_names[slave_task] = 1

			task_order.append(slave_task)
			task_slave.set_task('.', 0)

			num_slaves_updated += 1

			## if slave is no longer busy, expand its now-done task
			## NB:
			##   two or more slaves can theoretically end a task on
			##   the same timestep and both expand the same subtask
			for sub_task in edges_pc[slave_task]:
				if (all_parents_done(sub_task, task_names, edges_cp)): ## and not (sub_task in task_queue)):
					task_queue.append(sub_task)

		task_queue.sort()
		return (num_slaves_updated > 0)

	def assign_tasks(task_queue, task_order, time_step):
		task_index = 0

		## assign as many workers on same time-step as possible
		for task_slave in task_slaves:
			if (task_index >= len(task_queue)):
				break
			if (task_slave.is_busy(time_step)):
				assert(task_slave.has_task())
				continue

			assert(all_parents_done(task_queue[task_index], task_names, edges_cp))

			if (task_slave.has_task()):
				task_names[task_slave.task[0]] = 1
				task_order.append(task_slave.task[0])

			task_slave.set_task(task_queue[task_index], time_step + min_task_time + (ord(task_queue[task_index]) + 1 - ord('A')))
			task_index += 1

		return task_queue[task_index: ]


	for time_step in xrange(1000000000):
		update_slaves(task_slaves, task_queue, task_order, time_step)

		if (len(task_queue) != 0):
			## if at least one task is available, it will be picked up
			## by an idle worker which means we can not be finished yet
			task_queue = assign_tasks(task_queue, task_order, time_step)
			continue

		if (all_workers_idle(task_slaves, time_step)):
			return ("".join(task_order), time_step)

	## unreachable
	assert(False)
	return ("", -1)

def handle_input_timed(fun, inp):
	return (time(), fun(inp), time())



def run(inp, out):
	ret_part1 = handle_input_timed(handle_input_part1, inp)
	ret_part2 = handle_input_timed(handle_input_part2, inp)
	assert(ret_part1[1] == out[0])
	assert(ret_part2[1] == out[1])
	print("[%s] dt=%fs" % (__file__, ret_part2[2] - ret_part1[0]))

run(parse_input(__file__[: -2] + "in.test"), (                    "CABDFE", (                    "CABFDE",  15)))
run(parse_input(__file__[: -2] + "in"     ), ("FHICMRTXYDBOAJNPWQGVZUEKLS", ("FHICMRYDTXBOPWAJQNVGZUEKLS", 946)))

