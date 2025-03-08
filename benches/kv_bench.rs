use criterion::{criterion_group, criterion_main};

mod scenarios {
    pub mod data_size;
    pub mod concurrent_ops;
    pub mod bulk_ops;
}

use scenarios::data_size::bench_data_size;
use scenarios::concurrent_ops::bench_concurrent_ops;
use scenarios::bulk_ops::bench_bulk_ops;

criterion_group!(
    benches,
    bench_data_size,
    bench_concurrent_ops,
    bench_bulk_ops
);
criterion_main!(benches);