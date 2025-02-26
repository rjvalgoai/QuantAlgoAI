import requests

class AngelAPI:
    def __init__(self, api_key, client_code):
        self.api_key = api_key
        self.client_code = client_code
        self.base_url = "https://apiconnect.angelbroking.com"

    def login(self):
        """Authenticates with Angel One API."""
        payload = {
            "clientcode": self.client_code,
            "apikey": self.api_key
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/rest/auth", json=payload, headers=headers)

        if response.status_code == 200:
            print("✅ Login Successful!")
            return response.json()
        else:
            print("❌ Login Failed:", response.text)
            return None

# Example Usage
if __name__ == "__main__":
    api = AngelAPI(api_key="your_api_key", client_code="your_client_code")
    api.login()
