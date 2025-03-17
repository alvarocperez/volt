import requests
import json
from typing import Any, Dict, Optional, Union


class VoltClient:
    """
    Python client for the Volt key-value database.
    """
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        """
        Initialize the Volt client.
        
        Args:
            host: The hostname of the Volt server
            port: The port of the Volt server
        """
        self.base_url = f"http://{host}:{port}"
    
    def health(self) -> bool:
        """Check if the Volt server is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[str]:
        """
        Get a value from the database.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value as a string, or None if the key doesn't exist
        """
        response = requests.get(f"{self.base_url}/kv/{key}")
        if response.status_code == 200:
            return response.json()["value"]
        return None
    
    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        """
        Set a value in the database.
        
        Args:
            key: The key to set
            value: The value to set
            ttl_seconds: Optional time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        data = {"value": value}
        if ttl_seconds is not None:
            data["ttl_seconds"] = ttl_seconds
            
        response = requests.post(
            f"{self.base_url}/kv/{key}",
            json=data
        )
        return response.status_code == 200
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the database.
        
        Args:
            key: The key to delete
            
        Returns:
            True if successful, False otherwise
        """
        response = requests.delete(f"{self.base_url}/kv/{key}")
        return response.status_code == 200
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a JSON value from the database.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The JSON value as a dictionary, or None if the key doesn't exist
        """
        response = requests.get(f"{self.base_url}/json/{key}")
        if response.status_code == 200:
            return response.json()["value"]
        return None
    
    def set_json(self, key: str, value: Union[Dict[str, Any], list], ttl_seconds: Optional[int] = None) -> bool:
        """
        Set a JSON value in the database.
        
        Args:
            key: The key to set
            value: The JSON value to set (dict or list)
            ttl_seconds: Optional time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        data = {"value": value}
        if ttl_seconds is not None:
            data["ttl_seconds"] = ttl_seconds
            
        response = requests.post(
            f"{self.base_url}/json/{key}",
            json=data
        )
        return response.status_code == 200


# Example usage
if __name__ == "__main__":
    client = VoltClient()
    
    # Check if the server is running
    if not client.health():
        print("Volt server is not running!")
        exit(1)
    
    # Basic string operations
    client.set("hello", "world")
    print(f"hello = {client.get('hello')}")
    
    # With TTL
    client.set("temporary", "This will expire", ttl_seconds=60)
    print(f"temporary = {client.get('temporary')}")
    
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
    print(f"After delete, hello = {client.get('hello')}") 