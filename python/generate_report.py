#!/usr/bin/env python3
"""
Generate a comprehensive benchmark report for Volt database.
This script takes benchmark results and creates a detailed Markdown report.
"""

import os
import sys
import json
import time
import platform
import socket
import datetime
from typing import Dict, Any, List, Tuple

# Configuration
TEMPLATE_FILE = "benchmark_report_template.md"
DEFAULT_VERSION = "0.1.0"


def load_results(filename: str) -> Dict[str, Any]:
    """Load benchmark results from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def get_system_info() -> Dict[str, str]:
    """Get system information for the report."""
    info = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": DEFAULT_VERSION,
        "environment": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "hardware": f"CPU: {platform.processor()}, Python: {platform.python_version()}"
    }
    
    # Try to get more detailed CPU info on Linux
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        info["hardware"] = f"CPU: {line.split(':', 1)[1].strip()}, Python: {platform.python_version()}"
                        break
        except:
            pass
    
    return info


def format_string_results(results: Dict[str, Any]) -> str:
    """Format string operation results for the report."""
    if "string_operations" not in results or not results["string_operations"]:
        return "No string operation results available."
    
    output = []
    output.append("| Value Size | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |")
    output.append("|------------|-----------|----------|----------|----------|---------|")
    
    for size, size_data in sorted(results["string_operations"].items(), key=lambda x: int(x[0])):
        for op, op_data in sorted(size_data.items()):
            output.append(f"| {size} bytes | {op} | {op_data['min']:.3f} | {op_data['max']:.3f} | {op_data['avg']:.3f} | {op_data['ops_per_second']:.2f} |")
    
    return "\n".join(output)


def format_json_results(results: Dict[str, Any]) -> str:
    """Format JSON operation results for the report."""
    if "json_operations" not in results or not results["json_operations"]:
        return "No JSON operation results available."
    
    output = []
    output.append("| Fields | Operation | Min (ms) | Max (ms) | Avg (ms) | Ops/sec |")
    output.append("|--------|-----------|----------|----------|----------|---------|")
    
    for size, size_data in sorted(results["json_operations"].items(), key=lambda x: int(x[0])):
        for op, op_data in sorted(size_data.items()):
            output.append(f"| {size} | {op} | {op_data['min']:.3f} | {op_data['max']:.3f} | {op_data['avg']:.3f} | {op_data['ops_per_second']:.2f} |")
    
    return "\n".join(output)


def format_ttl_results(results: Dict[str, Any]) -> str:
    """Format TTL operation results for the report."""
    return "TTL operations were not included in this benchmark run."


def calculate_avg_throughput(results: Dict[str, Any]) -> float:
    """Calculate the average throughput across all operations."""
    throughputs = []
    
    # Handle string operations
    if "string_operations" in results:
        for size, size_data in results["string_operations"].items():
            for op, op_data in size_data.items():
                throughputs.append(op_data["ops_per_second"])
    
    # Handle JSON operations
    if "json_operations" in results:
        for size, size_data in results["json_operations"].items():
            for op, op_data in size_data.items():
                throughputs.append(op_data["ops_per_second"])
    
    return sum(throughputs) / len(throughputs) if throughputs else 0


def find_fastest_slowest_ops(results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Find the fastest and slowest operations in the benchmark."""
    fastest = {"name": "", "type": "", "size": "", "ops_per_second": 0}
    slowest = {"name": "", "type": "", "size": "", "ops_per_second": float('inf')}
    
    # Process string operations
    if "string_operations" in results:
        for size, size_data in results["string_operations"].items():
            for op, op_data in size_data.items():
                ops_per_second = op_data["ops_per_second"]
                
                if ops_per_second > fastest["ops_per_second"]:
                    fastest = {
                        "name": op,
                        "type": "string",
                        "size": size,
                        "ops_per_second": ops_per_second
                    }
                
                if ops_per_second < slowest["ops_per_second"]:
                    slowest = {
                        "name": op,
                        "type": "string",
                        "size": size,
                        "ops_per_second": ops_per_second
                    }
    
    # Process JSON operations
    if "json_operations" in results:
        for size, size_data in results["json_operations"].items():
            for op, op_data in size_data.items():
                ops_per_second = op_data["ops_per_second"]
                
                if ops_per_second > fastest["ops_per_second"]:
                    fastest = {
                        "name": op,
                        "type": "json",
                        "size": size,
                        "ops_per_second": ops_per_second
                    }
                
                if ops_per_second < slowest["ops_per_second"]:
                    slowest = {
                        "name": op,
                        "type": "json",
                        "size": size,
                        "ops_per_second": ops_per_second
                    }
    
    return fastest, slowest


def calculate_size_impact(results: Dict[str, Any]) -> Tuple[float, float]:
    """Calculate the impact of value size on performance."""
    string_impact = 0.0
    json_impact = 0.0
    
    # Calculate string size impact
    if "string_operations" in results and len(results["string_operations"]) > 1:
        sizes = sorted([int(size) for size in results["string_operations"].keys()])
        if len(sizes) >= 2:
            smallest_size = str(sizes[0])
            largest_size = str(sizes[-1])
            
            # Calculate average performance for smallest size
            small_perf = 0.0
            count = 0
            for op, stats in results["string_operations"][smallest_size].items():
                small_perf += stats["ops_per_second"]
                count += 1
            small_perf /= count if count > 0 else 1
            
            # Calculate average performance for largest size
            large_perf = 0.0
            count = 0
            for op, stats in results["string_operations"][largest_size].items():
                large_perf += stats["ops_per_second"]
                count += 1
            large_perf /= count if count > 0 else 1
            
            # Calculate percentage decrease
            if small_perf > 0:
                string_impact = ((small_perf - large_perf) / small_perf) * 100
    
    # Calculate JSON size impact
    if "json_operations" in results and len(results["json_operations"]) > 1:
        sizes = sorted([int(size) for size in results["json_operations"].keys()])
        if len(sizes) >= 2:
            smallest_size = str(sizes[0])
            largest_size = str(sizes[-1])
            
            # Calculate average performance for smallest size
            small_perf = 0.0
            count = 0
            for op, stats in results["json_operations"][smallest_size].items():
                small_perf += stats["ops_per_second"]
                count += 1
            small_perf /= count if count > 0 else 1
            
            # Calculate average performance for largest size
            large_perf = 0.0
            count = 0
            for op, stats in results["json_operations"][largest_size].items():
                large_perf += stats["ops_per_second"]
                count += 1
            large_perf /= count if count > 0 else 1
            
            # Calculate percentage decrease
            if small_perf > 0:
                json_impact = ((small_perf - large_perf) / small_perf) * 100
    
    return string_impact, json_impact


def get_json_performance(results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Extract JSON performance metrics."""
    json_performance = {
        "small": {"get": 0, "set": 0},
        "medium": {"get": 0, "set": 0},
        "large": {"get": 0, "set": 0}
    }
    
    if "json_operations" in results:
        # Map numeric sizes to categories
        size_mapping = {}
        sizes = sorted([int(size) for size in results["json_operations"].keys()])
        
        if len(sizes) >= 1:
            size_mapping[str(sizes[0])] = "small"
        if len(sizes) >= 2:
            size_mapping[str(sizes[1])] = "medium"
        if len(sizes) >= 3:
            size_mapping[str(sizes[2])] = "large"
        
        # Extract performance metrics
        for size_str, size_data in results["json_operations"].items():
            category = size_mapping.get(size_str, "")
            if category and category in json_performance:
                if "get" in size_data:
                    json_performance[category]["get"] = size_data["get"]["ops_per_second"]
                if "set" in size_data:
                    json_performance[category]["set"] = size_data["set"]["ops_per_second"]
    
    return json_performance


def get_latency_distribution(results: Dict[str, Any]) -> Dict[str, float]:
    """Calculate the latency distribution across operations."""
    latencies = []
    
    # Collect all latencies from string operations
    if "string_operations" in results:
        for size_data in results["string_operations"].values():
            for op_data in size_data.values():
                latencies.append(1000 / op_data["ops_per_second"])  # Convert ops/sec back to ms
    
    # Collect all latencies from JSON operations
    if "json_operations" in results:
        for size_data in results["json_operations"].values():
            for op_data in size_data.values():
                latencies.append(1000 / op_data["ops_per_second"])  # Convert ops/sec back to ms
    
    # Calculate distribution
    if not latencies:
        return {"min": 0, "p25": 0, "p50": 0, "p75": 0, "p90": 0, "p99": 0, "max": 0}
    
    latencies.sort()
    n = len(latencies)
    
    return {
        "min": latencies[0],
        "p25": latencies[int(n * 0.25)],
        "p50": latencies[int(n * 0.5)],
        "p75": latencies[int(n * 0.75)],
        "p90": latencies[int(n * 0.9)],
        "p99": latencies[int(n * 0.99)] if n >= 100 else latencies[-1],
        "max": latencies[-1]
    }


def get_performance_rating(throughput: float) -> str:
    """Get a qualitative rating based on throughput."""
    if throughput > 5000:
        return "excellent"
    elif throughput > 1000:
        return "good"
    elif throughput > 500:
        return "acceptable"
    else:
        return "below expectations"


def generate_conclusion(results: Dict[str, Any], fastest_op: Dict[str, Any], slowest_op: Dict[str, Any]) -> str:
    """Generate a conclusion based on the benchmark results."""
    avg_throughput = calculate_avg_throughput(results)
    
    conclusion = []
    conclusion.append("## Conclusion")
    conclusion.append("")
    
    # Overall performance assessment
    if avg_throughput > 5000:
        performance = "excellent"
    elif avg_throughput > 1000:
        performance = "good"
    elif avg_throughput > 500:
        performance = "acceptable"
    else:
        performance = "below expectations"
    
    conclusion.append(f"The Volt database shows {performance} performance in this benchmark, " +
                     f"with an average throughput of {avg_throughput:.2f} operations per second.")
    conclusion.append("")
    
    # Fastest and slowest operations
    conclusion.append(f"The fastest operation was {fastest_op['name']} on {fastest_op['type']} data " +
                     f"with {fastest_op['size']} {'fields' if fastest_op['type'] == 'json' else 'bytes'}, " +
                     f"achieving {fastest_op['ops_per_second']:.2f} operations per second.")
    conclusion.append("")
    
    conclusion.append(f"The slowest operation was {slowest_op['name']} on {slowest_op['type']} data " +
                     f"with {slowest_op['size']} {'fields' if slowest_op['type'] == 'json' else 'bytes'}, " +
                     f"achieving {slowest_op['ops_per_second']:.2f} operations per second.")
    conclusion.append("")
    
    # Size impact
    string_impact, json_impact = calculate_size_impact(results)
    if string_impact > 0:
        conclusion.append(f"Increasing the size of string values resulted in a {string_impact:.2f}% decrease in performance.")
    if json_impact > 0:
        conclusion.append(f"Increasing the complexity of JSON documents resulted in a {json_impact:.2f}% decrease in performance.")
    conclusion.append("")
    
    # Recommendations
    conclusion.append("### Recommendations")
    conclusion.append("")
    
    if string_impact > 50 or json_impact > 50:
        conclusion.append("- Consider using smaller values when possible to maximize performance")
    
    if "json_operations" in results and "string_operations" in results:
        # Compare average JSON vs string performance
        json_avg = calculate_avg_throughput({"json_operations": results["json_operations"]})
        string_avg = calculate_avg_throughput({"string_operations": results["string_operations"]})
        
        if json_avg < string_avg * 0.7:  # JSON is significantly slower
            conclusion.append("- Use string values instead of JSON when complex data structures are not required")
        
    conclusion.append("- For latency-sensitive applications, consider using smaller values and simpler data structures")
    conclusion.append("- For throughput-oriented applications, batch operations when possible")
    
    return "\n".join(conclusion)


def generate_report(results_file: str, output_file: str) -> None:
    """Generate a benchmark report from the results file."""
    print(f"Generating benchmark report from {results_file}...")
    
    # Load results
    results = load_results(results_file)
    
    # Get system info
    system_info = get_system_info()
    
    # Format results
    string_results = format_string_results(results)
    json_results = format_json_results(results)
    ttl_results = format_ttl_results(results)
    
    # Calculate metrics
    avg_throughput = calculate_avg_throughput(results)
    fastest_op, slowest_op = find_fastest_slowest_ops(results)
    string_impact, json_impact = calculate_size_impact(results)
    json_perf = get_json_performance(results)
    latency_dist = get_latency_distribution(results)
    
    # Generate conclusion
    conclusion = generate_conclusion(results, fastest_op, slowest_op)
    
    # Get metadata
    metadata = results.get("metadata", {})
    host = metadata.get("host", "localhost")
    port = metadata.get("port", 3000)
    iterations = metadata.get("iterations", 0)
    warmup = metadata.get("warmup_iterations", 0)
    timestamp = metadata.get("timestamp", 0)
    test_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) if timestamp else "Unknown"
    
    # Prepare template variables
    template_vars = {
        "test_date": test_date,
        "host": host,
        "port": port,
        "iterations": iterations,
        "warmup": warmup,
        "os": system_info.get("os", "Unknown"),
        "cpu": system_info.get("cpu", "Unknown"),
        "memory": system_info.get("memory", "Unknown"),
        "python_version": system_info.get("python_version", "Unknown"),
        "avg_throughput": f"{avg_throughput:.2f}",
        "fastest_op_name": fastest_op["name"],
        "fastest_op_type": fastest_op["type"],
        "fastest_op_size": fastest_op["size"],
        "fastest_op_speed": f"{fastest_op['ops_per_second']:.2f}",
        "slowest_op_name": slowest_op["name"],
        "slowest_op_type": slowest_op["type"],
        "slowest_op_size": slowest_op["size"],
        "slowest_op_speed": f"{slowest_op['ops_per_second']:.2f}",
        "string_results": string_results,
        "json_results": json_results,
        "ttl_results": ttl_results,
        "string_impact": f"{string_impact:.2f}",
        "json_impact": f"{json_impact:.2f}",
        "small_json_get": f"{json_perf.get('small', {}).get('get', 0):.3f}",
        "small_json_set": f"{json_perf.get('small', {}).get('set', 0):.3f}",
        "medium_json_get": f"{json_perf.get('medium', {}).get('get', 0):.3f}",
        "medium_json_set": f"{json_perf.get('medium', {}).get('set', 0):.3f}",
        "large_json_get": f"{json_perf.get('large', {}).get('get', 0):.3f}",
        "large_json_set": f"{json_perf.get('large', {}).get('set', 0):.3f}",
        "min_latency": f"{latency_dist.get('min', 0):.3f}",
        "p50_latency": f"{latency_dist.get('p50', 0):.3f}",
        "p90_latency": f"{latency_dist.get('p90', 0):.3f}",
        "p99_latency": f"{latency_dist.get('p99', 0):.3f}",
        "max_latency": f"{latency_dist.get('max', 0):.3f}",
        "conclusion": conclusion
    }
    
    # Load template
    template_file = "benchmark_report_template.md"
    try:
        with open(template_file, "r") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template file '{template_file}' not found.")
        return
    
    # Replace template variables
    for key, value in template_vars.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    
    # Write report
    with open(output_file, "w") as f:
        f.write(template)
    
    print(f"Report generated successfully: {output_file}")
    
    # Print summary
    print("\nBenchmark Summary:")
    print(f"- Average throughput: {avg_throughput:.2f} ops/sec")
    print(f"- Fastest operation: {fastest_op['name']} ({fastest_op['ops_per_second']:.2f} ops/sec)")
    print(f"- Slowest operation: {slowest_op['name']} ({slowest_op['ops_per_second']:.2f} ops/sec)")
    if string_impact > 0:
        print(f"- String size impact: {string_impact:.2f}% performance decrease")
    if json_impact > 0:
        print(f"- JSON complexity impact: {json_impact:.2f}% performance decrease")


def main():
    """Main function to generate the benchmark report."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <results_file> [output_file]")
        print("Example: python generate_report.py volt_benchmark_results.json volt_benchmark_report.md")
        sys.exit(1)
    
    # Get filenames
    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "volt_benchmark_report.md"
    
    # Generate report
    generate_report(results_file, output_file)


if __name__ == "__main__":
    main() 