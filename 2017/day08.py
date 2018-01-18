import re

## grammar of test instructions is limited enough to not need an expression parser
## operators can only be >, <, >=, <=, ==, !=, keywords can only be "dec" and "inc"
PREF_REXP = r"([a-z]+)\s+(inc|dec)\s+(-?[0-9]+)\s+"
POST_REXP = r"(if)\s+([a-z]+)\s+([<>=!]+)\s+(-?[0-9]+)"
REG_OPERS = {"inc": "+=", "dec": "-="}

TEST_INSTS = []
REAL_INSTS = []


def parse_expr(expr, regs):
	## splitting by whitespace is less robust
	## mod_reg, reg_op, op_val, if_kw, cmp_reg, cmp_op, cmp_val = expr.split()

	match = re.search(PREF_REXP + POST_REXP, expr)

	assert(match != None)
	assert(len(match.groups()) == 7)

	mod_reg = match.group(1) ## "bkd" (target register)
	cmp_reg = match.group(5) ## "uly" (source register)

	reg_op  = match.group(2) ## "dec"
	op_val  = match.group(3) ## -976
	if_kw   = match.group(4) ## "if"
	cmp_op  = match.group(6) ## "<="
	cmp_val = match.group(7) ## -338

	## either do this or use a defaultdict
	if (not (cmp_reg in regs)): regs[cmp_reg] = 0
	if (not (mod_reg in regs)): regs[mod_reg] = 0

	return ("%s regs[\'%s\'] %s %s: regs[\'%s\'] %s %s" % (if_kw, cmp_reg, cmp_op, cmp_val, mod_reg, REG_OPERS[reg_op], op_val))


def parse_input(fn):
	with open(fn, 'r') as f:
		## strip newlines
		lines = f.readlines()
		insts = [raw_instr[0: -1] for raw_instr in lines]
		return insts


def exec_instrs(instrs):
	ex_env = {"regs": {}}

	max_exec_reg_val = 0
	max_post_reg_val = 0
	max_post_reg_key = ""

	for i in xrange(len(instrs)):
		regs = ex_env["regs"]
		expr = parse_expr(instrs[i], regs)

		## exec[ute] expr in env
		exec(expr, ex_env)
		max_exec_reg_val = max(max_exec_reg_val, max(regs.values()))

	for reg in ex_env["regs"]:
		if (ex_env["regs"][reg] <= max_post_reg_val):
			continue

		max_post_reg_val = ex_env["regs"][reg]
		max_post_reg_key = reg

	return (max_post_reg_val, max_exec_reg_val)


assert(exec_instrs(parse_input("day08_test.in")) == (   1,   10))
assert(exec_instrs(parse_input("day08.in"     )) == (6611, 6619))

