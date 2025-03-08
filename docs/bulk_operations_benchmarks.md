# Bulk Operations Benchmarks

This document analyzes Volt's performance when handling bulk operations, focusing on sequential operations with varying quantities.

## Test Configuration

- **Hardware**: MacBook Pro
- **Build**: Release mode
- **Runtime**: Tokio async runtime
- **Storage**: DashMap concurrent hash map
- **Operation Counts**: 10, 100, 1,000, 10,000, 100,000 operations
- **Data Size**: Fixed 100 bytes per value

## Operations Tested

### 1. Sequential Bulk SET Operations
Writing multiple keys in sequence.

```rust
for i in 0..n {
    cluster.set(
        format!("bulk_key_{}", i),
        data.clone(),
        None
    ).await;
}
```

Results:
- 10 ops: 8.60µs (860ns per op)
- 100 ops: 84.15µs (841.5ns per op)
- 1,000 ops: 839.27µs (839.27ns per op)
- 10,000 ops: 8.66ms (866ns per op)
- 100,000 ops: 91.18ms (911.8ns per op)

Analysis:
- Very consistent per-operation latency (839-911ns)
- Minimal overhead from sequential access
- Near-perfect linear scaling up to 1K operations
- Slight performance degradation beyond 10K ops (~5% at 100K)

### 2. Sequential Bulk GET Operations
Reading multiple keys in sequence.

```rust
for i in 0..n {
    cluster.get(&format!("bulk_key_{}", i));
}
```

Results:
- 10 ops: 1.34µs (134ns per op)
- 100 ops: 13.74µs (137.4ns per op)
- 1,000 ops: 142.95µs (142.95ns per op)
- 10,000 ops: 1.45ms (145ns per op)
- 100,000 ops: 17.22ms (172.2ns per op)

Analysis:
- Highly consistent per-operation latency up to 10K ops
- Performance degradation pattern:
  * 134-145ns per op up to 10K operations
  * 172.2ns per op at 100K operations (~19% degradation)
- Superior scaling compared to SET operations

## Performance Characteristics

### Latency Analysis

1. **Per-Operation Cost by Scale**:
   - SET:
     * Small scale (≤100): 841-860ns
     * Medium scale (1K-10K): 839-866ns
     * Large scale (100K): 911.8ns
   - GET:
     * Small scale (≤100): 134-137ns
     * Medium scale (1K-10K): 142-145ns
     * Large scale (100K): 172.2ns

2. **GET/SET Performance Ratio**:
   - 10 ops: ~6.4x faster (134ns vs 860ns)
   - 100 ops: ~6.1x faster (137.4ns vs 841.5ns)
   - 1,000 ops: ~5.9x faster (142.95ns vs 839.27ns)
   - 10,000 ops: ~6.0x faster (145ns vs 866ns)
   - 100,000 ops: ~5.3x faster (172.2ns vs 911.8ns)

### Operation Count Impact

1. **Small Batches** (≤100 ops):
   - Extremely consistent performance
   - GET: 134-137ns per op
   - SET: 841-860ns per op
   - Ideal for transactional workloads

2. **Medium Batches** (1K - 10K ops):
   - Minimal performance degradation
   - GET: 142-145ns per op (~5% slower than small batches)
   - SET: 839-866ns per op (~stable)
   - Optimal efficiency range

3. **Large Batches** (100K ops):
   - Noticeable performance impact
   - GET: 172.2ns per op (~19% slower than medium batches)
   - SET: 911.8ns per op (~5% slower than medium batches)
   - Consider batch splitting

## System Behavior Analysis

### Resource Utilization
1. **CPU Usage**:
   - Efficient for small-medium batches
   - Increased pressure at large counts
   - Good instruction cache utilization

2. **Memory Patterns**:
   - Predictable allocation pattern
   - Low fragmentation risk
   - Efficient key storage

### Performance Bottlenecks
1. **Operation Processing**:
   - Key formatting overhead
   - Value cloning cost
   - Async runtime scheduling

2. **Data Structure Access**:
   - Hash table performance
   - Memory locality effects
   - Lock contention minimal

## Observations and Recommendations

### Strong Points
1. Exceptional consistency in per-operation latency
2. Near-linear scaling up to 10K operations
3. Predictable performance degradation

### Areas for Improvement
1. Large batch efficiency (>10K operations)
2. Memory reuse opportunities
3. Key generation efficiency

### Usage Recommendations
1. Optimal batch size: 1K-10K operations
2. Split 100K+ batches into 10K chunks
3. Prefer GET operations for large batches (better scaling)

## Future Work

1. **Optimization Opportunities**:
   - Batch operation API
   - Key space optimization
   - Memory pooling

2. **Additional Tests Needed**:
   - Mixed batch operations
   - Variable value sizes
   - Concurrent batch operations
   - Memory usage patterns

3. **Feature Enhancements**:
   - Atomic batch operations
   - Batch operation priorities
   - Smart batching strategies 

## Raw Benchmark Data

### Methodology
- **Framework**: Criterion.rs
- **Sample Size**: 100 measurements per operation
- **Measurement**: Each result shows [min time, median time, max time]
- **Statistical Significance**: Outliers are detected and reported
- **Environment**: Single-threaded, local execution

### Detailed Results

#### Sequential Bulk SET Operations
```
Bulk Operations/bulk_sequential_set/10:
  Time: [8.5417 µs 8.5999 µs 8.6645 µs]
  Found 8 outliers among 100 measurements (8.00%)
    7 (7.00%) high mild
    1 (1.00%) high severe

Bulk Operations/bulk_sequential_set/100:
  Time: [83.764 µs 84.147 µs 84.557 µs]
  Found 19 outliers among 100 measurements (19.00%)
    2 (2.00%) low severe
    3 (3.00%) low mild
    8 (8.00%) high mild
    6 (6.00%) high severe

Bulk Operations/bulk_sequential_set/1000:
  Time: [834.18 µs 839.27 µs 844.55 µs]
  Found 9 outliers among 100 measurements (9.00%)
    1 (1.00%) low mild
    7 (7.00%) high mild
    1 (1.00%) high severe

Bulk Operations/bulk_sequential_set/10000:
  Time: [8.6156 ms 8.6589 ms 8.7038 ms]
  Found 2 outliers among 100 measurements (2.00%)
    1 (1.00%) low mild
    1 (1.00%) high mild

Bulk Operations/bulk_sequential_set/100000:
  Time: [90.611 ms 91.180 ms 91.814 ms]
  Found 8 outliers among 100 measurements (8.00%)
    6 (6.00%) high mild
    2 (2.00%) high severe
```

#### Sequential Bulk GET Operations
```
Bulk Operations/bulk_sequential_get/10:
  Time: [1.3372 µs 1.3426 µs 1.3482 µs]
  Found 7 outliers among 100 measurements (7.00%)
    5 (5.00%) low mild
    1 (1.00%) high mild
    1 (1.00%) high severe

Bulk Operations/bulk_sequential_get/100:
  Time: [13.674 µs 13.743 µs 13.813 µs]
  Found 1 outliers among 100 measurements (1.00%)
    1 (1.00%) high severe

Bulk Operations/bulk_sequential_get/1000:
  Time: [142.25 µs 142.95 µs 143.69 µs]

Bulk Operations/bulk_sequential_get/10000:
  Time: [1.4434 ms 1.4485 ms 1.4536 ms]
  Found 1 outliers among 100 measurements (1.00%)
    1 (1.00%) low mild

Bulk Operations/bulk_sequential_get/100000:
  Time: [17.115 ms 17.218 ms 17.345 ms]
  Found 6 outliers among 100 measurements (6.00%)
    2 (2.00%) high mild
    4 (4.00%) high severe
```

### Statistical Analysis

1. **Measurement Stability**:
   - SET operations show higher variance:
     * Small batches (≤100): 8-19% outliers
     * Medium batches (1K-10K): 2-9% outliers
     * Large batches (100K): 8% outliers
   - GET operations more stable:
     * Small batches (≤100): 1-7% outliers
     * Medium batches (1K-10K): 0-1% outliers
     * Large batches (100K): 6% outliers

2. **Confidence Intervals**:
   - SET operations:
     * Small batches: ~1.5% range
     * Medium batches: ~1.2% range
     * Large batches: ~1.3% range
   - GET operations:
     * Small batches: ~0.8% range
     * Medium batches: ~1% range
     * Large batches: ~1.3% range

3. **Outlier Patterns**:
   - SET operations show more outliers overall
   - Higher variance in small batch sizes for SET
   - GET operations more consistent across sizes
   - Both show increased variance at 100K operations

### Notes on Methodology
- All benchmarks run on the same machine in sequence
- Fixed payload size of 100 bytes for all operations
- System was idle during measurements
- Each operation includes full end-to-end timing
- Criterion automatically warms up the system before measuring
- Results exclude initialization time (cluster setup)

### Performance Stability Observations
1. **SET Operations**:
   - Higher variance in small batches suggests scheduling overhead impact
   - More stable in medium-sized batches
   - Consistent degradation pattern at large sizes

2. **GET Operations**:
   - Very stable performance across most batch sizes
   - Minimal outliers in medium-sized batches
   - Predictable scaling with batch size
   - Some instability at very large batch sizes (100K)

3. **System Behavior**:
   - More outliers in write operations suggests memory allocation impact
   - Read operations show more predictable performance
   - Both operations maintain tight confidence intervals despite outliers 