use criterion::{Criterion, BenchmarkId};
use tokio::runtime::Runtime;
use volt::KVCluster;
use serde::{Serialize, Deserialize};
use serde_json::json;
use std::time::Duration;

// Tamaños aproximados de documentos JSON para pruebas
const JSON_SIZES: &[usize] = &[
    1,      // JSON muy pequeño (pocos campos)
    10,     // JSON pequeño
    100,    // JSON mediano
    1000,   // JSON grande
    10000,  // JSON muy grande
];

// Estructura simple para pruebas
#[derive(Debug, Serialize, Deserialize)]
struct SimpleDocument {
    id: String,
    value: i32,
    active: bool,
}

// Estructura anidada para pruebas
#[derive(Debug, Serialize, Deserialize)]
struct ComplexDocument {
    id: String,
    name: String,
    tags: Vec<String>,
    metadata: Metadata,
    items: Vec<Item>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Metadata {
    created_at: String,
    updated_at: Option<String>,
    version: i32,
}

#[derive(Debug, Serialize, Deserialize)]
struct Item {
    id: i32,
    name: String,
    value: f64,
    properties: Vec<String>,
}

// Genera un documento JSON simple
fn generate_simple_document(size_factor: usize) -> SimpleDocument {
    SimpleDocument {
        id: format!("doc-{}", size_factor),
        value: size_factor as i32,
        active: size_factor % 2 == 0,
    }
}

// Genera un documento JSON complejo con tamaño variable
fn generate_complex_document(size_factor: usize) -> ComplexDocument {
    // Ajustar el número de elementos según el factor de tamaño
    let num_tags = size_factor.min(100);
    let num_items = (size_factor / 10).max(1).min(1000);
    let num_properties = (size_factor / 20).max(1).min(500);
    
    // Generar tags
    let tags = (0..num_tags)
        .map(|i| format!("tag-{}", i))
        .collect();
    
    // Generar items
    let items = (0..num_items)
        .map(|i| {
            let properties = (0..num_properties)
                .map(|j| format!("property-{}-{}", i, j))
                .collect();
            
            Item {
                id: i as i32,
                name: format!("Item {}", i),
                value: (i * 10) as f64 / 3.0,
                properties,
            }
        })
        .collect();
    
    ComplexDocument {
        id: format!("complex-{}", size_factor),
        name: format!("Document with size factor {}", size_factor),
        tags,
        metadata: Metadata {
            created_at: "2023-03-08T12:00:00Z".to_string(),
            updated_at: Some("2023-03-08T14:30:00Z".to_string()),
            version: 1,
        },
        items,
    }
}

// Genera un documento JSON genérico con tamaño variable
fn generate_generic_json(size_factor: usize) -> serde_json::Value {
    // Ajustar el número de elementos según el factor de tamaño
    let num_fields = size_factor.min(1000);
    
    // Crear un objeto base
    let mut obj = json!({
        "id": format!("generic-{}", size_factor),
        "timestamp": "2023-03-08T12:00:00Z",
        "type": "benchmark"
    });
    
    // Añadir campos dinámicamente
    if let Some(obj_map) = obj.as_object_mut() {
        for i in 0..num_fields {
            obj_map.insert(
                format!("field_{}", i), 
                json!({
                    "name": format!("Field {}", i),
                    "value": i,
                    "active": i % 2 == 0,
                    "tags": [format!("tag-{}-1", i), format!("tag-{}-2", i)]
                })
            );
        }
    }
    
    obj
}

pub fn bench_json_ops(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    let mut group = c.benchmark_group("JSON Operations");
    
    for &size in JSON_SIZES {
        // Crear un cluster para cada tamaño
        let mut cluster = KVCluster::new(100, 2);
        rt.block_on(async {
            cluster.add_node("node1".to_string());
        });
        
        // Benchmark para documentos simples
        let simple_doc = generate_simple_document(size);
        group.bench_with_input(BenchmarkId::new("simple_set", size), &size, |b, _| {
            b.iter(|| {
                rt.block_on(async {
                    let _ = cluster.set_json(
                        format!("simple:{}", size), 
                        &simple_doc, 
                        Some(Duration::from_secs(60))
                    ).await;
                })
            })
        });
        
        // Pre-almacenar para get
        rt.block_on(async {
            let _ = cluster.set_json(
                format!("simple:{}", size), 
                &simple_doc, 
                Some(Duration::from_secs(60))
            ).await;
        });
        
        group.bench_with_input(BenchmarkId::new("simple_get", size), &size, |b, _| {
            b.iter(|| {
                let _: Result<Option<SimpleDocument>, _> = rt.block_on(async {
                    cluster.get_json(&format!("simple:{}", size))
                });
            })
        });
        
        // Benchmark para documentos complejos
        let complex_doc = generate_complex_document(size);
        group.bench_with_input(BenchmarkId::new("complex_set", size), &size, |b, _| {
            b.iter(|| {
                rt.block_on(async {
                    let _ = cluster.set_json(
                        format!("complex:{}", size), 
                        &complex_doc, 
                        Some(Duration::from_secs(60))
                    ).await;
                })
            })
        });
        
        // Pre-almacenar para get
        rt.block_on(async {
            let _ = cluster.set_json(
                format!("complex:{}", size), 
                &complex_doc, 
                Some(Duration::from_secs(60))
            ).await;
        });
        
        group.bench_with_input(BenchmarkId::new("complex_get", size), &size, |b, _| {
            b.iter(|| {
                let _: Result<Option<ComplexDocument>, _> = rt.block_on(async {
                    cluster.get_json(&format!("complex:{}", size))
                });
            })
        });
        
        // Benchmark para JSON genérico
        let generic_doc = generate_generic_json(size);
        group.bench_with_input(BenchmarkId::new("generic_set", size), &size, |b, _| {
            b.iter(|| {
                rt.block_on(async {
                    let _ = cluster.set_json_value(
                        format!("generic:{}", size), 
                        &generic_doc, 
                        Some(Duration::from_secs(60))
                    ).await;
                })
            })
        });
        
        // Pre-almacenar para get
        rt.block_on(async {
            let _ = cluster.set_json_value(
                format!("generic:{}", size), 
                &generic_doc, 
                Some(Duration::from_secs(60))
            ).await;
        });
        
        group.bench_with_input(BenchmarkId::new("generic_get", size), &size, |b, _| {
            b.iter(|| {
                let _: Result<Option<serde_json::Value>, _> = rt.block_on(async {
                    cluster.get_json_value(&format!("generic:{}", size))
                });
            })
        });
    }
    
    group.finish();
} 