#ifndef CACHE_UNIFIED_HPP_
#define CACHE_UNIFIED_HPP_

#include <map>
#include <memory>
#include <vector>

#include "cache.h"

class CACHE;

namespace unified {

/// Metadata for a cache line.
struct CacheLineMetadata {
  /// The age of the cache line.
  /// This is used to estimate the reuse distance.
  size_t age;
  /// If the cache line was reused.
  bool hit;
  /// Full address of the cache line.
  uint64_t full_addr;
};

struct CacheContext {
  std::map<CACHE*, std::vector<CacheLineMetadata>> metadata;
  std::map<CACHE*, std::vector<uint8_t>> num_hits;
  std::map<CACHE*, std::vector<uint8_t>> num_misses;
  std::map<CACHE*, std::vector<size_t>> reuse_distances;
  std::map<CACHE*, std::vector<size_t>> accumulators;

  void initialize(CACHE* cache, size_t num_set, size_t num_way) {
    this->metadata[cache] = std::vector<CacheLineMetadata>(num_set * num_way);
    this->num_hits[cache] = std::vector<uint8_t>(num_set);
    this->num_misses[cache] = std::vector<uint8_t>(num_set);
    this->reuse_distances[cache] = std::vector<size_t>(num_set);
    this->accumulators[cache] = std::vector<size_t>(num_set);
  }
};

/// Use pre-prefetch distance to estimate a re-prefetch distance.
struct PrefetchInfo {
  size_t accumulator;
  size_t estimated_distance;
  size_t last_timestamp;
  size_t prefetch_count;

  PrefetchInfo()
    : accumulator(0),
      estimated_distance(0),
      last_timestamp(0),
      prefetch_count(0) {}
};

struct PrefetchContext {
  /// Address and information about prefetching in a certain cache.
  std::map<CACHE*, std::map<uint64_t, PrefetchInfo>> prefetch_info;

  std::map<CACHE*, size_t> timestamp_counters;

  void initialize(CACHE* cache) { this->timestamp_counters[cache] = 0; }

  /// query when(estimated) the cache line will be prefetched (again).
  size_t query_future(CACHE* cache, uint64_t full_addr) {
    auto& info_map = this->prefetch_info[cache];
    auto it = info_map.find(full_addr);
    if (it == info_map.end()) {
      return 0;
    }
    if (info_map[full_addr].prefetch_count <= 1) {
      return 0;
    }
    auto info = info_map[full_addr];
    return info.estimated_distance -
           (this->timestamp_counters[cache] - info.last_timestamp);
  }

  /// Register/Update a prefetch.
  void update(CACHE* cache, uint64_t full_addr) {
    auto& info_map = this->prefetch_info[cache];
    auto it = info_map.find(full_addr);
    if (it == info_map.end()) {
      info_map[full_addr] = PrefetchInfo();
    }
    auto& info = info_map[full_addr];

    info.prefetch_count++;

    if (info.prefetch_count > 1) {
      info.accumulator += this->timestamp_counters[cache] - info.last_timestamp;
    }
    info.last_timestamp = this->timestamp_counters[cache];
    info.estimated_distance = info.accumulator / info.prefetch_count;

    if (info.prefetch_count > 32) {
      info.accumulator = info.estimated_distance;
      info.prefetch_count = 1;
    }

    this->timestamp_counters[cache]++;
  }
};

}  // namespace unified

#endif  // CACHE_UNIFIED_HPP_