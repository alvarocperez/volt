FROM rust:latest as builder

WORKDIR /usr/src/volt

# Copy the Cargo files for dependency caching
COPY Cargo.toml Cargo.lock ./

# Create a dummy main.rs and bench file to build dependencies
RUN mkdir -p src && \
    echo "fn main() {}" > src/main.rs && \
    echo "pub fn dummy() {}" > src/lib.rs && \
    mkdir -p benches && \
    echo "use criterion::{black_box, criterion_group, criterion_main, Criterion}; fn bench_dummy(_c: &mut Criterion) {} criterion_group!(benches, bench_dummy); criterion_main!(benches);" > benches/kv_bench.rs && \
    cargo build --release && \
    rm -rf src benches

# Copy the actual source code
COPY . .

# Build the application
RUN cargo build --release --bin server

# Create a smaller runtime image
FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /usr/src/volt/target/release/server .

# Set environment variables
ENV VOLT_HOST=0.0.0.0
ENV VOLT_PORT=3000
ENV VOLT_NODE_COUNT=3

# Expose the port
EXPOSE 3000

# Run the server
CMD ["./server"] 