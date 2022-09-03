import os
from functools import partial

import trio
from kivy.app import async_runTouchApp

from src.gui import *
from src.api import *

async def main():
  token = os.getenv("TOKEN")
  if not token:
    print("環境変数 $TOKEN が設定されていません。")
    exit(1)
  print(f"$TOKEN: {token}")

  host = os.getenv("HOST")
  if not host:
    print("環境変数 $HOST が設定されていません。")
    exit(1)
  print(f"$HOST: {host}")

  initApi(host, token)

  async with trio.open_nursery() as nursery:
    root = ProconUI(nursery)

    async def ui_root():
      await async_runTouchApp(root, async_lib="trio")
      nursery.cancel_scope.cancel()

    nursery.start_soon(ui_root)
    nursery.start_soon(root.update_problem_handler)
    nursery.start_soon(root.update_match_handler)
    nursery.start_soon(root.preview_answer_handler)
    nursery.start_soon(root.submit_answer_handler)

if __name__ == "__main__":
  trio.run(main)
