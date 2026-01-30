import sys
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load env
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

async def test_httpx():
    host = os.getenv("WAZUH_HOST", "192.168.88.129")
    port = int(os.getenv("WAZUH_PORT", 55000))
    user = os.getenv("WAZUH_USER", "wazuh")
    password = os.getenv("WAZUH_PASS")
    verify = os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true"
    
    url = f"https://{host}:{port}/security/user/authenticate"
    print(f"Testing httpx connection to: {url}")
    print(f"Verify SSL: {verify}")
    
    try:
        async with httpx.AsyncClient(verify=verify) as client:
            print("Sending request...")
            response = await client.post(url, auth=(user, password))
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text[:100]}...")
            response.raise_for_status()
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_httpx())
