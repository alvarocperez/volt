use dashmap::DashMap;
use priority_queue::PriorityQueue;
use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tokio::sync::mpsc;
use xxhash_rust::xxh32::xxh32;

#[derive(Clone)]
struct KVEntry {
    value: Vec<u8>,
    expiry: Option<Instant>,
}

enum KVOperation {
    Set(String, Vec<u8>, Option<Duration>),
    Del(String),
}

struct KVNode {
    id: String,
    store: DashMap<String, KVEntry>,
    ttl_queue: Mutex<PriorityQueue<String, Instant>>,
    tx: mpsc::Sender<KVOperation>,
}

#[derive(Clone)]
pub struct KVCluster {
    nodes: Vec<Arc<KVNode>>,
    ring: Arc<BTreeMap<u32, usize>>,
    vnodes_per_node: usize,
    replication_factor: usize,
}

impl KVCluster {
    pub fn new(vnodes_per_node: usize, replication_factor: usize) -> Self {
        KVCluster {
            nodes: Vec::new(),
            ring: Arc::new(BTreeMap::new()),
            vnodes_per_node,
            replication_factor,
        }
    }

    pub fn add_node(&mut self, node_id: String) {
        let (tx, mut rx) = mpsc::channel::<KVOperation>(1000);
        let node = Arc::new(KVNode {
            id: node_id.clone(),
            store: DashMap::new(),
            ttl_queue: Mutex::new(PriorityQueue::new()),
            tx,
        });
        let node_idx = self.nodes.len();
        self.nodes.push(node.clone());

        let node_for_ops = node.clone();
        tokio::spawn(async move {
            while let Some(op) = rx.recv().await {
                match op {
                    KVOperation::Set(key, value, ttl) => {
                        let expiry = ttl.map(|d| Instant::now() + d);
                        node_for_ops.store.insert(key.clone(), KVEntry { value, expiry });
                        if let Some(exp) = expiry {
                            node_for_ops.ttl_queue.lock().unwrap().push(key, exp);
                        }
                    }
                    KVOperation::Del(key) => {
                        node_for_ops.store.remove(&key);
                        node_for_ops.ttl_queue.lock().unwrap().remove(&key);
                    }
                }
            }
        });

        let ring = Arc::get_mut(&mut self.ring).unwrap();
        for i in 0..self.vnodes_per_node {
            let vhash = xxh32(format!("{}:{}", node_id, i).as_bytes(), 0);
            ring.insert(vhash, node_idx);
        }

        let ttl_node = node.clone();
        tokio::spawn(async move {
            loop {
                tokio::time::sleep(Duration::from_millis(1)).await;
                let mut queue = ttl_node.ttl_queue.lock().unwrap();
                while let Some((key, expiry)) = queue.peek() {
                    if *expiry > Instant::now() {
                        break;
                    }
                    ttl_node.store.remove(key);
                    queue.pop();
                }
            }
        });
    }

    fn get_nodes(&self, key: &str) -> Vec<Arc<KVNode>> {
        let khash = xxh32(key.as_bytes(), 0);
        let mut nodes = Vec::with_capacity(self.replication_factor);
        let mut iter = self.ring.range(khash..).chain(self.ring.iter());
        for _ in 0..self.replication_factor {
            if let Some((_, idx)) = iter.next() {
                nodes.push(self.nodes[*idx].clone());
            }
        }
        nodes
    }

    pub async fn set(&self, key: String, value: Vec<u8>, ttl: Option<Duration>) {
        let nodes = self.get_nodes(&key);
        let primary = &nodes[0];
        let expiry = ttl.map(|d| Instant::now() + d);
        primary.store.insert(key.clone(), KVEntry { value: value.clone(), expiry });
        if let Some(exp) = expiry {
            primary.ttl_queue.lock().unwrap().push(key.clone(), exp);
        }
        for replica in &nodes[1..] {
            let _ = replica.tx.send(KVOperation::Set(key.clone(), value.clone(), ttl)).await;
        }
    }

    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        let nodes = self.get_nodes(key);
        let primary = &nodes[0];
        primary.store.get(key).and_then(|entry| {
            if let Some(expiry) = entry.expiry {
                if expiry <= Instant::now() {
                    primary.store.remove(key);
                    primary.ttl_queue.lock().unwrap().remove(key);
                    return None;
                }
            }
            Some(entry.value.clone())
        })
    }

    pub async fn del(&self, key: &str) {
        let nodes = self.get_nodes(key);
        let primary = &nodes[0];
        primary.store.remove(key);
        primary.ttl_queue.lock().unwrap().remove(key);
        for replica in &nodes[1..] {
            let _ = replica.tx.send(KVOperation::Del(key.to_string())).await;
        }
    }
}