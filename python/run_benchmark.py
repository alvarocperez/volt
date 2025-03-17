#!/usr/bin/env python3
"""
Comprehensive benchmark runner for Volt database.
This script runs the benchmark, visualizes the results, and provides analysis.
"""

import os
import sys
import time
import subprocess
import json
from typing import Dict, Any, List, Tuple

# Configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3000
BENCHMARK_ITERATIONS = 3  # Number of times to run the benchmark for consistency
COMPARISON_DATABASES = {
    "redis": "Redis is an in-memory data structure store, used as a database, cache, and message broker.",
    "memcached": "Memcached is a general-purpose distributed memory-caching system.",
    "etcd": "etcd is a distributed key-value store designed for reliability and performance."
}


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)


def check_volt_running(host: str, port: int) -> bool:
    """Check if Volt database is running."""
    try:
        from volt_client import VoltClient
        client = VoltClient(host=host, port=port)
        return client.health()
    except Exception as e:
        print(f"Error connecting to Volt: {e}")
        return False


def run_benchmark(host: str, port: int) -> str:
    """Run the benchmark and return the results filename."""
    print_header("RUNNING VOLT DATABASE BENCHMARK")
    print(f"Target: {host}:{port}")
    
    # Generate a timestamp for the results file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"volt_benchmark_{timestamp}.json"
    
    # Run the benchmark
    cmd = [sys.executable, "benchmark.py", host, str(port)]
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        
        # Rename the results file with timestamp
        os.rename("volt_benchmark_results.json", results_file)
        print(f"Benchmark results saved to {results_file}")
        
        return results_file
    except subprocess.CalledProcessError as e:
        print(f"Error running benchmark: {e}")
        sys.exit(1)


def visualize_results(results_file: str) -> None:
    """Visualize the benchmark results."""
    print_header("VISUALIZING BENCHMARK RESULTS")
    
    cmd = [sys.executable, "visualize_benchmark.py", results_file]
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error visualizing results: {e}")


def load_results(filename: str) -> Dict[str, Any]:
    """Load benchmark results from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def analyze_results(results_file: str) -> None:
    """Analyze the benchmark results and provide insights."""
    print_header("BENCHMARK ANALYSIS")
    
    # Load results
    results = load_results(results_file)
    
    # Find fastest and slowest operations
    fastest_op = {"name": "", "test": "", "speed": 0}
    slowest_op = {"name": "", "test": "", "speed": float('inf')}
    
    for test_name, operations in results.items():
        for op_name, stats in operations.items():
            ops_per_sec = stats["operations_per_second"]
            
            if ops_per_sec > fastest_op["speed"]:
                fastest_op = {"name": op_name, "test": test_name, "speed": ops_per_sec}
            
            if ops_per_sec < slowest_op["speed"]:
                slowest_op = {"name": op_name, "test": test_name, "speed": ops_per_sec}
    
    # Analyze string operations by size
    string_sizes = []
    string_get_times = []
    string_set_times = []
    
    for key, data in results.items():
        if key.startswith("string_"):
            size = int(key.split("_")[1])
            string_sizes.append(size)
            if "get" in data:
                string_get_times.append((size, data["get"]["avg_ms"]))
            if "set" in data:
                string_set_times.append((size, data["set"]["avg_ms"]))
    
    # Sort by size
    string_get_times.sort(key=lambda x: x[0])
    string_set_times.sort(key=lambda x: x[0])
    
    # Calculate size impact
    size_impact_get = None
    size_impact_set = None
    
    if len(string_get_times) >= 2:
        smallest = string_get_times[0]
        largest = string_get_times[-1]
        size_ratio = largest[0] / smallest[0]
        time_ratio = largest[1] / smallest[1]
        size_impact_get = time_ratio / size_ratio
    
    if len(string_set_times) >= 2:
        smallest = string_set_times[0]
        largest = string_set_times[-1]
        size_ratio = largest[0] / smallest[0]
        time_ratio = largest[1] / smallest[1]
        size_impact_set = time_ratio / size_ratio
    
    # Print analysis
    print("\n1. PERFORMANCE OVERVIEW")
    print(f"   Fastest operation: {fastest_op['name']} ({fastest_op['test']}) - {fastest_op['speed']:.2f} ops/sec")
    print(f"   Slowest operation: {slowest_op['name']} ({slowest_op['test']}) - {slowest_op['speed']:.2f} ops/sec")
    print(f"   Performance ratio: {fastest_op['speed'] / slowest_op['speed']:.2f}x")
    
    print("\n2. SIZE IMPACT ANALYSIS")
    if size_impact_get is not None:
        print(f"   GET operations: For every 10x increase in size, latency increases by {size_impact_get * 10:.2f}x")
    if size_impact_set is not None:
        print(f"   SET operations: For every 10x increase in size, latency increases by {size_impact_set * 10:.2f}x")
    
    print("\n3. JSON OPERATIONS ANALYSIS")
    for size in ["small", "medium", "large"]:
        key = f"json_{size}"
        if key in results:
            if "get_json" in results[key] and "set_json" in results[key]:
                get_time = results[key]["get_json"]["avg_ms"]
                set_time = results[key]["set_json"]["avg_ms"]
                print(f"   {size.title()} JSON: GET {get_time:.3f}ms, SET {set_time:.3f}ms, Ratio: {set_time/get_time:.2f}x")
    
    print("\n4. LATENCY DISTRIBUTION")
    # Select a representative operation
    if "string_100" in results and "get" in results["string_100"]:
        stats = results["string_100"]["get"]
        p95_p50_ratio = stats["p95_ms"] / stats["median_ms"]
        p99_p50_ratio = stats["p99_ms"] / stats["median_ms"]
        print(f"   GET string_100: P95/P50 ratio: {p95_p50_ratio:.2f}x, P99/P50 ratio: {p99_p50_ratio:.2f}x")
        print(f"   This indicates {'high' if p99_p50_ratio > 3 else 'moderate' if p99_p50_ratio > 2 else 'low'} latency variability")
    
    print("\n5. COMPARISON WITH OTHER DATABASES")
    print("   Note: The following are typical performance characteristics based on published benchmarks.")
    print("   Actual performance depends on hardware, configuration, and workload.")
    
    # Typical performance ranges for common operations in other databases (ops/sec)
    # These are approximate values based on published benchmarks
    typical_ranges = {
        "redis": {"get": (80000, 150000), "set": (60000, 120000)},
        "memcached": {"get": (100000, 200000), "set": (80000, 150000)},
        "etcd": {"get": (10000, 30000), "set": (5000, 15000)}
    }
    
    # Get Volt's performance for comparison
    volt_get_ops = 0
    volt_set_ops = 0
    
    if "string_100" in results:
        if "get" in results["string_100"]:
            volt_get_ops = results["string_100"]["get"]["operations_per_second"]
        if "set" in results["string_100"]:
            volt_set_ops = results["string_100"]["set"]["operations_per_second"]
    
    for db, description in COMPARISON_DATABASES.items():
        print(f"\n   {db.upper()}: {description}")
        if db in typical_ranges:
            get_range = typical_ranges[db]["get"]
            set_range = typical_ranges[db]["set"]
            
            print(f"   - GET: {get_range[0]:,} - {get_range[1]:,} ops/sec")
            if volt_get_ops > 0:
                avg_other = (get_range[0] + get_range[1]) / 2
                ratio = avg_other / volt_get_ops
                print(f"     Volt comparison: {volt_get_ops:.2f} ops/sec ({1/ratio:.2f}x)")
            
            print(f"   - SET: {set_range[0]:,} - {set_range[1]:,} ops/sec")
            if volt_set_ops > 0:
                avg_other = (set_range[0] + set_range[1]) / 2
                ratio = avg_other / volt_set_ops
                print(f"     Volt comparison: {volt_set_ops:.2f} ops/sec ({1/ratio:.2f}x)")
    
    print("\n6. RECOMMENDATIONS")
    print("   Based on the benchmark results, here are some recommendations:")
    
    # Recommendations based on results
    if "string_10000" in results and "set" in results["string_10000"]:
        large_set_time = results["string_10000"]["set"]["avg_ms"]
        if large_set_time > 10:
            print("   - For large values (10KB+), consider sharding or compression to improve performance")
    
    if "json_large" in results and "set_json" in results["json_large"]:
        large_json_time = results["json_large"]["set_json"]["avg_ms"]
        if large_json_time > 20:
            print("   - For complex JSON documents, consider flattening structure or splitting into smaller documents")
    
    # General recommendations
    print("   - For read-heavy workloads, increase the number of nodes to improve throughput")
    print("   - For write-heavy workloads, consider batching operations when possible")
    print("   - Monitor memory usage as the database grows, especially with large values")
    print("   - For production use, implement proper error handling and retry logic in client applications")


def main():
    """Main function to run the benchmark and analyze results."""
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Check if Volt is running
    if not check_volt_running(host, port):
        print(f"Error: Volt database is not running at {host}:{port}")
        print("Please start the Volt database and try again.")
        sys.exit(1)
    
    # Run multiple benchmark iterations for consistency
    results_files = []
    for i in range(BENCHMARK_ITERATIONS):
        print(f"\nRunning benchmark iteration {i+1}/{BENCHMARK_ITERATIONS}...")
        results_file = run_benchmark(host, port)
        results_files.append(results_file)
    
    # Use the last results file for visualization and analysis
    final_results_file = results_files[-1]
    
    # Visualize results
    visualize_results(final_results_file)
    
    # Analyze results
    analyze_results(final_results_file)
    
    print("\nBenchmark complete! Review the analysis above and check the generated charts.")


if __name__ == "__main__":
    main() 