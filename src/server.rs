use std::net::SocketAddr;
use std::sync::Arc;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

use crate::KVCluster;
use crate::api::create_api_router;

pub async fn run_server(cluster: KVCluster, addr: SocketAddr) -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("Failed to set tracing subscriber");

    // Create shared state
    let shared_cluster = Arc::new(cluster);
    
    // Build the API router
    let app = create_api_router(shared_cluster).await;
    
    // Start the server
    info!("Starting Volt server on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    
    Ok(())
} 