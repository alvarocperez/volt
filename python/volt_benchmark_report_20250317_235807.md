# Volt Database Performance Benchmark Report

**Date:** 2025-03-17 23:58:09  
**Host:** localhost  
**Port:** 3000  
**OS:** Unknown  
**CPU:** Unknown  
**Memory:** Unknown  
**Python Version:** Unknown  

## Executive Summary

This report presents the performance benchmark results for the Volt key-value database. The benchmark tests various operations including string and JSON operations with different data sizes.

### Key Findings

- **Average Throughput:** 1313.11 operations per second
- **Fastest Operation:** get (json, 1) - 1407.25 ops/sec
- **Slowest Operation:** set (json, 100) - 1115.25 ops/sec
- **String Size Impact:** 5.48% performance decrease from smallest to largest
- **JSON Complexity Impact:** 13.18% performance decrease from simplest to most complex

## Benchmark Configuration

- **Iterations:** 100 per operation
- **Warmup Iterations:** 10 per operation

## Detailed Results

### String Operations

| Value Size | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |
|------------|-----------|----------|----------|----------|---------|
| 10 bytes | delete | 0.627 | 0.977 | 0.745 | 1341.57 |
| 10 bytes | get | 0.614 | 2.126 | 0.746 | 1341.08 |
| 10 bytes | set | 0.649 | 1.269 | 0.773 | 1294.02 |
| 100 bytes | delete | 0.626 | 0.990 | 0.715 | 1398.64 |
| 100 bytes | get | 0.626 | 1.119 | 0.712 | 1404.93 |
| 100 bytes | set | 0.634 | 1.042 | 0.745 | 1341.67 |
| 1000 bytes | delete | 0.630 | 1.978 | 0.769 | 1300.50 |
| 1000 bytes | get | 0.628 | 7.352 | 0.846 | 1182.36 |
| 1000 bytes | set | 0.644 | 1.102 | 0.784 | 1275.78 |

### JSON Operations

| Fields | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |
|--------|-----------|----------|----------|----------|---------|
| 1 | delete | 0.635 | 1.048 | 0.724 | 1381.32 |
| 1 | get | 0.609 | 0.961 | 0.711 | 1407.25 |
| 1 | set | 0.648 | 0.983 | 0.739 | 1352.36 |
| 10 | delete | 0.635 | 0.983 | 0.725 | 1379.47 |
| 10 | get | 0.631 | 1.050 | 0.743 | 1345.63 |
| 10 | set | 0.649 | 1.679 | 0.773 | 1294.09 |
| 100 | delete | 0.622 | 1.032 | 0.737 | 1357.30 |
| 100 | get | 0.777 | 1.169 | 0.891 | 1122.71 |
| 100 | set | 0.804 | 1.095 | 0.897 | 1115.25 |

### TTL Operations

TTL operations were not included in this benchmark run.

## Performance Analysis

### Latency Distribution

- **Min Latency:** 0.711 ms
- **Median (P50) Latency:** 0.745 ms
- **P90 Latency:** 0.891 ms
- **P99 Latency:** 0.897 ms
- **Max Latency:** 0.897 ms

### JSON Performance

- **Small JSON:** GET 1407.248 ops/sec, SET 1352.356 ops/sec
- **Medium JSON:** GET 1345.626 ops/sec, SET 1294.091 ops/sec
- **Large JSON:** GET 1122.714 ops/sec, SET 1115.254 ops/sec

## Conclusion

The Volt database shows good performance in this benchmark, with an average throughput of 1313.11 operations per second.

The fastest operation was get on json data with 1 fields, achieving 1407.25 operations per second.

The slowest operation was set on json data with 100 fields, achieving 1115.25 operations per second.

Increasing the size of string values resulted in a 5.48% decrease in performance.
Increasing the complexity of JSON documents resulted in a 13.18% decrease in performance.

### Recommendations

- For latency-sensitive applications, consider using smaller values and simpler data structures
- For throughput-oriented applications, batch operations when possible

---

*This benchmark was generated automatically by the Volt Benchmark Tool.* 