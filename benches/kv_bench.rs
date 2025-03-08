use criterion::{criterion_group, criterion_main, Criterion};
use tokio::runtime::Runtime;
use volt::KVCluster; // Use the KVCluster from the lib.rs

fn bench_operations(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut group = c.benchmark_group("KVStore");
    
    group.bench_function("setup", |b| {
        b.iter(|| {
            let mut cluster = KVCluster::new(100, 2);
            rt.block_on(async {
                cluster.add_node("node1".to_string());
                cluster.add_node("node2".to_string());
            });
            cluster
        })
    });

    let mut cluster = KVCluster::new(100, 2);
    rt.block_on(async {
        cluster.add_node("node1".to_string());
        cluster.add_node("node2".to_string());
    });

    group.bench_function("set", |b| {
        b.iter(|| {
            rt.block_on(async {
                cluster.set("key".to_string(), b"value".to_vec(), None).await
            })
        })
    });

    group.bench_function("get", |b| {
        b.iter(|| cluster.get("key"))
    });

    group.bench_function("del", |b| {
        b.iter(|| {
            rt.block_on(async {
                cluster.del("key").await
            })
        })
    });

    group.finish();
}

criterion_group!(benches, bench_operations);
criterion_main!(benches);