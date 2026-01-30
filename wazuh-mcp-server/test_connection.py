import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurations to test
configs = [
    {
        "name": "Direct IP (192.168.88.129) - File API Pass",
        "url": "https://192.168.88.129:55000",
        "user": "wazuh",
        "pass": "fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO"
    },
    {
        "name": "Localhost (127.0.0.1) - File API Pass",
        "url": "https://127.0.0.1:55000",
        "user": "wazuh",
        "pass": "fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO"
    },
    {
        "name": "Direct IP (192.168.88.129) - Default Pass",
        "url": "https://192.168.88.129:55000",
        "user": "wazuh",
        "pass": "wazuh"
    }
]

print("Starting connectivity and authentication tests...\n")

for config in configs:
    print(f"Testing: {config['name']}")
    print(f"  Target: {config['url']}")
    
    try:
        # 1. Test Network Connection (Socket check)
        print("  - Connecting...", end=" ", flush=True)
        try:
            response = requests.get(
                config['url'], 
                verify=False, 
                timeout=5
            )
            print(f"OK (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("FAILED (Connection Refused/Timeout)")
            continue # Skip auth test if connection failed
            
        # 2. Test Authentication (Get Token)
        print("  - Authenticating...", end=" ", flush=True)
        try:
            auth_url = f"{config['url']}/security/user/authenticate"
            auth_response = requests.post(
                auth_url,
                auth=(config['user'], config['pass']),
                verify=False,
                timeout=5
            )
            
            if auth_response.status_code == 200:
                print("SUCCESS! Valid Credentials.")
                print(f"  >>> WORKING CONFIG FOUND: URL={config['url']}, PASS={config['pass'][:5]}...")
                break # Stop after finding working config
            else:
                print(f"FAILED (Status: {auth_response.status_code})")
                try:
                    print(f"    Reason: {auth_response.json().get('message', 'Unknown')}")
                except:
                    print(f"    Reason: {auth_response.text}")
                    
        except Exception as e:
            print(f"Error during auth: {e}")

    except Exception as e:
        print(f"  Error: {e}")
    print("-" * 30)
