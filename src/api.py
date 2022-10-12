import trio
import httpx
import tempfile
import wave
import hashlib

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

async def post_json(path, obj={}):
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
    print(f"{datetime.now()}       GET /match", json)
    return json
  else:
    raise

async def get_problem():
  res = await get("/problem")
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"{datetime.now()}       GET /problem", json)
    return json
  else:
    raise

async def get_chunk(name):
  [_, digest] = name.split(".")[0].split("_")
  for _ in range(3): # try for 3 times
    res = await get(f"/problem/chunks/{name}")
    if digest == hashlib.sha256(res.content).hexdigest():
      with tempfile.NamedTemporaryFile() as f:
        f.write(res.content)
        return f
  print(f"{datetime.now()}       failed to get /problem/chunks/{name}")
  raise

async def get_wav(chunk_n):
  res = await post_json(f"/problem/chunks?n={chunk_n}")
  if res.status_code != httpx.codes.OK:
    raise
  chunk_names = res.json()["chunks"]

  chunks = {}
  async with trio.open_nursery() as nursery:
    for name in chunk_names:
      async def store_chunk(name): # there is no async lambda
        print(f"{datetime.now()}       GET /problem/chunks/{name}")
        chunks[name] = await get_chunk(name)
      nursery.start_soon(store_chunk, name)
  print(f"{datetime.now()} [OK ] all chunks got successfully")

  with tempfile.NamedTemporaryFile() as f:
    with wave.open(f, "w") as w:
      for name in chunk_names:
        f_chunk = chunks[name]
        with wave.open(f_chunk, "r") as w_chunk:
          w.writeframes(f_chunk.readframes()) # error
    print(f"{datetime.now()} [OK ] wave generated : {f.name}")
    return f

async def submit_problem(ans):
  res = await post_json("/problem", ans)
  if res.status_code == httpx.codes.OK:
    json = res.json()
    print(f"{datetime.now()}       POST /problem", json)
    return json
  elif res.status_code == 400:
    raise AnswerException
  else:
    raise
