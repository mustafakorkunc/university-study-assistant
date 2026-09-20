import httpx
try:
    req = httpx.Client().build_request(method="POST", url="http://example.com", content="?? Hello")
    print("Success")
except Exception as e:
    print(e)

