import trio

from time import time
from datetime import datetime

import japanize_kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout

from .solve import *
from .api import *

ans = []

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "640")

Builder.load_string("""
<StrongButton@Button>:
  font_name: "assets/Roboto-Bold.ttf"
  font_size: 20

<ProconUI>:
  orientation: "vertical"

  # UITop
  BoxLayout:
    orientation: "vertical"
    size_hint_y: 0.3

    ## UITop Row 0
    BoxLayout:
      BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.6
        Label:
          text: "現在時刻"
        Label:
          id: clock
          size: self.texture_size
          font_name: "assets/Roboto-Bold.ttf"
          font_size: 42
          bold: True
      BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.5
        Label:
          text: "タイムリミット"
        Label:
          id: timelimit
          size: self.texture_size
          font_name: "assets/Roboto-Bold.ttf"
          font_size: 42
          bold: True
      BoxLayout:
        padding: 20, 10
        GridLayout:
          cols: 2
          Label:
            id: problem_id
            text: "-"
          Label:
            id: problem_starts_at
            text: "-"
          Label:
            id: problem_time_limit
            text: "-"
          Label:
            id: problem_data
            text: "-"
      BoxLayout:
        size_hint_x: 0.4
        padding: 8
        StrongButton:
          text: "Reload"
          on_press: root.trigger_update_info()

    ## UITop Row 1
    BoxLayout:
      size_hint_y: 0.3
      padding: 80, 0
      Label:
        id: match_problems
        text: "-"
      Label:
        id: match_bonus
        text: "-"
      Label:
        id: match_penalty
        text: "-"

  # UIMiddle
  BoxLayout:
    Button:
      text: "ここで回答"

  # UIBottom
  BoxLayout:
    size_hint_y: 0.3
    BoxLayout:
      size_hint_y: 0.3
      StrongButton:
        text: "-1"
        on_press: root.chunk_minus_event()
    BoxLayout:
      size_hint_y: 0.3
      StrongButton:
        text: "+1"
        on_press: root.chunk_plus_event()
    BoxLayout:
      Label:
        id: current_ans
        text: "-"
    BoxLayout:
      Label:
        id: server_res
        text: "-"
    BoxLayout:
      size_hint_x: 0.4
      padding: 8
      StrongButton:
        text: "Submit"
        on_press: root.submit_answer_event.set()
""")

## 今は使ってない
## ProconApp().async_run(async_lib="trio")
class ProconApp(App):
  def build(self):
    return ProconUI()
##

class ProconUI(BoxLayout):
  nursery = None
  update_problem_event = trio.Event()
  update_match_event = trio.Event()
  solve_problem_event = trio.Event()
  submit_answer_event = trio.Event()
  # chunk_minus_event = trio.Event()
  # chunk_plus_event = trio.Event()
  timelimit = 0
  chunks_n = 0 # update_problem_handler, solve_problem_event
  ans = [] # solve_problem_handler
  previewed = False
  data_num = 0
  current_chunks = 0

  def __init__(self, nursery, **kwargs):
    super().__init__(**kwargs)
    self.nursery = nursery
    Clock.schedule_interval(lambda _: self.update_clock(), 0.001)
    Clock.schedule_interval(lambda _: self.update_timelimit(), 0.001)
    Clock.schedule_interval(lambda _: self.trigger_update_info(), 2)

  def trigger_update_info(self):
    self.update_problem_event.set()
    self.update_match_event.set()

  def update_clock(self):
    local = datetime.now()
    evenSec = local.second % 2
    self.ids.clock.text = \
      ("0" + str(local.hour))[-2:]    + \
      (":" if evenSec else " ")       + \
      ("0" + str(local.minute))[-2:]  + \
      (":" if evenSec else " ")       + \
      ("0" + str(local.second))[-2:]  + \
      ("." if evenSec else " ")       + \
      ("00" + str(local.microsecond))[-3:]

  def update_timelimit(self):
    local = datetime.now()
    evenSec = local.second % 2
    nokori = self.timelimit - time()
    if nokori < 0:
      self.ids.timelimit.text = "-"
    else:
      self.ids.timelimit.text = \
        ("00" + str(int(nokori)))[-3:] + "." + \
        ("00" + str(nokori % 1))[-3:]

  async def update_problem_handler(self):
    def display(pid, st, tl, dt):
      self.ids.problem_id.text          = f"問題ID: {pid}"
      self.ids.problem_starts_at.text   = f"開始時刻: {st}"
      self.ids.problem_time_limit.text  = f"タイムリミット: {tl} 秒"
      self.ids.problem_data.text        = f"重ね合わせ: {dt}"

    while True:
      try:
        await self.update_problem_event.wait()
        self.update_problem_event = trio.Event()

        res = await get_problem()
        self.data_num = res["data"]
        print(f"{datetime.now()}       問題情報を取得しました")
        problem_id  = res["id"]
        starts_at   = res["starts_at"]
        time_limit  = res["time_limit"]
        data        = res["data"]
        self.chunks_n   = res["chunks"]
        self.timelimit  = starts_at + time_limit

        sat = datetime.fromtimestamp(starts_at)
        sat_fmt = \
          ("0" + str(sat.hour))[-2:] \
          + ":" + \
          ("0" + str(sat.minute))[-2:] \
          + ":" + \
          ("0" + str(sat.second))[-2:]
        display(problem_id, sat_fmt, time_limit, data)

        if not previewed:
          print(f"{datetime.now()} [OK ] 問題情報が更新されたので解いてみました")
          self.solve_problem_event.set()
          previewed = True

      except Exception:
        print(f"{datetime.now()}       問題情報の取得に失敗しました")
        previewed = False
        display("-", "-", "-", "-")

  async def update_match_handler(self):
    def display(problems, bonus, penalty):
      self.ids.match_problems.text  = f"試合中: {problems}"
      self.ids.match_bonus.text     = f"ボーナス係数: {bonus}"
      self.ids.match_penalty.text   = f"変更札の係数: {penalty}"

    while True:
      try:
        await self.update_match_event.wait()
        self.update_match_event = trio.Event()

        res = await get_match()
        print(f"{datetime.now()}       試合情報を取得しました")
        problems  = res["problems"]
        bonus     = res["bonus_factor"]
        penalty   = res["penalty"]
        display(problems, bonus, penalty)

      except Exception:
        print(f"{datetime.now()}       試合情報の取得に失敗しました")
        display("-", "-", "-")

  async def solve_problem_handler(self):
    while True:
      try:
        await self.solve_problem_event.wait()
        self.solve_problem_event = trio.Event()

        ans = await solve(await get_wav(self.chunks_n), self.data_num)
        print(f"{datetime.now()} [OK ] 問題を解きました : ", ans)

        # preview
        self.ids.current_ans.text = str(ans)

      except Exception:
        print(f"{datetime.now()} [ERR] 問題が解けませんでした")

  async def submit_answer_handler(self):
    while True:
      try:
        await self.submit_answer_event.wait()
        self.submit_answer_event = trio.Event()

        res = await submit_problem(ans)
        print(f"{datetime.now()} [OK ] 問題を提出しました")
        # display result

      except AnswerException:
        print(f"{datetime.now()} [ERR] 回答の形式が不正です")

      except Exception:
        print(f"{datetime.now()} [ERR] 問題の提出に失敗しました")


  def chunk_minus_event(self):
    self.current_chunks -= 1
    print(f"{datetime.now()} [INF] 現在のCHUNK指定: {self.current_chunks}")
  
  def chunk_plus_event(self):
    self.current_chunks += 1
    print(f"{datetime.now()} [INF] 現在のCHUNK指定: {self.current_chunks}")
    try:
      print(f"{self.data_num}")
    except Exception:
      pass
