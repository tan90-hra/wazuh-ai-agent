import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_indexer():
    host = "192.168.88.129"
    port = 9201
    username = "admin"
    password = "Hra010809."
    verify_ssl = False
    
    url = f"https://{host}:{port}"
    print(f"Connecting to {url}...")
    
    try:
        # Increase timeout and trust_env=False to avoid proxy issues
        async with httpx.AsyncClient(verify=verify_ssl, auth=(username, password), timeout=10.0, trust_env=False) as client:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try health check
            print("\nChecking cluster health...")
            health = await client.get(f"{url}/_cluster/health")
            print(f"Health Status: {health.status_code}")
            print(f"Health Response: {health.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_indexer())
