import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://192.168.88.129:55000/security/user/authenticate"

users = [
    ("wazuh", "fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO"),
    ("admin", "Hra010809.")
]

for user, password in users:
    print(f"Testing user: {user}")
    try:
        response = requests.post(url, auth=HTTPBasicAuth(user, password), verify=False, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success! Token received.")
        else:
            print(f"Failed. Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
