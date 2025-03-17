# Volt Database Benchmark Tools

This directory contains tools for benchmarking the Volt key-value database performance.

## Prerequisites

- Python 3.7 or higher
- Volt database running (either locally or in Docker)
- Required Python packages (install with `pip install -r benchmark_requirements.txt`)

## Running the Benchmark

1. Make sure the Volt database is running:

```bash
# If using Docker
docker-compose up -d
```

2. Install the required packages:

```bash
pip install -r benchmark_requirements.txt
```

3. Run the benchmark:

```bash
# Default: localhost:3000
python benchmark.py

# Custom host/port
python benchmark.py 192.168.1.100 8080
```

The benchmark will:
- Test string operations (SET, GET, DELETE) with different value sizes
- Test JSON operations (SET_JSON, GET_JSON) with different complexity levels
- Test TTL operations
- Calculate statistics for each operation
- Save results to `volt_benchmark_results.json`

## Visualizing Results

After running the benchmark, you can visualize the results:

```bash
python visualize_benchmark.py volt_benchmark_results.json
```

This will generate several charts:
- `string_operations.png`: Performance of string operations by value size
- `json_operations.png`: Performance of JSON operations by complexity
- `operations_per_second.png`: Operations per second for all tested operations
- `latency_distribution.png`: Latency distribution for key operations

## Benchmark Configuration

You can modify the benchmark parameters in `benchmark.py`:

- `NUM_ITERATIONS`: Number of operations per test (default: 1000)
- `NUM_WARMUP`: Number of warmup operations before measuring (default: 100)
- `VALUE_SIZES`: Sizes of string values to test in bytes (default: [10, 100, 1000, 10000])
- `JSON_SIZES`: Complexity levels of JSON objects to test (default: ["small", "medium", "large"])

## Understanding the Results

The benchmark measures and reports the following metrics:

- **Min**: Minimum latency observed
- **Avg**: Average latency
- **Median**: Median latency (50th percentile)
- **P95**: 95th percentile latency
- **P99**: 99th percentile latency
- **Max**: Maximum latency observed
- **StdDev**: Standard deviation of latencies
- **Ops/sec**: Operations per second (calculated as 1000 / avg_ms)

All time measurements are in milliseconds.

## Example Results

Here's an example of what the benchmark results might look like:

```
================================================================================
VOLT DATABASE BENCHMARK RESULTS
================================================================================

## String 100 ##

Operation      Min (ms)   Avg (ms)   Median (ms) P95 (ms)   P99 (ms)   StdDev     Ops/sec       
-------------------------------------------------------------------------------
get            0.123      0.245      0.231      0.356      0.489      0.078      4081.63
set            0.345      0.567      0.543      0.789      0.912      0.123      1764.55
delete         0.234      0.456      0.432      0.654      0.789      0.098      2192.98

## Json Medium ##

Operation      Min (ms)   Avg (ms)   Median (ms) P95 (ms)   P99 (ms)   StdDev     Ops/sec       
-------------------------------------------------------------------------------
get_json       0.456      0.789      0.765      1.123      1.345      0.187      1267.43
set_json       0.678      1.234      1.198      1.567      1.789      0.234      810.37
```

## Performance Factors

Several factors can affect the performance of Volt:

1. **Network latency**: If the database is running remotely, network latency will impact results
2. **Value size**: Larger values generally result in higher latencies
3. **JSON complexity**: More complex JSON structures take longer to process
4. **Concurrent load**: Performance may degrade under high concurrent load
5. **Hardware resources**: CPU, memory, and disk speed affect performance
6. **Docker overhead**: Running in Docker may introduce slight overhead

## Comparing with Other Databases

When comparing Volt with other key-value databases, consider:

1. **Consistency model**: Volt uses eventual consistency which favors performance
2. **Persistence**: In-memory databases like Volt are faster than disk-based ones
3. **Feature set**: More features often mean more overhead
4. **Optimization level**: Volt is optimized for low-latency operations 