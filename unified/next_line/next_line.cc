#include "../unified.hpp"

#include <bitset>
#include <fstream>
#include <map>
#include <vector>

#include "cache.h"

namespace unified {
PrefetchContext prefetch_context;
}

void CACHE::prefetcher_initialize() {}

uint32_t CACHE::prefetcher_cache_operate(
  uint64_t addr,
  uint64_t ip,
  uint8_t cache_hit,
  bool useful_prefetch,
  uint8_t type,
  uint32_t metadata_in
) {
  uint64_t pf_addr = addr + (1 << LOG2_BLOCK_SIZE);
  prefetch_line(pf_addr, true, metadata_in);
  unified::prefetch_context.update(this, pf_addr);
  return metadata_in;
}

uint32_t CACHE::prefetcher_cache_fill(
  uint64_t addr,
  uint32_t set,
  uint32_t way,
  uint8_t prefetch,
  uint64_t evicted_addr,
  uint32_t metadata_in
) {
  return metadata_in;
}

void CACHE::prefetcher_cycle_operate() {}

void CACHE::prefetcher_final_stats() {
  std::fstream file("prefetcher_info.txt", std::ios::out);

  for (auto& [addr, info] : unified::prefetch_context.prefetch_info[this]) {
    file << addr << " " << info.prefetch_count << " " << info.estimated_distance
         << std::endl;
  }
}