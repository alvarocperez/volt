# Volt Database Performance Benchmark Report

**Date:** {{test_date}}  
**Host:** {{host}}  
**Port:** {{port}}  
**OS:** {{os}}  
**CPU:** {{cpu}}  
**Memory:** {{memory}}  
**Python Version:** {{python_version}}  

## Executive Summary

This report presents the performance benchmark results for the Volt key-value database. The benchmark tests various operations including string and JSON operations with different data sizes.

### Key Findings

- **Average Throughput:** {{avg_throughput}} operations per second
- **Fastest Operation:** {{fastest_op_name}} ({{fastest_op_type}}, {{fastest_op_size}}) - {{fastest_op_speed}} ops/sec
- **Slowest Operation:** {{slowest_op_name}} ({{slowest_op_type}}, {{slowest_op_size}}) - {{slowest_op_speed}} ops/sec
- **String Size Impact:** {{string_impact}}% performance decrease from smallest to largest
- **JSON Complexity Impact:** {{json_impact}}% performance decrease from simplest to most complex

## Benchmark Configuration

- **Iterations:** {{iterations}} per operation
- **Warmup Iterations:** {{warmup}} per operation

## Detailed Results

### String Operations

{{string_results}}

### JSON Operations

{{json_results}}

### TTL Operations

{{ttl_results}}

## Performance Analysis

### Latency Distribution

- **Min Latency:** {{min_latency}} ms
- **Median (P50) Latency:** {{p50_latency}} ms
- **P90 Latency:** {{p90_latency}} ms
- **P99 Latency:** {{p99_latency}} ms
- **Max Latency:** {{max_latency}} ms

### JSON Performance

- **Small JSON:** GET {{small_json_get}} ops/sec, SET {{small_json_set}} ops/sec
- **Medium JSON:** GET {{medium_json_get}} ops/sec, SET {{medium_json_set}} ops/sec
- **Large JSON:** GET {{large_json_get}} ops/sec, SET {{large_json_set}} ops/sec

{{conclusion}}

---

*This benchmark was generated automatically by the Volt Benchmark Tool.* 