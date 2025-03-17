use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post, delete},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::Duration;
use tower_http::cors::{Any, CorsLayer};
use tracing::info;

use crate::KVCluster;

// Request and response types
#[derive(Deserialize)]
pub struct SetRequest {
    value: String,
    ttl_seconds: Option<u64>,
}

#[derive(Deserialize)]
pub struct SetJsonRequest {
    value: serde_json::Value,
    ttl_seconds: Option<u64>,
}

#[derive(Serialize)]
pub struct GetResponse {
    value: String,
}

#[derive(Serialize)]
pub struct GetJsonResponse {
    value: serde_json::Value,
}

#[derive(Serialize)]
pub struct ApiResponse {
    success: bool,
    message: String,
}

// API handlers
pub async fn create_api_router(cluster: Arc<KVCluster>) -> Router {
    // Configure CORS
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .route("/health", get(health_check))
        .route("/kv/:key", get(get_value))
        .route("/kv/:key", post(set_value))
        .route("/kv/:key", delete(delete_value))
        .route("/json/:key", get(get_json_value))
        .route("/json/:key", post(set_json_value))
        .layer(cors)
        .with_state(cluster)
}

// Health check endpoint
async fn health_check() -> impl IntoResponse {
    StatusCode::OK
}

// Get a value
async fn get_value(
    State(cluster): State<Arc<KVCluster>>,
    Path(key): Path<String>,
) -> impl IntoResponse {
    if let Some(value) = cluster.get(&key) {
        let value_str = String::from_utf8_lossy(&value).to_string();
        (StatusCode::OK, Json(GetResponse { value: value_str })).into_response()
    } else {
        (
            StatusCode::NOT_FOUND,
            Json(ApiResponse {
                success: false,
                message: format!("Key '{}' not found", key),
            }),
        ).into_response()
    }
}

// Set a value
async fn set_value(
    State(cluster): State<Arc<KVCluster>>,
    Path(key): Path<String>,
    Json(payload): Json<SetRequest>,
) -> impl IntoResponse {
    let ttl = payload.ttl_seconds.map(|secs| Duration::from_secs(secs));
    
    cluster
        .set(key.clone(), payload.value.as_bytes().to_vec(), ttl)
        .await;
    
    (
        StatusCode::OK,
        Json(ApiResponse {
            success: true,
            message: format!("Key '{}' set successfully", key),
        }),
    )
}

// Delete a value
async fn delete_value(
    State(cluster): State<Arc<KVCluster>>,
    Path(key): Path<String>,
) -> impl IntoResponse {
    cluster.del(&key).await;
    
    (
        StatusCode::OK,
        Json(ApiResponse {
            success: true,
            message: format!("Key '{}' deleted successfully", key),
        }),
    )
}

// Get a JSON value
async fn get_json_value(
    State(cluster): State<Arc<KVCluster>>,
    Path(key): Path<String>,
) -> impl IntoResponse {
    match cluster.get_json_value(&key) {
        Ok(Some(value)) => {
            (StatusCode::OK, Json(GetJsonResponse { value })).into_response()
        },
        Ok(None) => {
            (
                StatusCode::NOT_FOUND,
                Json(ApiResponse {
                    success: false,
                    message: format!("Key '{}' not found", key),
                }),
            ).into_response()
        },
        Err(e) => {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse {
                    success: false,
                    message: format!("Error retrieving JSON: {}", e),
                }),
            ).into_response()
        }
    }
}

// Set a JSON value
async fn set_json_value(
    State(cluster): State<Arc<KVCluster>>,
    Path(key): Path<String>,
    Json(payload): Json<SetJsonRequest>,
) -> impl IntoResponse {
    let ttl = payload.ttl_seconds.map(|secs| Duration::from_secs(secs));
    
    match cluster.set_json_value(key.clone(), &payload.value, ttl).await {
        Ok(_) => (
            StatusCode::OK,
            Json(ApiResponse {
                success: true,
                message: format!("JSON key '{}' set successfully", key),
            }),
        ),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiResponse {
                success: false,
                message: format!("Error setting JSON: {}", e),
            }),
        ),
    }
} 