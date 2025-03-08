use criterion::{Criterion, BenchmarkId};
use tokio::runtime::Runtime;
use volt::KVCluster;

const SIZES: &[usize] = &[10, 100, 1_000, 10_000, 100_000];

fn generate_data(size: usize) -> Vec<u8> {
    (0..size).map(|i| (i % 256) as u8).collect()
}

pub fn bench_bulk_ops(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut group = c.benchmark_group("Bulk Operations");
    
    for size in SIZES {
        let data = generate_data(100); // Fixed data size for bulk ops
        let mut cluster = KVCluster::new(100, 2);
        rt.block_on(async {
            cluster.add_node("node1".to_string());
        });

        // Sequential bulk SET
        group.bench_with_input(BenchmarkId::new("bulk_sequential_set", size), size, |b, &n| {
            b.iter(|| {
                rt.block_on(async {
                    for i in 0..n {
                        cluster.set(
                            format!("bulk_key_{}", i),
                            data.clone(),
                            None
                        ).await;
                    }
                })
            })
        });

        // Pre-set keys for bulk GET
        rt.block_on(async {
            for i in 0..*size {
                cluster.set(format!("bulk_key_{}", i), data.clone(), None).await;
            }
        });

        // Sequential bulk GET
        group.bench_with_input(BenchmarkId::new("bulk_sequential_get", size), size, |b, &n| {
            b.iter(|| {
                for i in 0..n {
                    cluster.get(&format!("bulk_key_{}", i));
                }
            })
        });
    }
    
    group.finish();
} 