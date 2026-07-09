import json
import urllib.request
import urllib.parse
import urllib.error

login_data = urllib.parse.urlencode({'username': 'alice', 'password': 'password123'}).encode()
login_req = urllib.request.Request('http://localhost:8000/auth/login', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(login_req, timeout=10) as resp:
    login_body = json.loads(resp.read().decode())
    print('login', login_body)

payload = json.dumps({'title': 'testtask'}).encode()
req = urllib.request.Request(
    'http://localhost:8000/tasks/',
    data=payload,
    headers={'Authorization': f"Bearer {login_body['access_token']}", 'Content-Type': 'application/json'},
    method='POST',
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('create', resp.status, resp.read().decode())
except urllib.error.HTTPError as err:
    print('create error', err.code)
    print(err.read().decode())
