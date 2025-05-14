"""
Database Benchmark Script

This script benchmarks the performance of the optimized database manager
against the original implementation.
"""

import time
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import both database implementations
from src.database import db_manager
from src.database import db_manager_optimized

# Import file processing
from src.data_processing.file_finder import find_underwriting_files
from src.data_processing.excel_reader import process_excel_files

def generate_test_data(num_rows: int) -> pd.DataFrame:
    """
    Generate test data for benchmarking.
    
    Args:
        num_rows: Number of rows to generate
        
    Returns:
        DataFrame with test data
    """
    logger.info(f"Generating {num_rows} rows of test data")
    
    # Generate random data
    data = {
        'File Name': [f"Test_File_{i}.xlsb" for i in range(num_rows)],
        'Absolute File Path': [f"/test/path/Test_File_{i}.xlsb" for i in range(num_rows)],
        'Deal Stage Subdirectory Name': np.random.choice(['Active UW', 'Closed', 'Realized'], num_rows),
        'Deal Stage Subdirectory Path': [f"/test/path/{np.random.choice(['Active UW', 'Closed', 'Realized'])}" for i in range(num_rows)],
        'Last Modified Date': pd.date_range(start='1/1/2024', periods=num_rows).strftime('%Y-%m-%d').tolist(),
        'File Size in Bytes': np.random.randint(1000, 10000000, num_rows),
        'Property Type': np.random.choice(['Multifamily', 'Office', 'Retail', 'Industrial'], num_rows),
        'Market': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Miami', 'Dallas'], num_rows),
        'Sub-Market': np.random.choice(['Downtown', 'Midtown', 'Uptown', 'Suburbs'], num_rows),
        'Deal Status': np.random.choice(['Pending', 'Closed', 'Failed'], num_rows),
        'Property Class': np.random.choice(['A', 'B', 'C', 'D'], num_rows),
        'Property Value': np.random.uniform(1000000, 50000000, num_rows),
        'Acquisition Price': np.random.uniform(800000, 40000000, num_rows),
        'NOI': np.random.uniform(50000, 2000000, num_rows),
        'Cap Rate': np.random.uniform(0.04, 0.08, num_rows),
    }
    
    return pd.DataFrame(data)

def benchmark_insert(original_db_path: Path, optimized_db_path: Path, test_data: pd.DataFrame) -> dict:
    """
    Benchmark insert operations.
    
    Args:
        original_db_path: Path to the original database
        optimized_db_path: Path to the optimized database
        test_data: DataFrame with test data
        
    Returns:
        Dictionary with benchmark results
    """
    logger.info("Benchmarking insert operations")
    
    results = {}
    
    # Original implementation
    logger.info("Testing original implementation")
    original_db = db_manager.DatabaseManager(original_db_path)
    original_db.setup_database()
    
    start_time = time.time()
    db_manager.store_data(test_data)
    original_time = time.time() - start_time
    
    results['original_insert'] = original_time
    logger.info(f"Original implementation: {original_time:.2f} seconds")
    
    # Optimized implementation
    logger.info("Testing optimized implementation")
    optimized_db = db_manager_optimized.DatabaseManager(optimized_db_path)
    optimized_db.setup_database()
    
    start_time = time.time()
    db_manager_optimized.store_data(test_data)
    optimized_time = time.time() - start_time
    
    results['optimized_insert'] = optimized_time
    logger.info(f"Optimized implementation: {optimized_time:.2f} seconds")
    
    # Batch insert (optimized only)
    logger.info("Testing batch insert")
    start_time = time.time()
    db_manager_optimized.batch_store_data(test_data, batch_size=100)
    batch_time = time.time() - start_time
    
    results['batch_insert'] = batch_time
    logger.info(f"Batch insert: {batch_time:.2f} seconds")
    
    return results

def benchmark_query(original_db_path: Path, optimized_db_path: Path) -> dict:
    """
    Benchmark query operations.
    
    Args:
        original_db_path: Path to the original database
        optimized_db_path: Path to the optimized database
        
    Returns:
        Dictionary with benchmark results
    """
    logger.info("Benchmarking query operations")
    
    results = {}
    
    # Setup database managers
    original_db = db_manager.DatabaseManager(original_db_path)
    optimized_db = db_manager_optimized.DatabaseManager(optimized_db_path)
    
    # Get all data
    logger.info("Testing get_all_data")
    
    start_time = time.time()
    original_data = db_manager.get_all_data()
    original_time = time.time() - start_time
    
    start_time = time.time()
    optimized_data = db_manager_optimized.get_all_data()
    optimized_time = time.time() - start_time
    
    results['original_get_all'] = original_time
    results['optimized_get_all'] = optimized_time
    
    logger.info(f"Get all data - Original: {original_time:.2f} seconds, Optimized: {optimized_time:.2f} seconds")
    
    # Filtered data
    logger.info("Testing get_filtered_data")
    filters = {
        'Property Type': 'Multifamily',
        'Market': 'New York'
    }
    
    start_time = time.time()
    original_filtered = db_manager.get_filtered_data(filters)
    original_time = time.time() - start_time
    
    start_time = time.time()
    optimized_filtered = db_manager_optimized.get_filtered_data(filters)
    optimized_time = time.time() - start_time
    
    results['original_filter'] = original_time
    results['optimized_filter'] = optimized_time
    
    logger.info(f"Filtered data - Original: {original_time:.2f} seconds, Optimized: {optimized_time:.2f} seconds")
    
    # Search data
    logger.info("Testing search_data")
    
    start_time = time.time()
    original_search = db_manager.search_data("New York")
    original_time = time.time() - start_time
    
    start_time = time.time()
    optimized_search = db_manager_optimized.search_data("New York")
    optimized_time = time.time() - start_time
    
    results['original_search'] = original_time
    results['optimized_search'] = optimized_time
    
    logger.info(f"Search data - Original: {original_time:.2f} seconds, Optimized: {optimized_time:.2f} seconds")
    
    # Test aggregated data (optimized only)
    logger.info("Testing aggregated data")
    
    start_time = time.time()
    group_by = ["Property_Type", "Market"]
    metrics = {"Property_Value": "sum", "Acquisition_Price": "avg", "id": "count"}
    aggregated_data = db_manager_optimized.get_aggregated_data(group_by, metrics)
    optimized_time = time.time() - start_time
    
    results['optimized_aggregate'] = optimized_time
    
    logger.info(f"Aggregated data - Optimized: {optimized_time:.2f} seconds")
    
    return results

def plot_results(insert_results: dict, query_results: dict, output_path: Path) -> None:
    """
    Plot benchmark results.
    
    Args:
        insert_results: Results from insert benchmark
        query_results: Results from query benchmark
        output_path: Path to save the plots
    """
    logger.info("Plotting benchmark results")
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Plot insert results
    plt.figure(figsize=(10, 6))
    insert_labels = ['Original Insert', 'Optimized Insert', 'Batch Insert']
    insert_values = [insert_results['original_insert'], insert_results['optimized_insert'], insert_results['batch_insert']]
    
    bars = plt.bar(insert_labels, insert_values, color=['#ff9999', '#66b3ff', '#99ff99'])
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.2f}s',
                 ha='center', va='bottom')
    
    plt.title('Database Insert Performance Comparison')
    plt.ylabel('Time (seconds)')
    plt.tight_layout()
    plt.savefig(output_path / 'insert_benchmark.png')
    
    # Plot query results
    plt.figure(figsize=(12, 6))
    query_pairs = [
        ('original_get_all', 'optimized_get_all', 'Get All Data'),
        ('original_filter', 'optimized_filter', 'Filtered Data'),
        ('original_search', 'optimized_search', 'Search Data')
    ]
    
    x = np.arange(len(query_pairs))
    width = 0.35
    
    original_values = [query_results[pair[0]] for pair in query_pairs]
    optimized_values = [query_results[pair[1]] for pair in query_pairs]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, original_values, width, label='Original', color='#ff9999')
    rects2 = ax.bar(x + width/2, optimized_values, width, label='Optimized', color='#66b3ff')
    
    # Add values on top of bars
    for rect in rects1:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 0.1,
                f'{height:.2f}s',
                ha='center', va='bottom')
    
    for rect in rects2:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 0.1,
                f'{height:.2f}s',
                ha='center', va='bottom')
    
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Database Query Performance Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels([pair[2] for pair in query_pairs])
    ax.legend()
    
    fig.tight_layout()
    plt.savefig(output_path / 'query_benchmark.png')
    
    # Plot speedup
    plt.figure(figsize=(12, 6))
    speedup_labels = [
        'Insert', 
        'Get All Data', 
        'Filtered Data', 
        'Search Data'
    ]
    
    speedup_values = [
        insert_results['original_insert'] / insert_results['optimized_insert'],
        query_results['original_get_all'] / query_results['optimized_get_all'],
        query_results['original_filter'] / query_results['optimized_filter'],
        query_results['original_search'] / query_results['optimized_search']
    ]
    
    bars = plt.bar(speedup_labels, speedup_values, color='#66b3ff')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.2f}x',
                 ha='center', va='bottom')
    
    plt.title('Performance Improvement Factor (Higher is Better)')
    plt.ylabel('Speedup Factor (x times faster)')
    plt.axhline(y=1, color='r', linestyle='--')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path / 'speedup_benchmark.png')
    
    logger.info(f"Plots saved to {output_path}")

def main():
    """Main function to run the benchmark."""
    logger.info("Starting database benchmark")
    
    # Paths for benchmark databases
    benchmark_dir = Path("benchmark")
    benchmark_dir.mkdir(exist_ok=True)
    
    original_db_path = benchmark_dir / "original_benchmark.db"
    optimized_db_path = benchmark_dir / "optimized_benchmark.db"
    
    # Delete existing databases if they exist
    if original_db_path.exists():
        original_db_path.unlink()
    if optimized_db_path.exists():
        optimized_db_path.unlink()
    
    # Generate test data
    test_data = generate_test_data(10000)
    
    # Benchmark insert operations
    insert_results = benchmark_insert(original_db_path, optimized_db_path, test_data)
    
    # Benchmark query operations
    query_results = benchmark_query(original_db_path, optimized_db_path)
    
    # Create output directory for plots
    output_path = Path("benchmark/results")
    
    # Plot results
    plot_results(insert_results, query_results, output_path)
    
    # Print summary
    print("\nBenchmark Results Summary:")
    print("=========================")
    print("\nInsert Operations:")
    print(f"Original Implementation: {insert_results['original_insert']:.2f} seconds")
    print(f"Optimized Implementation: {insert_results['optimized_insert']:.2f} seconds")
    print(f"Batch Insert: {insert_results['batch_insert']:.2f} seconds")
    print(f"Speedup (Original vs. Optimized): {insert_results['original_insert'] / insert_results['optimized_insert']:.2f}x")
    print(f"Speedup (Original vs. Batch): {insert_results['original_insert'] / insert_results['batch_insert']:.2f}x")
    
    print("\nQuery Operations:")
    print(f"Get All Data - Original: {query_results['original_get_all']:.2f} seconds, Optimized: {query_results['optimized_get_all']:.2f} seconds")
    print(f"Speedup: {query_results['original_get_all'] / query_results['optimized_get_all']:.2f}x")
    
    print(f"Filtered Data - Original: {query_results['original_filter']:.2f} seconds, Optimized: {query_results['optimized_filter']:.2f} seconds")
    print(f"Speedup: {query_results['original_filter'] / query_results['optimized_filter']:.2f}x")
    
    print(f"Search Data - Original: {query_results['original_search']:.2f} seconds, Optimized: {query_results['optimized_search']:.2f} seconds")
    print(f"Speedup: {query_results['original_search'] / query_results['optimized_search']:.2f}x")
    
    print(f"\nAggregated Data (Optimized only): {query_results['optimized_aggregate']:.2f} seconds")
    
    print("\nResults have been plotted and saved to the benchmark/results directory.")
    
if __name__ == "__main__":
    main()