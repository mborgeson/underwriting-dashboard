"""
Excel Processing Benchmark Script

This script benchmarks the performance of the optimized Excel reader
against the original implementation.
"""

import time
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import both Excel reader implementations
from src.data_processing.excel_reader import process_excel_files as process_original
from src.data_processing.excel_reader_optimized import process_excel_files as process_optimized

# Import file finder
from src.data_processing.file_finder import find_underwriting_files

def benchmark_excel_processing(files, repeats=3):
    """
    Benchmark Excel processing with both implementations.
    
    Args:
        files: List of files to process
        repeats: Number of times to repeat the benchmark for reliable results
        
    Returns:
        Dictionary with benchmark results
    """
    results = {
        'original': [],
        'optimized_sequential': [],
        'optimized_parallel': []
    }
    
    logger.info(f"Running Excel processing benchmark with {len(files)} files")
    
    for i in range(repeats):
        logger.info(f"Benchmark run {i+1}/{repeats}")
        
        # Test original implementation
        logger.info("Testing original implementation")
        start_time = time.time()
        
        result_df = process_original(files)
        
        elapsed_time = time.time() - start_time
        results['original'].append(elapsed_time)
        logger.info(f"Original implementation: {elapsed_time:.2f} seconds")
        
        # Test optimized implementation (sequential)
        logger.info("Testing optimized implementation (sequential)")
        start_time = time.time()
        
        result_df = process_optimized(files, parallel=False)
        
        elapsed_time = time.time() - start_time
        results['optimized_sequential'].append(elapsed_time)
        logger.info(f"Optimized implementation (sequential): {elapsed_time:.2f} seconds")
        
        # Test optimized implementation (parallel)
        logger.info("Testing optimized implementation (parallel)")
        start_time = time.time()
        
        result_df = process_optimized(files, parallel=True)
        
        elapsed_time = time.time() - start_time
        results['optimized_parallel'].append(elapsed_time)
        logger.info(f"Optimized implementation (parallel): {elapsed_time:.2f} seconds")
    
    # Calculate averages
    for key in results:
        results[key] = sum(results[key]) / len(results[key])
    
    return results

def plot_results(results, output_path):
    """
    Plot benchmark results.
    
    Args:
        results: Dictionary with benchmark results
        output_path: Path to save the plot
    """
    # Create the output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a bar chart
    labels = ['Original', 'Optimized (Sequential)', 'Optimized (Parallel)']
    values = [
        results['original'],
        results['optimized_sequential'],
        results['optimized_parallel']
    ]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=['#ff9999', '#66b3ff', '#99ff99'])
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}s',
                ha='center', va='bottom')
    
    # Add speedup annotations
    original_time = results['original']
    seq_speedup = original_time / results['optimized_sequential']
    par_speedup = original_time / results['optimized_parallel']
    
    plt.text(1, results['optimized_sequential'] / 2,
            f'{seq_speedup:.2f}x faster',
            ha='center', va='center', color='black', fontweight='bold')
    
    plt.text(2, results['optimized_parallel'] / 2,
            f'{par_speedup:.2f}x faster',
            ha='center', va='center', color='black', fontweight='bold')
    
    plt.title('Excel Processing Performance Comparison')
    plt.ylabel('Time (seconds)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path)
    logger.info(f"Plot saved to {output_path}")

def main():
    """Main function to run the benchmark."""
    logger.info("Starting Excel processing benchmark")
    
    # Find files to use for benchmark
    logger.info("Finding underwriting files")
    included_files, _ = find_underwriting_files()
    
    if not included_files:
        logger.error("No files found for benchmarking")
        return
    
    # Limit to 5 files for benchmarking (or fewer if that's all that's available)
    file_count = min(5, len(included_files))
    benchmark_files = included_files[:file_count]
    
    logger.info(f"Running benchmark with {file_count} files")
    
    # Run the benchmark
    results = benchmark_excel_processing(benchmark_files)
    
    # Plot the results
    plot_results(results, "benchmark/results/excel_benchmark.png")
    
    # Print summary
    print("\nExcel Processing Benchmark Results:")
    print("==================================")
    print(f"Original implementation: {results['original']:.2f} seconds")
    print(f"Optimized implementation (sequential): {results['optimized_sequential']:.2f} seconds")
    print(f"Optimized implementation (parallel): {results['optimized_parallel']:.2f} seconds")
    print(f"Sequential speedup: {results['original'] / results['optimized_sequential']:.2f}x")
    print(f"Parallel speedup: {results['original'] / results['optimized_parallel']:.2f}x")
    print("\nResults have been plotted and saved to benchmark/results/excel_benchmark.png")

if __name__ == "__main__":
    main()