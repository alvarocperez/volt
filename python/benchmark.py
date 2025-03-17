import argparse
import json
import random
import string
import time
from typing import Dict, List, Tuple, Any, Callable
import os
import sys

# Add the parent directory to the path so we can import the volt_client module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from volt_client import VoltClient
except ImportError:
    print("Error: volt_client module not found. Make sure it's installed or in the correct path.")
    sys.exit(1)

# Constants for the benchmark
NUM_ITERATIONS = 100  # Reduced from 1000
NUM_WARMUP = 10  # Reduced from 100
VALUE_SIZES = [10, 100, 1000]  # Removed 10000
JSON_SIZES = [1, 10, 100]  # Reduced from [1, 10, 100, 1000]

# Helper functions
def generate_random_string(length: int) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_random_json(num_fields: int) -> Dict[str, str]:
    """Generate a random JSON object with the specified number of fields."""
    return {f"field_{i}": generate_random_string(10) for i in range(num_fields)}

def measure_operation(client: VoltClient, operation: str, key: str, value: str = None, json_value: Dict = None) -> float:
    """Measure the time it takes to perform an operation."""
    start_time = time.time()
    
    if operation == "set":
        client.set(key, value)
    elif operation == "get":
        client.get(key)
    elif operation == "delete":
        client.delete(key)
    elif operation == "set_json":
        client.set_json(key, json_value)
    elif operation == "get_json":
        client.get_json(key)
    
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds

def run_benchmark(client: VoltClient) -> Dict[str, Any]:
    """Run the benchmark and return the results."""
    results = {
        "string_operations": {},
        "json_operations": {}
    }
    
    # Benchmark string operations with different value sizes
    for size in VALUE_SIZES:
        print(f"\nBenchmarking string operations with {size} byte values...")
        
        # Prepare test data
        test_value = generate_random_string(size)
        
        # Warmup
        for i in range(NUM_WARMUP):
            warmup_key = f"benchmark:warmup:{size}:{i}"
            client.set(warmup_key, test_value)
            client.get(warmup_key)
            client.delete(warmup_key)
        
        # Benchmark
        set_times = []
        get_times = []
        delete_times = []
        
        for i in range(NUM_ITERATIONS):
            iteration_key = f"benchmark:string:{size}:{i}"
            
            # Measure set operation
            set_times.append(measure_operation(client, "set", iteration_key, test_value))
            
            # Measure get operation
            get_times.append(measure_operation(client, "get", iteration_key))
            
            # Measure delete operation
            delete_times.append(measure_operation(client, "delete", iteration_key))
        
        # Calculate statistics
        results["string_operations"][str(size)] = {
            "set": {
                "min": min(set_times),
                "max": max(set_times),
                "avg": sum(set_times) / len(set_times),
                "ops_per_second": 1000 / (sum(set_times) / len(set_times))
            },
            "get": {
                "min": min(get_times),
                "max": max(get_times),
                "avg": sum(get_times) / len(get_times),
                "ops_per_second": 1000 / (sum(get_times) / len(get_times))
            },
            "delete": {
                "min": min(delete_times),
                "max": max(delete_times),
                "avg": sum(delete_times) / len(delete_times),
                "ops_per_second": 1000 / (sum(delete_times) / len(delete_times))
            }
        }
    
    # Benchmark JSON operations with different sizes
    for size in JSON_SIZES:
        print(f"\nBenchmarking JSON operations with {size} fields...")
        
        # Prepare test data
        test_json = generate_random_json(size)
        
        # Warmup
        for i in range(NUM_WARMUP):
            warmup_key = f"benchmark:json:warmup:{size}:{i}"
            client.set_json(warmup_key, test_json)
            client.get_json(warmup_key)
            client.delete(warmup_key)
        
        # Benchmark
        set_times = []
        get_times = []
        delete_times = []
        
        for i in range(NUM_ITERATIONS):
            iteration_key = f"benchmark:json:{size}:{i}"
            
            # Measure set_json operation
            set_times.append(measure_operation(client, "set_json", iteration_key, json_value=test_json))
            
            # Measure get_json operation
            get_times.append(measure_operation(client, "get_json", iteration_key))
            
            # Measure delete operation
            delete_times.append(measure_operation(client, "delete", iteration_key))
        
        # Calculate statistics
        results["json_operations"][str(size)] = {
            "set": {
                "min": min(set_times),
                "max": max(set_times),
                "avg": sum(set_times) / len(set_times),
                "ops_per_second": 1000 / (sum(set_times) / len(set_times))
            },
            "get": {
                "min": min(get_times),
                "max": max(get_times),
                "avg": sum(get_times) / len(get_times),
                "ops_per_second": 1000 / (sum(get_times) / len(get_times))
            },
            "delete": {
                "min": min(delete_times),
                "max": max(delete_times),
                "avg": sum(delete_times) / len(delete_times),
                "ops_per_second": 1000 / (sum(delete_times) / len(delete_times))
            }
        }
    
    return results

def save_results(results: Dict[str, Any], output_file: str) -> None:
    """Save the benchmark results to a file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")

def main() -> None:
    """Main function to run the benchmark."""
    parser = argparse.ArgumentParser(description='Benchmark the Volt key-value store')
    parser.add_argument('host', help='The host where the Volt server is running')
    parser.add_argument('port', type=int, help='The port where the Volt server is listening')
    parser.add_argument('--output', default='volt_benchmark_results.json', help='Output file for the results')
    
    args = parser.parse_args()
    
    # Create a client
    client = VoltClient(args.host, args.port)
    
    print(f"Starting Volt benchmark on {args.host}:{args.port}...")
    print(f"Connected to Volt server at http://{args.host}:{args.port}")
    print(f"Running benchmark with {NUM_ITERATIONS} iterations per test (after {NUM_WARMUP} warmup iterations)")
    
    # Run the benchmark
    results = run_benchmark(client)
    
    # Add metadata
    results["metadata"] = {
        "host": args.host,
        "port": args.port,
        "iterations": NUM_ITERATIONS,
        "warmup_iterations": NUM_WARMUP,
        "timestamp": time.time(),
        "value_sizes": VALUE_SIZES,
        "json_sizes": JSON_SIZES
    }
    
    # Save the results
    save_results(results, args.output)
    
    print("\nBenchmark completed successfully!")

if __name__ == "__main__":
    main() 