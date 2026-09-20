import urllib.request
req = urllib.request.Request("http://example.com", data="?? Hello")
try:
    urllib.request.urlopen(req)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

