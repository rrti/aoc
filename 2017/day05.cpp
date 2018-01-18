#include <cassert>
#include <cstdint>
#include <cstring> // memset
#include <fstream>

#include <array>
#include <vector>

#include "../lib/util.hpp"


typedef int8_t t_jmp_mods[2];
constexpr static t_jmp_mods g_jmp_mods[2] = {{1,  1}, {1, -1}};


static uint32_t parse_input(std::vector<int32_t>& v) {
	std::ifstream s("day05.in", std::ios::in);

	v.clear();
	v.reserve(1024);

	while (s.good()) {
		char a[16];

		std::memset(&a[0], 0, 16);
		s.getline(&a[0], 16, '\n');

		if (a[0] == 0)
			break;

		v.push_back(std::atoi(a));
	}
	
	return (v.size());
}


// saves ~7ms compared to a std::vector
static std::array<int32_t, 2048> instr_arr;

static uint32_t exec_instrs(std::vector<int32_t>&& instr_vec, const t_jmp_mods& jmp_mods) {
	uint32_t cur_instr = 0;
	uint32_t num_jumps = 0;

	const int8_t jump_mods[] = {jmp_mods[0], jmp_mods[1]};
	const uint32_t num_instrs = instr_vec.size();

	assert(instr_vec.size() <= instr_arr.size());
	std::memcpy(instr_arr.data(), instr_vec.data(), instr_vec.size() * sizeof(instr_vec[0]));

	int32_t* instr_data = instr_arr.data();

	while (cur_instr < num_instrs) {
		#if 0
		const int32_t jump_size = instr_arr[cur_instr];

		instr_arr[cur_instr] += jump_mods[jump_size >= 3];
		// instr_arr[cur_instr] += jump_mods(jump_size);

		cur_instr += jump_size;
		#else
		int32_t* instr_ptr = &instr_data[cur_instr];
		int32_t  jump_size = *instr_ptr;

		cur_instr += jump_size;
		*instr_ptr += jump_mods[jump_size >= 3];
		#endif

		num_jumps += 1;
	}

	return num_jumps;
}


int main() {
	std::vector<int32_t> ins;
	util::system_timer clk;

	parse_input(ins);
	#if 1
	// warm cache with copies; ~108ms to ~58ms on final run
	// (this also helps to ensure dynamic frequency scaling
	// clocks the CPU to full speed from the detected load)
	// code is also ~8ms faster using int32_t versus int16_t
	exec_instrs(std::vector<int32_t>{ins}, g_jmp_mods[1]);
	exec_instrs(std::vector<int32_t>{ins}, g_jmp_mods[1]);
	exec_instrs(std::vector<int32_t>{ins}, g_jmp_mods[1]);
	exec_instrs(std::vector<int32_t>{ins}, g_jmp_mods[1]);
	#endif

	clk.tick_time();

	const uint32_t num_jumps = exec_instrs(std::move(ins), g_jmp_mods[1]);
	const uint64_t exec_time = clk.tock_time();

	printf("[%s] num_jumps=%u exec_time=%.3fms\n", __func__, num_jumps, exec_time / (1000.0f * 1000.0f));
	assert(num_jumps == 27502966);
	return 0;
}

