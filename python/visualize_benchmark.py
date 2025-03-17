import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any


def load_results(filename: str) -> Dict[str, Any]:
    """Load benchmark results from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def plot_string_operations(results: Dict[str, Any]) -> None:
    """Plot string operations performance by size."""
    # Extract data
    sizes = []
    set_times = []
    get_times = []
    delete_times = []
    
    if "string_operations" in results:
        for size_str, size_data in results["string_operations"].items():
            size = int(size_str)
            sizes.append(size)
            set_times.append(size_data["set"]["avg"])
            get_times.append(size_data["get"]["avg"])
            delete_times.append(size_data["delete"]["avg"])
    
    # Sort by size
    if sizes:
        sizes, set_times, get_times, delete_times = zip(*sorted(zip(sizes, set_times, get_times, delete_times)))
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Plot data
        plt.plot(sizes, set_times, 'o-', label='SET')
        plt.plot(sizes, get_times, 's-', label='GET')
        plt.plot(sizes, delete_times, '^-', label='DELETE')
        
        # Set logarithmic scale for better visualization
        plt.xscale('log')
        
        # Add labels and title
        plt.xlabel('Value Size (bytes)')
        plt.ylabel('Average Time (ms)')
        plt.title('String Operations Performance by Value Size')
        
        # Add grid and legend
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        
        # Save figure
        plt.tight_layout()
        plt.savefig('string_operations.png')
        print("String operations chart saved as string_operations.png")
    else:
        print("No string operations data found to plot")


def plot_json_operations(results: Dict[str, Any]) -> None:
    """Plot JSON operations performance by size."""
    # Extract data
    sizes = []
    set_times = []
    get_times = []
    
    if "json_operations" in results:
        for size_str, size_data in results["json_operations"].items():
            sizes.append(size_str)
            if "set" in size_data:
                set_times.append(size_data["set"]["avg"])
            if "get" in size_data:
                get_times.append(size_data["get"]["avg"])
    
    # Create figure
    if sizes and len(set_times) == len(sizes) and len(get_times) == len(sizes):
        plt.figure(figsize=(10, 6))
        
        # Set positions for bars
        x = np.arange(len(sizes))
        width = 0.35
        
        # Plot data
        plt.bar(x - width/2, set_times, width, label='SET_JSON')
        plt.bar(x + width/2, get_times, width, label='GET_JSON')
        
        # Add labels and title
        plt.xlabel('JSON Size (fields)')
        plt.ylabel('Average Time (ms)')
        plt.title('JSON Operations Performance by Size')
        plt.xticks(x, sizes)
        
        # Add grid and legend
        plt.grid(True, which="major", ls="--", alpha=0.5)
        plt.legend()
        
        # Save figure
        plt.tight_layout()
        plt.savefig('json_operations.png')
        print("JSON operations chart saved as json_operations.png")
    else:
        print("No JSON operations data found to plot")


def plot_operations_per_second(results: Dict[str, Any]) -> None:
    """Plot operations per second for different operations."""
    # Extract data
    operations = []
    ops_per_second = []
    categories = []
    
    # Process string operations
    if "string_operations" in results:
        for size_str, size_data in results["string_operations"].items():
            for op_name, op_data in size_data.items():
                operations.append(f"{op_name} (string {size_str})")
                ops_per_second.append(op_data["ops_per_second"])
                categories.append("String")
    
    # Process JSON operations
    if "json_operations" in results:
        for size_str, size_data in results["json_operations"].items():
            for op_name, op_data in size_data.items():
                operations.append(f"{op_name} (json {size_str})")
                ops_per_second.append(op_data["ops_per_second"])
                categories.append("JSON")
    
    if operations:
        # Sort by operations per second (descending)
        operations, ops_per_second, categories = zip(*sorted(zip(operations, ops_per_second, categories), 
                                                          key=lambda x: x[1], reverse=True))
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create color map
        colors = {'String': 'blue', 'JSON': 'green', 'TTL': 'red'}
        bar_colors = [colors[cat] for cat in categories]
        
        # Plot data
        bars = plt.barh(operations, ops_per_second, color=bar_colors)
        
        # Add labels and title
        plt.xlabel('Operations per Second')
        plt.ylabel('Operation')
        plt.title('Volt Database Performance: Operations per Second')
        
        # Add grid
        plt.grid(True, which="major", ls="--", alpha=0.5)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors[cat], label=cat) for cat in set(categories)]
        plt.legend(handles=legend_elements)
        
        # Save figure
        plt.tight_layout()
        plt.savefig('operations_per_second.png')
        print("Operations per second chart saved as operations_per_second.png")
    else:
        print("No operations data found to plot")


def plot_latency_distribution(results: Dict[str, Any]) -> None:
    """Plot latency distribution for key operations."""
    # Extract data
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
    
    if latencies:
        # Calculate distribution
        latencies.sort()
        n = len(latencies)
        
        p25 = latencies[int(n * 0.25)]
        p50 = latencies[int(n * 0.5)]
        p75 = latencies[int(n * 0.75)]
        p90 = latencies[int(n * 0.9)]
        p99 = latencies[int(n * 0.99)] if n >= 100 else latencies[-1]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create data for violin plot
        percentiles = ['Min', 'P25', 'P50', 'P75', 'P90', 'P99', 'Max']
        data = [latencies[0], p25, p50, p75, p90, p99, latencies[-1]]
        
        # Plot data
        plt.bar(percentiles, data)
        
        # Add labels and title
        plt.xlabel('Percentile')
        plt.ylabel('Latency (ms)')
        plt.title('Latency Distribution')
        
        # Add grid
        plt.grid(True, which="major", ls="--", alpha=0.5)
        
        # Save figure
        plt.tight_layout()
        plt.savefig('latency_distribution.png')
        print("Latency distribution chart saved as latency_distribution.png")
    else:
        print("No latency data found to plot")


def main():
    """Main function to visualize benchmark results."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python visualize_benchmark.py <results_file>")
        print("Example: python visualize_benchmark.py volt_benchmark_results.json")
        sys.exit(1)
    
    # Load results
    filename = sys.argv[1]
    print(f"Loading benchmark results from {filename}...")
    results = load_results(filename)
    
    # Create visualizations
    plot_string_operations(results)
    plot_json_operations(results)
    plot_operations_per_second(results)
    plot_latency_distribution(results)
    
    print("\nAll visualizations completed!")


if __name__ == "__main__":
    main() 