# Example: tools/print_openai_limits.py
import os
from dotenv import load_dotenv
import httpx

def print_openai_rate_limits():
    load_dotenv()
    api_key = os.getenv("OPEN_API_KEY")
    if not api_key:
        print("OPEN_API_KEY not found in environment.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello!"}]
    }

    with httpx.Client() as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data
        )
        print("Status code:", response.status_code)
        print("Rate limit headers:")
        for k, v in response.headers.items():
            if k.lower().startswith("x-ratelimit"):
                print(f"{k}: {v}")
        print("Response:", response.text[:200], "...")  # Print only first 200 chars

if __name__ == "__main__":
    print_openai_rate_limits()