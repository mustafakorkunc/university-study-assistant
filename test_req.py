import requests
try:
    requests.post("http://example.com", data="?? Hello")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

