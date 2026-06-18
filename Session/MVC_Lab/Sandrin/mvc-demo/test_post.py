import json, urllib.request

url = 'http://localhost:8000/tasks'
data = json.dumps({"title":"Test task from Python","owner_id":1}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    print(res.status)
    print(res.read().decode('utf-8'))
