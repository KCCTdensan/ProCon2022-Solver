import os
from src.gui import *

def main():
  token = os.getenv("TOKEN")
  if not token:
    print("環境変数 $TOKEN が設定されていません。")
    exit(1)

  gui_start(token)

if __name__ == "__main__":
  main()
