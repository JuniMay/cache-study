#include "../unified.hpp"

#include <algorithm>
#include <cassert>
#include <map>
#include <vector>

#include "cache.h"

namespace unified {
extern PrefetchContext prefetch_context;
}

namespace {

unified::CacheContext cache_context;

}  // namespace

void CACHE::initialize_replacement() {
  ::cache_context.initialize(this, NUM_SET, NUM_WAY);
}

uint32_t CACHE::find_victim(
  uint32_t triggering_cpu,
  uint64_t instr_id,
  uint32_t set,
  const BLOCK* current_set,
  uint64_t ip,
  uint64_t full_addr,
  uint32_t type
) {
  auto begin =
    std::next(std::begin(::cache_context.metadata[this]), set * NUM_WAY);
  auto end = std::next(begin, NUM_WAY);

  size_t reuse_distance = ::cache_context.reuse_distances[this].at(set);

  // get the minimum priority
  auto victim = std::min_element(
    begin, end,
    [&](
      const unified::CacheLineMetadata& metadata1,
      const unified::CacheLineMetadata& metadata2
    ) {
      uint8_t priority1 = 0;
      priority1 += metadata1.age > reuse_distance ? 0 : 8;
      priority1 += metadata1.hit;
      priority1 +=
        unified::prefetch_context.query_future(this, metadata1.full_addr) > 0 ? 0 : 4;

      uint8_t priority2 = 0;
      priority2 += metadata2.age > reuse_distance ? 0 : 8;
      priority2 += metadata2.hit;
      priority2 +=
        unified::prefetch_context.query_future(this, metadata2.full_addr) > 0 ? 0 : 4;

      return priority1 < priority2 ||
             (priority1 == priority2 && metadata1.age < metadata2.age);
    }
  );

  assert(begin <= victim);
  assert(victim < end);

  return static_cast<uint32_t>(std::distance(begin, victim));
}

void CACHE::update_replacement_state(
  uint32_t triggering_cpu,
  uint32_t set,
  uint32_t way,
  uint64_t full_addr,
  uint64_t ip,
  uint64_t victim_addr,
  uint32_t type,
  uint8_t hit
) {
  auto begin =
    std::next(std::begin(::cache_context.metadata[this]), set * NUM_WAY);
  auto end = std::next(begin, NUM_WAY);

  auto& metadata = ::cache_context.metadata[this].at(set * NUM_WAY + way);

  for (auto it = begin; it != end; ++it) {
    it->age++;
  }

  if (hit) {
    ::cache_context.accumulators[this].at(set) += metadata.age;
    ::cache_context.num_hits[this].at(set)++;
    metadata.hit = true;
    metadata.age = 0;

    if (::cache_context.num_hits[this].at(set) == 32) {
      ::cache_context.reuse_distances[this].at(set) =
        ::cache_context.accumulators[this].at(set) >> 4;
      ::cache_context.accumulators[this].at(set) = 0;
      ::cache_context.num_hits[this].at(set) = 0;
    }
  } else {
    ::cache_context.num_misses[this].at(set)++;
  }
}

void CACHE::replacement_final_stats() {}