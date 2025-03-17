# Volt Database Performance Benchmark Report

**Date:** 2025-03-17 23:56:12  
**Host:** localhost  
**Port:** 3000  
**OS:** Unknown  
**CPU:** Unknown  
**Memory:** Unknown  
**Python Version:** Unknown  

## Executive Summary

This report presents the performance benchmark results for the Volt key-value database. The benchmark tests various operations including string and JSON operations with different data sizes.

### Key Findings

- **Average Throughput:** 1286.86 operations per second
- **Fastest Operation:** delete (string, 10) - 1377.70 ops/sec
- **Slowest Operation:** set (json, 100) - 1077.35 ops/sec
- **String Size Impact:** 3.93% performance decrease from smallest to largest
- **JSON Complexity Impact:** 6.97% performance decrease from simplest to most complex

## Benchmark Configuration

- **Iterations:** 100 per operation
- **Warmup Iterations:** 10 per operation

## Detailed Results

### String Operations

| Value Size | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |
|------------|-----------|----------|----------|----------|---------|
| 10 bytes | delete | 0.593 | 1.457 | 0.726 | 1377.70 |
| 10 bytes | get | 0.637 | 1.276 | 0.730 | 1369.28 |
| 10 bytes | set | 0.630 | 1.156 | 0.749 | 1334.53 |
| 100 bytes | delete | 0.629 | 1.021 | 0.746 | 1340.23 |
| 100 bytes | get | 0.632 | 0.980 | 0.744 | 1344.15 |
| 100 bytes | set | 0.647 | 1.052 | 0.774 | 1291.82 |
| 1000 bytes | delete | 0.625 | 1.032 | 0.742 | 1348.18 |
| 1000 bytes | get | 0.630 | 3.867 | 0.778 | 1284.75 |
| 1000 bytes | set | 0.665 | 1.076 | 0.776 | 1288.05 |

### JSON Operations

| Fields | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |
|--------|-----------|----------|----------|----------|---------|
| 1 | delete | 0.643 | 4.153 | 0.803 | 1244.95 |
| 1 | get | 0.640 | 4.756 | 0.795 | 1257.85 |
| 1 | set | 0.654 | 1.061 | 0.778 | 1285.18 |
| 10 | delete | 0.651 | 1.149 | 0.762 | 1311.90 |
| 10 | get | 0.649 | 1.447 | 0.772 | 1295.66 |
| 10 | set | 0.651 | 1.884 | 0.790 | 1265.21 |
| 100 | delete | 0.614 | 1.177 | 0.750 | 1332.98 |
| 100 | get | 0.788 | 1.172 | 0.898 | 1113.70 |
| 100 | set | 0.803 | 2.540 | 0.928 | 1077.35 |

### TTL Operations

TTL operations were not included in this benchmark run.

## Performance Analysis

### Latency Distribution

- **Min Latency:** 0.726 ms
- **Median (P50) Latency:** 0.774 ms
- **P90 Latency:** 0.898 ms
- **P99 Latency:** 0.928 ms
- **Max Latency:** 0.928 ms

### JSON Performance

- **Small JSON:** GET 1257.851 ops/sec, SET 1285.181 ops/sec
- **Medium JSON:** GET 1295.658 ops/sec, SET 1265.208 ops/sec
- **Large JSON:** GET 1113.700 ops/sec, SET 1077.347 ops/sec

## Conclusion

The Volt database shows good performance in this benchmark, with an average throughput of 1286.86 operations per second.

The fastest operation was delete on string data with 10 bytes, achieving 1377.70 operations per second.

The slowest operation was set on json data with 100 fields, achieving 1077.35 operations per second.

Increasing the size of string values resulted in a 3.93% decrease in performance.
Increasing the complexity of JSON documents resulted in a 6.97% decrease in performance.

### Recommendations

- For latency-sensitive applications, consider using smaller values and simpler data structures
- For throughput-oriented applications, batch operations when possible

---

*This benchmark was generated automatically by the Volt Benchmark Tool.* 