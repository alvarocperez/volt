# Concurrent Operations Benchmarks

This document details the concurrent operations performance tests for Volt, analyzing how the system behaves under different levels of concurrency.

## Test Configuration

- **Hardware**: MacBook Pro
- **Build**: Release mode
- **Runtime**: Tokio async runtime
- **Concurrency Mechanism**: Tokio tasks + Arc for shared state
- **Storage Backend**: DashMap concurrent hash map
- **Test Sizes**: 1, 10, 100, 1000 concurrent operations

## Operations Tested

### 1. Concurrent SET Operations
Multiple clients simultaneously writing different keys.

```rust
handles.push(task::spawn(async move {
    cluster.set(
        format!("concurrent_key_{}", i),
        format!("value_{}", i).into_bytes(),
        None
    ).await
}));
```

Results:
- 1 concurrent: 9.24µs [9.20-9.28µs]
- 10 concurrent: 14.43µs [14.39-14.48µs]
- 100 concurrent: 75.21µs [75.09-75.34µs]
- 1000 concurrent: 736.74µs [715.90-758.12µs]

Analysis:
- Near-linear scaling up to 100 operations
- Significant variance increase at 1000 operations (~5.7% range)
- Task spawning overhead dominates at low concurrency
- Memory allocation and scheduling impact visible at high concurrency

### 2. Concurrent GET Operations
Multiple clients simultaneously reading different keys.

```rust
handles.push(task::spawn(async move {
    cluster.get(&format!("concurrent_key_{}", i))
}));
```

Results:
- 1 concurrent: 7.81µs [7.79-7.83µs]
- 10 concurrent: 11.59µs [11.54-11.69µs]
- 100 concurrent: 37.87µs [37.80-37.95µs]
- 1000 concurrent: 441.58µs [440.80-442.40µs]

Analysis:
- Faster than SET operations at all concurrency levels
- Better scaling with increased concurrency
- Lower contention due to read-only nature

### 3. Mixed Operations (50% GET, 50% SET)
Simulating real-world mixed workload.

Results:
- 1 concurrent: 9.18µs
- 10 concurrent: 13.28µs
- 100 concurrent: 63.49µs
- 1000 concurrent: 583.37µs

Analysis:
- Performance between pure GET and SET scenarios
- Good indication of real-world performance
- Scales well with increased concurrency

## Performance Characteristics

### Latency Analysis
1. **Base Latency** (1 operation):
   - SET: 9.24µs [9.20-9.28µs]
   - GET: 7.81µs [7.79-7.83µs]
   - Ratio: ~1.18x faster for GET operations

2. **Scaling by Concurrency Level**:
   - 10 concurrent:
     * SET: 14.43µs [14.39-14.48µs]
     * GET: 11.59µs [11.54-11.69µs]
     * Ratio: ~1.24x faster for GET
   - 100 concurrent:
     * SET: 75.21µs [75.09-75.34µs]
     * GET: 37.87µs [37.80-37.95µs]
     * Ratio: ~1.99x faster for GET
   - 1000 concurrent:
     * SET: 736.74µs [715.90-758.12µs]
     * GET: 441.58µs [440.80-442.40µs]
     * Ratio: ~1.67x faster for GET

### Concurrency Impact
1. **Low Concurrency** (1-10 ops):
   - Minimal contention
   - Overhead mainly from task spawning
   - Near-linear scaling

2. **Medium Concurrency** (100 ops):
   - Visible but manageable contention
   - Good throughput/latency balance
   - Efficient resource utilization

3. **High Concurrency** (1000 ops):
   - Increased contention visible
   - Still maintains reasonable latency
   - No exponential degradation

## Observations and Recommendations

### Strong Points
1. Consistent performance scaling
2. Good handling of mixed workloads
3. No catastrophic degradation at high concurrency

### Areas for Improvement
1. Task spawning overhead at low concurrency
2. Some contention at high concurrency levels
3. Room for optimization in SET operations

### Usage Recommendations
1. Optimal performance at 10-100 concurrent operations
2. Consider batch operations for very high concurrency
3. GET operations more efficient for high-concurrency scenarios

## Future Work

1. **Optimization Opportunities**:
   - Batch operation support
   - Connection pooling
   - More efficient task management

2. **Additional Tests Needed**:
   - Longer duration stability tests
   - Variable payload sizes
   - Network latency impact
   - Memory usage under load

3. **Monitoring Improvements**:
   - Detailed latency distribution
   - Resource usage tracking
   - Contention hot-spots identification

## Raw Benchmark Data

### Methodology
- **Framework**: Criterion.rs
- **Sample Size**: 100 measurements per operation
- **Measurement**: Each result shows [min time, median time, max time]
- **Statistical Significance**: Outliers are detected and reported
- **Environment**: Single-threaded, local execution with async runtime

### Detailed Results

#### Concurrent SET Operations
```
Concurrent Operations/concurrent_set/1:
  Time: [9.2002 µs 9.2416 µs 9.2830 µs]
  Found 4 outliers among 100 measurements (4.00%)
    3 (3.00%) low mild
    1 (1.00%) high severe

Concurrent Operations/concurrent_set/10:
  Time: [14.388 µs 14.427 µs 14.475 µs]
  Found 11 outliers among 100 measurements (11.00%)
    1 (1.00%) low severe
    1 (1.00%) low mild
    3 (3.00%) high mild
    6 (6.00%) high severe

Concurrent Operations/concurrent_set/100:
  Time: [75.086 µs 75.210 µs 75.335 µs]
  Found 3 outliers among 100 measurements (3.00%)
    1 (1.00%) low mild
    2 (2.00%) high mild

Concurrent Operations/concurrent_set/1000:
  Time: [715.90 µs 736.74 µs 758.12 µs]
```

#### Concurrent GET Operations
```
Concurrent Operations/concurrent_get/1:
  Time: [7.7886 µs 7.8090 µs 7.8283 µs]
  Found 2 outliers among 100 measurements (2.00%)
    1 (1.00%) low severe
    1 (1.00%) high mild

Concurrent Operations/concurrent_get/10:
  Time: [11.540 µs 11.591 µs 11.687 µs]
  Found 4 outliers among 100 measurements (4.00%)
    1 (1.00%) high mild
    3 (3.00%) high severe

Concurrent Operations/concurrent_get/100:
  Time: [37.798 µs 37.873 µs 37.951 µs]
  Found 3 outliers among 100 measurements (3.00%)
    2 (2.00%) high mild
    1 (1.00%) high severe

Concurrent Operations/concurrent_get/1000:
  Time: [440.80 µs 441.58 µs 442.40 µs]
  Found 7 outliers among 100 measurements (7.00%)
    1 (1.00%) low mild
    2 (2.00%) high mild
    4 (4.00%) high severe
```

#### Mixed Operations (50% GET, 50% SET)
```
Concurrent Operations/concurrent_mixed/1:
  Time: [9.1470 µs 9.1846 µs 9.2205 µs]
  Found 6 outliers among 100 measurements (6.00%)
    1 (1.00%) low severe
    3 (3.00%) low mild
    1 (1.00%) high mild
    1 (1.00%) high severe

Concurrent Operations/concurrent_mixed/10:
  Time: [13.264 µs 13.282 µs 13.301 µs]
  Found 8 outliers among 100 measurements (8.00%)
    1 (1.00%) low severe
    3 (3.00%) high mild
    4 (4.00%) high severe

Concurrent Operations/concurrent_mixed/100:
  Time: [63.388 µs 63.486 µs 63.589 µs]
  Found 8 outliers among 100 measurements (8.00%)
    1 (1.00%) low severe
    2 (2.00%) low mild
    1 (1.00%) high mild
    4 (4.00%) high severe

Concurrent Operations/concurrent_mixed/1000:
  Time: [582.25 µs 583.37 µs 584.53 µs]
  Found 2 outliers among 100 measurements (2.00%)
    1 (1.00%) low mild
    1 (1.00%) high mild
```

### Statistical Analysis

1. **Measurement Stability**:
   - SET operations:
     * Low concurrency (1-10): 4-11% outliers
     * Medium concurrency (100): 3% outliers
     * High concurrency (1000): High variance (5.7% range) but no reported outliers
   - GET operations:
     * Low concurrency (1-10): 2-4% outliers
     * Medium concurrency (100): 3% outliers
     * High concurrency (1000): 7% outliers
   - Mixed operations:
     * Low concurrency (1-10): 6-8% outliers
     * Medium concurrency (100): 8% outliers
     * High concurrency (1000): 2% outliers

2. **Confidence Intervals**:
   - SET operations:
     * 1 concurrent: ~0.9% range (9.20-9.28µs)
     * 10 concurrent: ~0.6% range (14.39-14.48µs)
     * 100 concurrent: ~0.3% range (75.09-75.34µs)
     * 1000 concurrent: ~5.7% range (715.90-758.12µs)
   - GET operations:
     * 1 concurrent: ~0.5% range (7.79-7.83µs)
     * 10 concurrent: ~1.3% range (11.54-11.69µs)
     * 100 concurrent: ~0.4% range (37.80-37.95µs)
     * 1000 concurrent: ~0.4% range (440.80-442.40µs)
   - Mixed operations:
     * Generally tighter intervals than pure operations
     * Most stable at high concurrency (~0.4% range)

3. **Outlier Patterns**:
   - More outliers in low concurrency scenarios
   - SET operations show higher variance, especially at high concurrency
   - Mixed operations show balanced outlier distribution
   - High concurrency patterns:
     * SET: High variance (5.7% range) suggesting potential system-level impacts
     * GET: Tight range but more frequent outliers
     * Mixed: Most stable overall with balanced variance

### Notes on Methodology
- All benchmarks run on the same machine in sequence
- Each operation uses 100 bytes of data
- System was idle during measurements
- Each operation includes task spawning and async runtime overhead
- Criterion automatically warms up the system before measuring
- Results include task scheduling and coordination overhead

### Performance Stability Observations
1. **Task Scheduling Impact**:
   - Visible overhead in low concurrency operations
   - Better amortized in higher concurrency
   - Mixed operations show balanced overhead

2. **Concurrency Scaling**:
   - SET operations: Less predictable at high concurrency
   - GET operations: More consistent scaling
   - Mixed operations: Best stability at high concurrency

3. **System Behavior**:
   - Task spawning overhead significant at low concurrency
   - Memory allocation patterns affect SET variance
   - Async runtime shows good stability under load 