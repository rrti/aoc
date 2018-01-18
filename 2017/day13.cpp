#define NUM_CALC_THREADS 4
#define   LIKELY(x) __builtin_expect((x), 1)
#define UNLIKELY(x) __builtin_expect((x), 0)

#include <cassert>
#include <cstdio>

#include <array>
#include <algorithm>

#if (NUM_CALC_THREADS > 0)
#include <atomic>
#include <thread>
#endif

#include "../lib/util.hpp"


// <depth, range>
typedef std::pair<uint32_t, uint32_t> fw_layer_t;
typedef std::array<fw_layer_t,  4> test_fw_t;
typedef std::array<fw_layer_t, 45> real_fw_t;

static test_fw_t TEST_FIREWALL = {{
	{0, 3},
	{1, 2},
	{4, 4},
	{6, 4},
}};

static real_fw_t REAL_FIREWALL = {{
	{0, 3},
	{1, 2},
	{2, 9},
	{4, 4},
	{6, 4},
	{8, 6},
	{10, 6},
	{12, 8},
	{14, 5},
	{16, 6},
	{18, 8},
	{20, 8},
	{22, 8},
	{24, 6},
	{26, 12},
	{28, 12},
	{30, 8},
	{32, 10},
	{34, 12},
	{36, 12},
	{38, 10},
	{40, 12},
	{42, 12},
	{44, 12},
	{46, 12},
	{48, 14},
	{50, 14},
	{52, 8},
	{54, 12},
	{56, 14},
	{58, 14},
	{60, 14},
	{64, 14},
	{66, 14},
	{68, 14},
	{70, 14},
	{72, 14},
	{74, 12},
	{76, 18},
	{78, 14},
	{80, 14},
	{86, 18},
	{88, 18},
	{94, 20},
	{98, 18},
}};

#if (NUM_CALC_THREADS > 0)
// technically redundant; 32-bit writes are atomic by themselves
static std::atomic<uint32_t> MIN_DELAY = {std::numeric_limits<uint32_t>::max()};
#endif


template<typename T> static uint32_t calc_packet_severity(const T& fw_layers) {
	uint32_t pkt_score = 0;

	for (const auto& fw_layer: fw_layers) {
		const uint32_t d = fw_layer.first;
		const uint32_t r = fw_layer.second;
		const uint32_t m = (r - 1) << 1;

		pkt_score += ((d * r) * ((d % m) == 0));
	}

	return pkt_score;
}


#if (NUM_CALC_THREADS > 0)
static uint32_t calc_min_packet_delay_thr(
	uint32_t thread_num,
	uint32_t num_threads,
	const real_fw_t& fw_layers
) {
	uint32_t pkt_delay = thread_num;

	// do not update local copy every iteration; atomic reads are slow
	uint32_t min_delay = MIN_DELAY;
	uint32_t num_iters = 0;

	for (size_t layer_idx = 0, layer_cnt = fw_layers.size(); layer_idx < layer_cnt && pkt_delay < min_delay; ) {
		const uint32_t k = (fw_layers[layer_idx].first  + pkt_delay);
		const uint32_t m = (fw_layers[layer_idx].second -         1) << 1;

		// UNLIKELY saves ~1ms compared to LIKELY; fewer misses
		if (UNLIKELY((k % m) == 0)) {
			layer_idx  = 0;
			pkt_delay += num_threads;
		} else {
			layer_idx += 1;
		}

		num_iters += 1;
		min_delay  = ((num_iters & ((1 << 13) - 1)) == 0)? MIN_DELAY.load(): min_delay;
	}

	MIN_DELAY = std::min(MIN_DELAY.load(), pkt_delay);
	return pkt_delay;
}
#endif


template<typename T> static uint32_t calc_min_packet_delay(const T& fw_layers) {
	uint32_t pkt_delay = 0;

	for (size_t layer_idx = 0, layer_cnt = fw_layers.size(); layer_idx < layer_cnt; ) {
		const uint32_t k = (fw_layers[layer_idx].first  + pkt_delay);
		const uint32_t m = (fw_layers[layer_idx].second -         1) << 1;

		#if 0
		const uint32_t z = ((k % m) != 0);

		layer_idx *= (    z);
		pkt_delay += (1 - z);
		layer_idx += (    z);

		#else

		if (UNLIKELY((k % m) == 0)) {
			layer_idx  = 0;
			pkt_delay += 1;
		} else {
			layer_idx += 1;
		}
		#endif
	}

	return pkt_delay;
}


int main() {
	util::system_timer clk;

	std::sort(TEST_FIREWALL.begin(), TEST_FIREWALL.end(), [](const fw_layer_t& a, const fw_layer_t& b) { return (a.second < b.second); });
	std::sort(REAL_FIREWALL.begin(), REAL_FIREWALL.end(), [](const fw_layer_t& a, const fw_layer_t& b) { return (a.second < b.second); });

	assert(calc_packet_severity(TEST_FIREWALL) ==   24);
	assert(calc_packet_severity(REAL_FIREWALL) == 1704);

	assert(calc_min_packet_delay(TEST_FIREWALL) ==      10);
	assert(calc_min_packet_delay(REAL_FIREWALL) == 3970918);

	// present some fake non-optimisable load
	for (size_t i = 0, n = 1000 * 1000 * 10; i < n; i++) {
		clk.tick_time();
	}


	#if (NUM_CALC_THREADS == 0)
	const uint32_t pkt_delay = calc_min_packet_delay(REAL_FIREWALL);
	const uint64_t exec_time = clk.tock_time();

	#else

	std::array<std::thread, NUM_CALC_THREADS> threads;

	for (uint32_t i = 0; i < NUM_CALC_THREADS; i++) {
		threads[i] = std::move(std::thread(calc_min_packet_delay_thr, i, NUM_CALC_THREADS, std::cref(REAL_FIREWALL)));
	}
	for (uint32_t i = 0; i < NUM_CALC_THREADS; i++) {
		threads[i].join();
	}

	const uint32_t pkt_delay = MIN_DELAY;
	const uint64_t exec_time = clk.tock_time();
	#endif


	printf("[%s] packet_delay=%dps exec_time=%.3fms\n", __func__, pkt_delay, exec_time / (1000.0f * 1000.0f));
	return 0;
}

