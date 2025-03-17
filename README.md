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
  - JSON document storage and retrieval (both typed and generic)
  - Asynchronous operations using Tokio
  - Basic TTL support with priority queue-based expiration
  - HTTP API for language-agnostic access
  - Python client library

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
JSON GET: ~1-5µs (simple), ~1-500µs (complex)
JSON SET: ~4-7µs (simple), ~5-1200µs (complex)
Setup: ~40µs (node initialization)

Environment: MacBook Pro, Release build
```

For detailed benchmark information, see:
- [General benchmarks](docs/benchmarks.md)
- [Data size impact](docs/data_size_benchmarks.md)
- [Concurrent operations](docs/concurrent_benchmarks.md)
- [Bulk operations](docs/bulk_operations_benchmarks.md)
- [JSON operations](docs/json_benchmarks.md)

## 🔧 Quick Start

### Using Docker

The easiest way to get started with Volt is using Docker:

```bash
# Clone the repository
git clone https://github.com/alvarocperez/volt.git
cd volt

# Build and start the Docker container
docker-compose up -d

# The Volt server will be available at http://localhost:3000
```

### Building from Source

```bash
# Clone the repository
git clone https://github.com/alvarocperez/volt.git
cd volt

# Build in release mode
cargo build --release

# Run the server
cargo run --release --bin server

# Run the benchmarks
cargo bench
```

## 📘 Usage Example

### Using the Rust API

```rust
use volt::KVCluster;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct User {
    id: u64,
    name: String,
    email: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a new storage instance
    let mut cluster = KVCluster::new(100, 2);
    cluster.add_node("node1".to_string());
    
    // Basic operations
    cluster.set("key1".to_string(), b"value1".to_vec(), Some(Duration::from_secs(60))).await;
    
    if let Some(value) = cluster.get("key1") {
        println!("Value: {:?}", String::from_utf8_lossy(&value));
    }
    
    // JSON operations with typed data
    let user = User {
        id: 1,
        name: "John Doe".to_string(),
        email: "john@example.com".to_string(),
    };
    
    // Store JSON document
    cluster.set_json("user:1".to_string(), &user, None).await?;
    
    // Retrieve and deserialize JSON document
    if let Some(retrieved_user) = cluster.get_json::<User>("user:1")? {
        println!("User: {} ({})", retrieved_user.name, retrieved_user.email);
    }
    
    Ok(())
}
```

### Using the Python Client

```python
from volt_client import VoltClient

# Connect to a Volt server
client = VoltClient(host="localhost", port=3000)

# Basic string operations
client.set("hello", "world")
print(client.get("hello"))  # Outputs: world

# JSON operations
user = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "active": True
}

client.set_json("user:1", user)
retrieved_user = client.get_json("user:1")
print(f"User: {retrieved_user['name']} ({retrieved_user['email']})")
```

### Using the HTTP API Directly

```bash
# Set a value
curl -X POST -H "Content-Type: application/json" -d '{"value":"world"}' http://localhost:3000/kv/hello

# Get a value
curl http://localhost:3000/kv/hello

# Set a JSON value
curl -X POST -H "Content-Type: application/json" \
  -d '{"value":{"name":"John","email":"john@example.com"}}' \
  http://localhost:3000/json/user:1

# Get a JSON value
curl http://localhost:3000/json/user:1

# Delete a value
curl -X DELETE http://localhost:3000/kv/hello
```

## 🐍 Python Client

A Python client is available in the `python/` directory. To install:

```bash
cd python
pip install .
```

For more details, see the [Python client README](python/README.md).

## 🛣️ Development Roadmap

### Phase 1: Core Engine & Performance (Current)
- [x] Basic key-value operations
- [x] Initial concurrent access support
- [x] Basic TTL implementation
- [x] JSON document support
- [x] HTTP API
- [x] Python client
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
- [ ] JSON path queries and indexing

### Phase 4: Production Readiness
- [x] REST API
- [x] Docker support
- [ ] Persistence layer
- [ ] gRPC API
- [ ] Production monitoring tools

## 🛠️ Development

### Prerequisites
- Rust 1.70 or higher
- Cargo
- Docker (optional)

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
