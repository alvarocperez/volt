use criterion::{Criterion, BenchmarkId};
use tokio::runtime::Runtime;
use volt::KVCluster;
use std::sync::Arc;
use tokio::task;

const CONCURRENT_OPS: &[usize] = &[1, 10, 100, 1_000];

pub fn bench_concurrent_ops(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut group = c.benchmark_group("Concurrent Operations");
    
    for &num_ops in CONCURRENT_OPS {
        let mut cluster = KVCluster::new(100, 2);
        rt.block_on(async {
            cluster.add_node("node1".to_string());
        });
        let cluster = Arc::new(cluster);

        // Concurrent SET operations
        group.bench_with_input(BenchmarkId::new("concurrent_set", num_ops), &num_ops, |b, &n| {
            b.iter(|| {
                rt.block_on(async {
                    let cluster = Arc::clone(&cluster);
                    let mut handles = Vec::with_capacity(n);
                    
                    for i in 0..n {
                        let cluster = Arc::clone(&cluster);
                        handles.push(task::spawn(async move {
                            cluster.set(
                                format!("concurrent_key_{}", i),
                                format!("value_{}", i).into_bytes(),
                                None
                            ).await
                        }));
                    }

                    for handle in handles {
                        handle.await.unwrap();
                    }
                })
            })
        });

        // Pre-set keys for concurrent GET operations
        rt.block_on(async {
            for i in 0..num_ops {
                cluster.set(
                    format!("concurrent_key_{}", i),
                    format!("value_{}", i).into_bytes(),
                    None
                ).await;
            }
        });

        // Concurrent GET operations
        group.bench_with_input(BenchmarkId::new("concurrent_get", num_ops), &num_ops, |b, &n| {
            b.iter(|| {
                rt.block_on(async {
                    let cluster = Arc::clone(&cluster);
                    let mut handles = Vec::with_capacity(n);
                    
                    for i in 0..n {
                        let cluster = Arc::clone(&cluster);
                        handles.push(task::spawn(async move {
                            cluster.get(&format!("concurrent_key_{}", i))
                        }));
                    }

                    for handle in handles {
                        handle.await.unwrap();
                    }
                })
            })
        });

        // Mixed concurrent operations (50% GET, 50% SET)
        group.bench_with_input(BenchmarkId::new("concurrent_mixed", num_ops), &num_ops, |b, &n| {
            b.iter(|| {
                rt.block_on(async {
                    let cluster = Arc::clone(&cluster);
                    let mut handles = Vec::with_capacity(n);
                    
                    for i in 0..n {
                        let cluster = Arc::clone(&cluster);
                        handles.push(task::spawn(async move {
                            if i % 2 == 0 {
                                cluster.set(
                                    format!("mixed_key_{}", i),
                                    format!("value_{}", i).into_bytes(),
                                    None
                                ).await;
                                None
                            } else {
                                cluster.get(&format!("mixed_key_{}", i - 1))
                            }
                        }));
                    }

                    for handle in handles {
                        handle.await.unwrap();
                    }
                })
            })
        });
    }
    
    group.finish();
} 