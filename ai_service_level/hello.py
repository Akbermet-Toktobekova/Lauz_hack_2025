import requests

url = "http://127.0.0.1:8080/v1/chat/completions"
payload = {
    "model": "gpt-oss-20b",
    "messages": [
        {
            "role": "user",
            "content": "hello"
        }
    ],
}

resp = requests.post(url, json=payload)
resp.raise_for_status()
data = resp.json()
print("MODEL RESPONSE:\n", data["choices"][0]["message"]["content"])
