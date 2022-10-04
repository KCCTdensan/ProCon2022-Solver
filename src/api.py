import trio
import httpx

from datetime import datetime

_token = ""
_host = ""

class AnswerException(Exception):
  pass

def initApi(host, token):
  global _host, _token
  _host = host
  _token = token

async def get(path):
  url = f"https://{_host}{path}"
  headers = { "procon-token": _token }
  async with httpx.AsyncClient() as client:
    return await client.get(url, headers=headers)

async def post_json(path, obj):
  url = f"https://{_host}{path}"
  headers = {
    "procon-token": _token,
    "Content-Type": "application/json",
  }
  async with httpx.AsyncClient() as client:
    return await client.post(url, json=obj, headers=headers)

async def get_match():
  res = await get("/match")
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"DEBUG: {datetime.now()}       GET /match", json)
    return json
  else:
    raise

async def get_problem():
  res = await get("/problem")
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"DEBUG: {datetime.now()}       GET /problem", json)
    return json
  else:
    raise

async def get_wav():
  res = await get("/problem/chunks/:filename")
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"\n")
  else:
    raise

async def submit_problem(ans):
  res = await post_json("/problem", ans)
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"DEBUG: {datetime.now()}       POST /problem", json)
    return json
  elif res.status_code == 400:
    raise AnswerException
  else:
    raise
