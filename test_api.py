#!/usr/bin/env python3
"""Script to test the API endpoints."""

import asyncio
import httpx
import json


async def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("Testing AI Personal Knowledge Assistant API")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("\n1. Testing Health Endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test root endpoint
        print("\n2. Testing Root Endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test registration
        print("\n3. Testing User Registration...")
        response = await client.post(
            f"{base_url}/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test login
        print("\n4. Testing User Login...")
        response = await client.post(
            f"{base_url}/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        print(f"Status: {response.status_code}")
        login_data = response.json()
        print(f"Response: {login_data}")
        
        if "access_token" in login_data:
            token = login_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test create item
            print("\n5. Testing Create Item...")
            response = await client.post(
                f"{base_url}/items",
                json={
                    "content": "Test note with important information",
                    "source_type": "manual",
                    "format": "text"
                },
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test search
            print("\n6. Testing Search...")
            response = await client.post(
                f"{base_url}/search",
                json={
                    "query": "important",
                    "max_results": 10
                },
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test sources
            print("\n7. Testing Get Sources...")
            response = await client.get(
                f"{base_url}/sources",
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test agent status
            print("\n8. Testing Agent Status...")
            response = await client.get(
                f"{base_url}/agent-status",
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        
        print("\n" + "=" * 50)
        print("API Tests Completed!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_api())