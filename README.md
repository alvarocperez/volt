# ⚡ Volt

[![Rust](https://img.shields.io/badge/rust-stable-brightgreen.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Volt is an experimental high-performance in-memory key-value store written in Rust. It focuses on achieving ultra-low latency operations, with sub-microsecond response times for key operations.

## 🎯 Project Goals

- **Ultra-Low Latency**: Sub-microsecond response times (~100-500ns) for key operations
- **High Concurrency**: Support for >1M requests/second with eventual consistency
- **Memory Efficiency**: Optimized for high-throughput, low-latency memory operations
- **Horizontal Scalability**: Dynamic node addition and automatic data redistribution

## 🚀 Current Features

- **Core Operations**:
  - Set/Get/Delete operations with string keys and byte values
  - Asynchronous operations using Tokio
  - Basic TTL support with priority queue-based expiration

- **Performance Characteristics**:
  - Lock-free concurrent access using `DashMap`
  - Efficient hash-based key distribution
  - Asynchronous operation handling

## 📊 Performance

Latest benchmarks (single node, local testing):

```
=== Operation Latencies ===
GET: ~80ns average (best case)
SET: ~4µs average
DEL: ~3.7µs average
Setup: ~40µs (node initialization)

Environment: MacBook Pro, Release build
```

For detailed benchmark information, see [benchmarks documentation](docs/benchmarks.md).

## 🔧 Quick Start

```bash
# Clone the repository
git clone https://github.com/alvarocperez/volt.git
cd volt

# Build in release mode
cargo build --release

# Run the benchmarks
cargo bench
```

## 📘 Usage Example

```rust
use volt::KVCluster;

#[tokio::main]
async fn main() {
    // Create a new storage instance
    let mut cluster = KVCluster::new(100, 2);
    cluster.add_node("node1".to_string());
    
    // Basic operations
    cluster.set("key1".to_string(), b"value1".to_vec(), Some(60)).await; // With 60s TTL
    
    if let Some(value) = cluster.get("key1") {
        println!("Value: {:?}", String::from_utf8_lossy(&value));
    }
}
```

## 🛣️ Development Roadmap

### Phase 1: Core Engine & Performance (Current)
- [x] Basic key-value operations
- [x] Initial concurrent access support
- [x] Basic TTL implementation
- [ ] Comprehensive benchmark suite
- [ ] Memory usage optimization
- [ ] Lock-free data structures optimization

### Phase 2: Scalability & Distribution
- [ ] Consistent hashing implementation
- [ ] Dynamic node management
- [ ] Automatic data sharding
- [ ] Replication with eventual consistency
- [ ] Node failure handling

### Phase 3: Advanced Features
- [ ] Custom eviction policies
- [ ] Vector storage for ML workloads
- [ ] Bulk operations support
- [ ] Advanced TTL management
- [ ] Performance monitoring

### Phase 4: Production Readiness
- [ ] Persistence layer
- [ ] REST/gRPC API
- [ ] Containerization
- [ ] Documentation and examples
- [ ] Production monitoring tools

## 🛠️ Development

### Prerequisites
- Rust 1.70 or higher
- Cargo

### Running Tests
```bash
# Run all tests
cargo test

# Run benchmarks
cargo bench
```

## 📝 Contributing

This is an experimental project in early stages. If you're interested in contributing, please:

1. Check the current issues and roadmap
2. Open an issue to discuss your proposed changes
3. Fork and submit a PR

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Project Status

This is currently a proof of concept focusing on core functionality and performance characteristics. The current implementation provides basic KV operations with promising latency characteristics (~80ns for reads, ~4µs for writes), but many planned features are still under development.
