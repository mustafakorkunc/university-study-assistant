import google.auth.transport.requests
req = google.auth.transport.requests.Request()
try:
    req(method="POST", url="http://example.com", body="?? Hello")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

