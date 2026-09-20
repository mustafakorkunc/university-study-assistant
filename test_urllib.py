import urllib.request
req = urllib.request.Request("http://example.com", data="?? Hello".encode("utf-8"))
try:
    urllib.request.urlopen(req)
    print("Success")
except Exception as e:
    print(e)

