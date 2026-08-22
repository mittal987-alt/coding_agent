import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    "http://localhost:8000/api/v1/projects/art/chat/stream",
    data=json.dumps({
        "messages": [{"role": "user", "content": "hi"}],
        "model": "mistral-large-latest",
        "temperature": 0.2
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

try:
    resp = urllib.request.urlopen(req)
    print("Status:", resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode())
