# 📊 Volt Benchmarks

This document details the current performance tests of Volt, their results, and limitations.

## Current Configuration

Benchmarks are run using:
- Criterion.rs for precise measurements
- Release build mode
- Tokio runtime for async operations
- DashMap for concurrent storage

## Implemented Tests

### 1. Cluster Setup
```rust
group.bench_function("setup", |b| {
    b.iter(|| {
        let mut cluster = KVCluster::new(100, 2);
        rt.block_on(async {
            cluster.add_node("node1".to_string());
            cluster.add_node("node2".to_string());
        });
        cluster
    })
});
```
- **Description**: Initialization of a cluster with two nodes
- **Configuration**: 100 virtual nodes, replication factor 2
- **Result**: ~40µs
- **Measured Components**:
  - Data structures creation
  - Consistent hash ring initialization
  - Node and async channel setup

### 2. SET Operation
```rust
group.bench_function("set", |b| {
    b.iter(|| {
        rt.block_on(async {
            cluster.set("key".to_string(), b"value".to_vec(), None).await
        })
    })
});
```
- **Description**: Simple write operation
- **Result**: ~4µs
- **Measured Components**:
  - Key hashing
  - Node location
  - DashMap write
  - Async runtime overhead

### 3. GET Operation
```rust
group.bench_function("get", |b| {
    b.iter(|| cluster.get("key"))
});
```
- **Description**: Simple read operation
- **Result**: ~80ns
- **Measured Components**:
  - Key hashing
  - Node location
  - DashMap read
- **Note**: Fastest operation due to being synchronous

### 4. DELETE Operation
```rust
group.bench_function("del", |b| {
    b.iter(|| {
        rt.block_on(async {
            cluster.del("key").await
        })
    })
});
```
- **Description**: Delete operation
- **Result**: ~3.7µs
- **Measured Components**:
  - Key hashing
  - Node location
  - DashMap deletion
  - Async runtime overhead

## Current Limitations

1. **Concurrency**
   - No truly concurrent operations measured
   - No evaluation of multiple client impact
   - No load testing performed

2. **Data**
   - Only small keys and values tested
   - No evaluation of data size impact
   - No testing with large data sets

3. **Features**
   - No TTL operations measured
   - No replication impact evaluated
   - No data redistribution testing

## Upcoming Improvements

### Phase 1: Concurrency
- [ ] Concurrent operations benchmark
- [ ] Multiple simultaneous clients testing
- [ ] Maximum throughput measurement

### Phase 2: Data
- [ ] Tests with different data sizes
- [ ] Large key sets evaluation
- [ ] Hash collision impact

### Phase 3: Features
- [ ] TTL operations performance
- [ ] Replication latency
- [ ] Redistribution overhead

## Results Comparison

| Operation | Latency | Notes |
|-----------|----------|-------|
| GET       | ~80ns    | Best case, synchronous read |
| SET       | ~4µs     | Includes async overhead |
| DELETE    | ~3.7µs   | Includes async overhead |
| SETUP     | ~40µs    | Complete initialization |

## Test Environment

- **Hardware**: MacBook Pro
- **Build**: Release
- **Rust**: 1.70+
- **OS**: macOS 