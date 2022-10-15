import trio

from time import time
import json
from datetime import datetime

import japanize_kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty

from .solve import *
from .api import *

ans = []

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "640")

ui = """
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
    orientation: "vertical"
"""

for i in range(44):
  if i % 10 == 0:
    ui += f"""
    BoxLayout:
    """
  ui += """
      BoxLayout:
        orientation: "vertical"
        Label:
          text: "{0}"
        CheckBox:
          id: check_{1}
          value: root.check[{2}]
          on_press: root.toggle_num({3}, self)
  """.format(i+1, i, i, i)

ui += """
  BoxLayout:
    size_hint_y: 0.3
    StrongButton:
      size_hint_x: 2
      text: "SOLVE"
      on_press: root.solve_problem_event.set()
    Label:
      id: ping
      text: "-"

  # UIBottom
  BoxLayout:
    size_hint_y: 0.3
    BoxLayout:
      StrongButton:
        text: "-1"
        on_press: root.chunk_minus_event()
    BoxLayout
      StrongButton:
        text: "+1"
        on_press: root.chunk_plus_event()
    BoxLayout:
      Label:
        id: current_chunks
        text: "-"
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
"""

print(ui)

Builder.load_string(ui)

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
  timelimit = 0
  chunks_n = 0 # update_problem_handler, solve_problem_event
  ans = [] # solve_problem_handler
  previewed = False
  data_num = 0
  current_chunks = 0 # to load chunk
  problem_get_time = 0
  problem_name = ""
  check = [BooleanProperty(False) for i in range(44)]
  submit_check = [False for i in range(44)]
  ans_list = [str("{:0=2}".format(i+1)) for i in range(44)]

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

        ## ping
        ping_res = await get("/test")
        self.ids.ping.text = "ping: " + ping_res.text

        res = await get_problem()
        self.problem_get_time = int(time())
        self.data_num = res["data"]
        self.problem_name = res["id"]
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

        # if not previewed:
        #   print(f"{datetime.now()} [OK ] 問題情報が更新されたので解いてみました")
        #   self.solve_problem_event.set()
        #   previewed = True

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

        ans = await solve(await get_wav(self.current_chunks), self.data_num)
        for i in range(len(self.check)):
          for j in range(len(ans)):
            if int(ans[j]) == i+1:
              self.check[i] = BooleanProperty(True)
              self.submit_check[i] = True
        print(f"{datetime.now()} [OK ] 問題を解きました : ", ans)

        # preview
        self.ids.current_ans.text = str(ans)

      except Exception as e:
        print(e)
        print(f"{datetime.now()} [ERR] 問題が解けませんでした")
        for i in range(len(self.check)):
          self.check[i] = BooleanProperty(False)
          self.submit_check[i] = False
        print(self.submit_check)


  async def submit_answer_handler(self):
    while True:
      try:
        await self.submit_answer_event.wait()
        self.submit_answer_event = trio.Event()
        ans = list([])
        print(self.ans_list)
        for i in range(44):
          if self.submit_check[i]:
            ans.append(str(self.ans_list[i]))
            # print(ans)
        print(ans)
        ans = dict(problem_id=str(self.problem_name),answers=ans)
        # ans = json.dumps(ans)
        # ans = ans.replace("\'", "\"")
        # print(ans)
        res = await submit_problem(ans)
        print(f"{datetime.now()} [OK ] 問題を提出しました")
        # display result

      except AnswerException:
        print(f"{datetime.now()} [ERR] 回答の形式が不正です")

      except Exception:
        print(f"{datetime.now()} [ERR] 問題の提出に失敗しました")


  def chunk_minus_event(self):
    self.current_chunks -= 1
    if self.current_chunks < 1:
      self.current_chunks = 1
    print(f"{datetime.now()} [INF] 現在のCHUNK指定: {self.current_chunks}")
    self.ids.current_chunks.text = str(self.current_chunks)
  
  def chunk_plus_event(self):
    self.current_chunks += 1
    if self.current_chunks > self.data_num:
      self.current_chunks = self.data_num
    print(f"{datetime.now()} [INF] 現在のCHUNK指定: {self.current_chunks}")
    self.ids.current_chunks.text = str(self.current_chunks)

  def toggle_num(self, num, checkbox):
    print(num)
    self.submit_check[num] = checkbox.active
    print(self.submit_check[num])
    print(self.submit_check)

