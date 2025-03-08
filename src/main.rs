use volt::KVCluster;
use std::time::{Duration, Instant};
use std::sync::Arc;
use tokio::task;

const NUM_OPERATIONS: usize = 1000;
const NUM_NODES: usize = 5;
const VALUE_SIZES: [usize; 3] = [100, 1000, 10000]; // bytes
const CONCURRENT_CLIENTS: usize = 10;

#[derive(Clone, Copy)]
enum Operation {
    Set,
    Get,
    Del,
}

fn calculate_stats(times: &[u128]) -> (u128, u128, u128, f64) {
    let sum: u128 = times.iter().sum();
    let avg = sum / times.len() as u128;
    let min = *times.iter().min().unwrap_or(&0);
    let max = *times.iter().max().unwrap_or(&0);
    
    // Calculate standard deviation
    let mean = avg as f64;
    let variance: f64 = times.iter()
        .map(|&x| {
            let diff = x as f64 - mean;
            diff * diff
        })
        .sum::<f64>() / times.len() as f64;
    let std_dev = variance.sqrt();
    
    (min, avg, max, std_dev)
}

async fn run_concurrent_operations(
    cluster: Arc<KVCluster>,
    operation: Operation,
    start_idx: usize,
    num_ops: usize,
    test_value: Vec<u8>,
) -> Vec<u128> {
    let mut handles = Vec::with_capacity(num_ops);
    
    for i in start_idx..start_idx + num_ops {
        let cluster = cluster.clone();
        let key = format!("key{}", i);
        let value = test_value.clone();
        
        let handle = task::spawn(async move {
            let start = Instant::now();
            match operation {
                Operation::Set => {
                    cluster.set(key, value, None).await;
                }
                Operation::Get => {
                    let _ = cluster.get(&key);
                }
                Operation::Del => {
                    cluster.del(&key).await;
                }
            }
            start.elapsed().as_nanos()
        });
        
        handles.push(handle);
    }

    let mut times = Vec::with_capacity(num_ops);
    for handle in handles {
        times.push(handle.await.unwrap());
    }
    times
}

#[tokio::main]
async fn main() {
    println!("\n=== Concurrent Performance Test (Nanoseconds) ===");
    println!("Total operations per test: {}", NUM_OPERATIONS);
    println!("Concurrent clients: {}", CONCURRENT_CLIENTS);
    println!("Operations per client: {}", NUM_OPERATIONS / CONCURRENT_CLIENTS);
    println!("Number of nodes: {}", NUM_NODES);
    println!("Value sizes: {:?} bytes\n", VALUE_SIZES);

    let mut cluster = KVCluster::new(100, 3); // 100 vnodes per node, replication factor 3
    
    // Add nodes
    println!("1. Adding {} nodes to cluster...", NUM_NODES);
    let start = Instant::now();
    for i in 0..NUM_NODES {
        cluster.add_node(format!("node{}", i));
    }
    let setup_time = start.elapsed().as_nanos();
    println!("Cluster setup time: {} nanoseconds\n", setup_time);

    // Convert cluster to Arc for thread sharing
    let cluster = Arc::new(cluster);

    // Tests for different value sizes
    for &size in VALUE_SIZES.iter() {
        println!("=== Concurrent tests with {} byte values ===", size);
        let test_value = vec![b'x'; size]; // Create a vector with 'size' bytes
        
        let ops_per_client = NUM_OPERATIONS / CONCURRENT_CLIENTS;
        let mut all_set_times = Vec::new();
        let mut all_get_times = Vec::new();
        let mut all_del_times = Vec::new();

        // Concurrent SET operations
        println!("Executing {} concurrent SET operations...", NUM_OPERATIONS);
        for c in 0..CONCURRENT_CLIENTS {
            let times = run_concurrent_operations(
                cluster.clone(),
                Operation::Set,
                c * ops_per_client,
                ops_per_client,
                test_value.clone(),
            ).await;
            all_set_times.extend(times);
        }

        // Concurrent GET operations
        println!("Executing {} concurrent GET operations...", NUM_OPERATIONS);
        for c in 0..CONCURRENT_CLIENTS {
            let times = run_concurrent_operations(
                cluster.clone(),
                Operation::Get,
                c * ops_per_client,
                ops_per_client,
                test_value.clone(),
            ).await;
            all_get_times.extend(times);
        }

        // Concurrent DELETE operations
        println!("Executing {} concurrent DELETE operations...", NUM_OPERATIONS);
        for c in 0..CONCURRENT_CLIENTS {
            let times = run_concurrent_operations(
                cluster.clone(),
                Operation::Del,
                c * ops_per_client,
                ops_per_client,
                test_value.clone(),
            ).await;
            all_del_times.extend(times);
        }

        // Calculate and display statistics
        let (min_set, avg_set, max_set, std_set) = calculate_stats(&all_set_times);
        let (min_get, avg_get, max_get, std_get) = calculate_stats(&all_get_times);
        let (min_del, avg_del, max_del, std_del) = calculate_stats(&all_del_times);

        println!("\nStatistics with {} concurrent clients (nanoseconds):", CONCURRENT_CLIENTS);
        println!("SET  - Min: {}, Average: {}, Max: {}, Std.Dev: {:.2}", min_set, avg_set, max_set, std_set);
        println!("GET  - Min: {}, Average: {}, Max: {}, Std.Dev: {:.2}", min_get, avg_get, max_get, std_get);
        println!("DEL  - Min: {}, Average: {}, Max: {}, Std.Dev: {:.2}", min_del, avg_del, max_del, std_del);
        println!("----------------------------------------\n");
    }
}