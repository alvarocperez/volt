use std::net::SocketAddr;
use volt::KVCluster;
use volt::server::run_server;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a new KV cluster
    let mut cluster = KVCluster::new(100, 3);
    
    // Add nodes to the cluster
    let node_count = std::env::var("VOLT_NODE_COUNT")
        .unwrap_or_else(|_| "3".to_string())
        .parse::<usize>()
        .unwrap_or(3);
    
    for i in 0..node_count {
        cluster.add_node(format!("node{}", i));
    }
    
    // Get the server address from environment or use default
    let host = std::env::var("VOLT_HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let port = std::env::var("VOLT_PORT")
        .unwrap_or_else(|_| "3000".to_string())
        .parse::<u16>()
        .unwrap_or(3000);
    
    let addr = format!("{}:{}", host, port).parse::<SocketAddr>()?;
    
    // Run the server
    run_server(cluster, addr).await
} 