use volt::KVCluster;
use std::time::{Duration, Instant};
use std::sync::Arc;
use tokio::task;
use serde::{Serialize, Deserialize};
use serde_json::json;

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

// Definición de una estructura para demostrar la serialización/deserialización
#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct User {
    id: u64,
    name: String,
    email: String,
    active: bool,
    metadata: UserMetadata,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct UserMetadata {
    created_at: String,
    last_login: Option<String>,
    preferences: UserPreferences,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct UserPreferences {
    theme: String,
    notifications_enabled: bool,
    language: String,
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

// Función para demostrar el uso de JSON con estructuras definidas
async fn demo_json_struct(cluster: &KVCluster) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Demostración de JSON con estructuras definidas ===");
    
    // Crear un usuario de ejemplo
    let user = User {
        id: 12345,
        name: "Ana García".to_string(),
        email: "ana.garcia@example.com".to_string(),
        active: true,
        metadata: UserMetadata {
            created_at: "2023-01-15T08:30:00Z".to_string(),
            last_login: Some("2023-03-20T14:25:30Z".to_string()),
            preferences: UserPreferences {
                theme: "dark".to_string(),
                notifications_enabled: true,
                language: "es".to_string(),
            },
        },
    };
    
    // Almacenar el usuario
    let key = "user:12345".to_string();
    let start = Instant::now();
    cluster.set_json(key.clone(), &user, Some(Duration::from_secs(3600))).await?;
    let set_time = start.elapsed().as_nanos();
    
    // Recuperar el usuario
    let start = Instant::now();
    let retrieved_user: Option<User> = cluster.get_json(&key)?;
    let get_time = start.elapsed().as_nanos();
    
    // Verificar que los datos son correctos
    match retrieved_user {
        Some(u) => {
            println!("Usuario recuperado correctamente: {}", u.name);
            println!("Email: {}", u.email);
            println!("Preferencias: {} / {}", u.metadata.preferences.theme, u.metadata.preferences.language);
            assert_eq!(u, user, "El usuario recuperado debe ser igual al original");
        },
        None => println!("Error: No se pudo recuperar el usuario"),
    }
    
    println!("Tiempo de SET_JSON: {} ns", set_time);
    println!("Tiempo de GET_JSON: {} ns", get_time);
    
    Ok(())
}

// Función para demostrar el uso de JSON genérico
async fn demo_json_generic(cluster: &KVCluster) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Demostración de JSON genérico ===");
    
    // Crear un documento JSON complejo
    let document = json!({
        "id": "doc-123",
        "type": "article",
        "title": "Introducción a las bases de datos clave-valor",
        "author": {
            "name": "Carlos Rodríguez",
            "email": "carlos@example.com"
        },
        "tags": ["database", "nosql", "performance"],
        "content": {
            "summary": "Una visión general de las bases de datos clave-valor y sus casos de uso",
            "sections": [
                {
                    "title": "¿Qué es una base de datos clave-valor?",
                    "paragraphs": 3
                },
                {
                    "title": "Ventajas y desventajas",
                    "paragraphs": 5
                }
            ],
            "published": true,
            "word_count": 2500,
            "read_time": 12
        },
        "metadata": {
            "created_at": "2023-02-10T10:15:00Z",
            "updated_at": "2023-03-05T16:20:00Z",
            "views": 1250,
            "likes": 42
        }
    });
    
    // Almacenar el documento
    let key = "article:doc-123".to_string();
    let start = Instant::now();
    cluster.set_json_value(key.clone(), &document, Some(Duration::from_secs(3600))).await?;
    let set_time = start.elapsed().as_nanos();
    
    // Recuperar el documento
    let start = Instant::now();
    let retrieved_doc = cluster.get_json_value(&key)?;
    let get_time = start.elapsed().as_nanos();
    
    // Verificar y mostrar partes del documento
    match retrieved_doc {
        Some(doc) => {
            println!("Documento recuperado: {}", doc["title"]);
            println!("Autor: {}", doc["author"]["name"]);
            println!("Etiquetas: {:?}", doc["tags"].as_array().unwrap());
            println!("Vistas: {}", doc["metadata"]["views"]);
            
            // Acceder a elementos anidados
            if let Some(sections) = doc["content"]["sections"].as_array() {
                println!("Secciones:");
                for (i, section) in sections.iter().enumerate() {
                    println!("  {}. {} ({} párrafos)", 
                        i+1, 
                        section["title"].as_str().unwrap_or("Sin título"),
                        section["paragraphs"].as_u64().unwrap_or(0)
                    );
                }
            }
        },
        None => println!("Error: No se pudo recuperar el documento"),
    }
    
    println!("Tiempo de SET_JSON_VALUE: {} ns", set_time);
    println!("Tiempo de GET_JSON_VALUE: {} ns", get_time);
    
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Configuración del cluster
    let mut cluster = KVCluster::new(100, 3); // 100 vnodes per node, replication factor 3
    cluster.add_node("node1".to_string());
    
    // Ejecutar demostraciones de JSON
    demo_json_struct(&cluster).await?;
    demo_json_generic(&cluster).await?;
    
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
    
    Ok(())
}