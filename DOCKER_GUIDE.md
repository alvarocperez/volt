# Guide to using Volt with Docker and Python

This guide explains how to run the Volt database in Docker and use it from Python.

## Requirements

- Docker and Docker Compose
- Python 3.7 or higher
- pip (Python package manager)

## Step 1: Run Volt in Docker

1. Clone the repository:

```bash
git clone https://github.com/alvarocperez/volt.git
cd volt
```

2. Build and run the Docker container:

```bash
docker-compose up -d
```

3. Verify that the server is running:

```bash
curl http://localhost:3000/health
```

## Step 2: Install the Python client

1. Install the Python client:

```bash
cd python
pip install .
```

2. Or install directly from the directory:

```bash
pip install -e ./python
```

## Step 3: Use Volt from Python

Now you can use Volt from any Python script:

```python
from volt_client import VoltClient

# Connect to the Volt server
client = VoltClient(host="localhost", port=3000)

# Verify that the server is running
if client.health():
    print("The Volt server is working!")
else:
    print("Cannot connect to the Volt server")
    exit(1)

# Basic operations
client.set("greeting", "Hello World!")
print(f"Retrieved value: {client.get('greeting')}")

# JSON operations
data = {
    "id": 123,
    "name": "John Smith",
    "email": "john@example.com",
    "active": True,
    "preferences": {
        "theme": "dark",
        "notifications": True,
        "language": "en"
    }
}

# Store JSON data
client.set_json("user:123", data)

# Retrieve JSON data
user = client.get_json("user:123")
print(f"User: {user['name']} ({user['email']})")
print(f"Preferences: {user['preferences']}")

# Delete data
client.delete("greeting")
```

## Step 4: Running in a production environment

For a production environment, consider:

1. Configure the number of nodes:

```bash
VOLT_NODE_COUNT=5 docker-compose up -d
```

2. Configure the port:

```bash
VOLT_PORT=8080 docker-compose up -d
```

3. Use a volume for persistence (upcoming version)

## Troubleshooting

1. **Cannot connect to the server**
   - Verify that the container is running: `docker ps`
   - Check the logs: `docker-compose logs volt`

2. **The server is slow**
   - Increase the number of nodes: `VOLT_NODE_COUNT=5 docker-compose up -d`

3. **Connection errors from another container**
   - Use the service name as the host: `client = VoltClient(host="volt", port=3000)`

## Current limitations

- No data persistence (data is lost when the container restarts)
- No authentication
- No SSL/TLS encryption
- No replication between separate instances

These features are planned for future versions. 