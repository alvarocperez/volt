#!/usr/bin/env python3
"""
Run all Volt benchmark tools in sequence.
This script runs the benchmark, visualizes the results, and generates a report.
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

# Configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3000


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print_header("CHECKING PREREQUISITES")
    
    # Check if Volt client is installed
    try:
        from volt_client import VoltClient
        print("✓ Volt client is installed")
    except ImportError:
        print("✗ Volt client is not installed. Please install it first:")
        print("  pip install -e .")
        return False
    
    # Check if required packages are installed
    required_packages = ["matplotlib", "numpy", "requests"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("✗ Some required packages are missing. Please install them:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    # Check if Volt server is running
    client = VoltClient(host=DEFAULT_HOST, port=DEFAULT_PORT)
    if client.health():
        print(f"✓ Volt server is running at {DEFAULT_HOST}:{DEFAULT_PORT}")
    else:
        print(f"✗ Volt server is not running at {DEFAULT_HOST}:{DEFAULT_PORT}")
        print("  Please start the Volt server and try again.")
        return False
    
    return True


def run_command(cmd: List[str], description: str) -> Tuple[int, str]:
    """Run a command and return the exit code and output."""
    print(f"\n> {description}")
    print(f"  Executing: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    output = ""
    for line in process.stdout:
        output += line
        print(f"  {line.rstrip()}")
    
    exit_code = process.wait()
    return exit_code, output


def main():
    """Main function to run all benchmark tools."""
    print_header("VOLT DATABASE BENCHMARK SUITE")
    print("This script will run all Volt benchmark tools in sequence.")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Generate timestamp for filenames
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"volt_benchmark_{timestamp}.json"
    report_file = f"volt_benchmark_report_{timestamp}.md"
    
    # Step 1: Run the benchmark
    print_header("STEP 1: RUNNING BENCHMARK")
    exit_code, _ = run_command(
        [sys.executable, "benchmark.py", host, str(port)],
        "Running benchmark"
    )
    
    if exit_code != 0:
        print("✗ Benchmark failed. Exiting.")
        sys.exit(1)
    
    # Rename the results file with timestamp
    os.rename("volt_benchmark_results.json", results_file)
    print(f"✓ Benchmark results saved to {results_file}")
    
    # Step 2: Visualize the results
    print_header("STEP 2: VISUALIZING RESULTS")
    exit_code, _ = run_command(
        [sys.executable, "visualize_benchmark.py", results_file],
        "Visualizing benchmark results"
    )
    
    if exit_code != 0:
        print("✗ Visualization failed. Continuing with report generation.")
    
    # Step 3: Generate the report
    print_header("STEP 3: GENERATING REPORT")
    exit_code, _ = run_command(
        [sys.executable, "generate_report.py", results_file, report_file],
        "Generating benchmark report"
    )
    
    if exit_code != 0:
        print("✗ Report generation failed.")
        sys.exit(1)
    
    print_header("BENCHMARK COMPLETE")
    print(f"Results file: {results_file}")
    print(f"Report file: {report_file}")
    print("\nVisualizations:")
    print("- string_operations.png")
    print("- json_operations.png")
    print("- operations_per_second.png")
    print("- latency_distribution.png")
    
    print("\nTo view the report, open the Markdown file in a Markdown viewer or convert it to HTML:")
    print(f"  python -m markdown {report_file} > {report_file.replace('.md', '.html')}")


if __name__ == "__main__":
    main() 