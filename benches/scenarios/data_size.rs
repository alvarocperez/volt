use criterion::{Criterion, BenchmarkId};
use tokio::runtime::Runtime;
use volt::KVCluster;

const SIZES: &[usize] = &[10, 100, 1_000, 10_000, 100_000];

fn generate_data(size: usize) -> Vec<u8> {
    (0..size).map(|i| (i % 256) as u8).collect()
}

pub fn bench_data_size(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut group = c.benchmark_group("Data Size Impact");
    
    for size in SIZES {
        let data = generate_data(*size);
        let mut cluster = KVCluster::new(100, 2);
        rt.block_on(async {
            cluster.add_node("node1".to_string());
        });

        group.bench_with_input(BenchmarkId::new("set", size), size, |b, &size| {
            b.iter(|| {
                rt.block_on(async {
                    cluster.set(format!("key_{}", size), data.clone(), None).await
                })
            })
        });

        // Pre-set the key for get operations
        rt.block_on(async {
            cluster.set(format!("key_{}", size), data.clone(), None).await
        });

        group.bench_with_input(BenchmarkId::new("get", size), size, |b, &size| {
            b.iter(|| cluster.get(&format!("key_{}", size)))
        });
    }
    
    group.finish();
} 