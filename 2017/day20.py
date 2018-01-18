import re
import time

class particle:
	def __init__(self, idx):
		self.idx = idx
		self.uid = idx

		self.pos = [0, 0, 0]
		self.vel = [0, 0, 0]
		self.acc = [0, 0, 0] ## constant after parse

	def parse_state(self, match):
		assert(match != None)
		assert(len(match.groups()) == 9)

		for j in xrange(3):
			self.pos[j] = int(match.group(1 + j))
			self.vel[j] = int(match.group(4 + j))
			self.acc[j] = int(match.group(7 + j))

	## forward Euler
	def step_state(self, t = 1):
		self.vel[0] += (self.acc[0] * t)
		self.vel[1] += (self.acc[1] * t)
		self.vel[2] += (self.acc[2] * t)
		self.pos[0] += (self.vel[0] * t)
		self.pos[1] += (self.vel[1] * t)
		self.pos[2] += (self.vel[2] * t)

	def calc_state(self, t):
		ax = self.acc[0]
		ay = self.acc[1]
		az = self.acc[2]
		vx = self.vel[0] + ax * t
		vy = self.vel[1] + ay * t
		vz = self.vel[2] + az * t  ## could also use t*(t+1) / 2 instead of t*t
		px = self.pos[0] + vx * t  ## vx * t + ax * t*t == (vx + ax * t) * t
		py = self.pos[1] + vy * t  ## vy * t + ay * t*t == (vy + ay * t) * t
		pz = self.pos[2] + vz * t  ## vz * t + az * t*t == (vz + az * t) * t
		return (px, py, pz, vx, vy, vz, ax, ay, az)

	def calc_linear_pos(self): return ((self.pos[0] * 10000 * 10000) + (self.pos[1] * 10000) + self.pos[2])
	def calc_origin_dist(self): return (abs(self.pos[0]) + abs(self.pos[1]) + abs(self.pos[2]))

	def calc_vel_scale(self):
		vx = self.vel[0]
		vy = self.vel[1]
		vz = self.vel[2]
		return ((vx * vx + vy * vy + vz * vz) ** 0.5)
	def calc_acc_scale(self):
		ax = self.acc[0]
		ay = self.acc[1]
		az = self.acc[2]
		return ((ax * ax + ay * ay + az * az) ** 0.5)



def parse_input(fn):
	coors_regex = "<(-?[0-9]+)\s*,\s*(-?[0-9]+)\s*,\s*(-?[0-9]+)>"
	state_regex = r"p=%s,\s+v=%s,\s+a=%s" % (coors_regex, coors_regex, coors_regex)

	with open(fn, 'r') as f:
		raw_lines = f.readlines()
		particles = [particle(i) for i in xrange(len(raw_lines))]

		for i in xrange(len(raw_lines)):
			particles[i].parse_state(re.search(state_regex, raw_lines[i].strip("\n")))

		return particles



"""
def calc_min_particle_acc(particles, max_particle_acc, max_particle_vel):
	min_particle_uid = 0
	min_particle_acc = max_particle_acc
	## min_particle_vel = max_particle_vel

	for p in particles:
		cur_particle_acc = p.calc_acc_scale()
		## cur_particle_vel = p.calc_vel_scale()

		if (cur_particle_acc >= min_particle_acc):
			continue

		min_particle_uid = p.uid
		min_particle_acc = cur_particle_acc

	return (min_particle_uid, min_particle_acc)
"""



"""
def calc_min_particle_dist_nc(particles, num_timesteps, max_particle_dst):
	## integrate a single particle; only correct when
	## also considering initial position and velocity
	min_particle_uid = calc_min_particle_acc(particles, min_particle_dst)[0]
	min_particle_ref = particles[min_particle_uid]

	for i in xrange(num_timesteps):
		min_particle_ref.step_state()

	return (min_particle_uid, min_particle_ref.calc_origin_dist(), len(particles))

def calc_min_particle_dist_nc(particles, num_timesteps, max_particle_dst):
	## integrate all particles; slowest
	for i in xrange(num_timesteps):
		for p in particles:
			p.step_state()

			cur_particle_dst = p.calc_origin_dist()
			max_particle_dst = max(max_particle_dst, cur_particle_dst)

	return (calc_min_particle_dist_pi(particles, max_particle_dst))
"""

def calc_min_particle_dist_nc(particles, num_timesteps, max_particle_dst):
	min_particle_uid = 0
	min_particle_dst = max_particle_dst

	## predict final positions for all particles; no collisions
	for p in particles:
		cur_particle_pos = p.calc_state(num_timesteps)[0: 3]
		cur_particle_dst = abs(cur_particle_pos[0]) + abs(cur_particle_pos[1]) + abs(cur_particle_pos[2])

		if (cur_particle_dst >= min_particle_dst):
			continue

		min_particle_dst = cur_particle_dst
		min_particle_uid = p.uid

	return (min_particle_uid, min_particle_dst, len(particles))

def calc_min_particle_dist_pi(particles, max_particle_dst):
	min_particle_uid = 0
	min_particle_dst = max_particle_dst

	## find minimum post-integration distance
	for p in particles:
		cur_particle_dst = p.calc_origin_dist()

		if (cur_particle_dst >= min_particle_dst):
			continue

		min_particle_uid = p.uid
		min_particle_dst = cur_particle_dst

	return (min_particle_uid, min_particle_dst, len(particles))



def integrate_particle_positions(particles, positions, num_timesteps, check_collisions):
	max_particle_dst = 0

	if (not check_collisions):
		return (calc_min_particle_dist_nc(particles, num_timesteps, 99999999999999.0))

	for i in xrange(num_timesteps):
		for p in particles:
			p.step_state()

			cur_particle_pos = tuple(p.pos)
			max_particle_dst = max(max_particle_dst, p.calc_origin_dist())

			## coordinates are integers, convert directly
			if (positions.has_key(cur_particle_pos)):
				positions[cur_particle_pos].append(p)
			else:
				positions[cur_particle_pos] = [p]

		## remove particles that collided
		for pos in positions:
			colliders = positions[pos]

			if (len(colliders) <= 1):
				continue

			for p in colliders:
				## remap indices (not id's); shrink list
				idx = p.idx

				particles[idx] = particles[-1]
				particles[idx].idx = idx

				particles.pop()

		positions.clear()

	## calculate minimum distance *after* the final timestep
	## len() is the number of particles that did not collide
	return (calc_min_particle_dist_pi(particles, max_particle_dst))


## NB:
##   should be no actual need to integrate, can calculate positions analytically
##   or track only the particles with smallest accelerations breaking any ties by
##   velocity, then position (the analytically calculated positions are different
##   than those resulting from Euler integration used here)
## assert(integrate_particle_positions(parse_input("day20.in"), 1000, False) == (344,  1057382, 1000))
assert(integrate_particle_positions(parse_input("day20.in"), {}, 1000, False) == (344,  2056382, 1000))
assert(integrate_particle_positions(parse_input("day20.in"), {}, 1000,  True) == (931, 11631297,  404))

