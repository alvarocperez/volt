# Volt Python Client

A Python client for the Volt key-value database.

## Installation

```bash
# Install from the local directory
pip install .

# Or install directly from GitHub (once published)
# pip install git+https://github.com/yourusername/volt.git#subdirectory=python
```

## Usage

```python
from volt_client import VoltClient

# Connect to a Volt server
client = VoltClient(host="localhost", port=3000)

# Check if the server is running
if client.health():
    print("Volt server is running!")

# Basic string operations
client.set("hello", "world")
print(client.get("hello"))  # Outputs: world

# With TTL (time-to-live)
client.set("temporary", "This will expire", ttl_seconds=60)

# JSON operations
user = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "active": True,
    "preferences": {
        "theme": "dark",
        "notifications": True
    }
}

client.set_json("user:1", user)
retrieved_user = client.get_json("user:1")
print(f"User: {retrieved_user['name']} ({retrieved_user['email']})")

# Delete operations
client.delete("hello")
```

## API Reference

### `VoltClient(host="localhost", port=3000)`

Creates a new client instance.

### Methods

- `health() -> bool`: Check if the Volt server is running
- `get(key: str) -> Optional[str]`: Get a string value
- `set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool`: Set a string value
- `delete(key: str) -> bool`: Delete a key
- `get_json(key: str) -> Optional[Dict[str, Any]]`: Get a JSON value
- `set_json(key: str, value: Union[Dict[str, Any], list], ttl_seconds: Optional[int] = None) -> bool`: Set a JSON value

## Running with Docker

If you're using the Volt server with Docker, you can connect to it like this:

```python
client = VoltClient(host="localhost", port=3000)
```

If you're running the client from another Docker container in the same network, use the service name:

```python
client = VoltClient(host="volt", port=3000)
``` 