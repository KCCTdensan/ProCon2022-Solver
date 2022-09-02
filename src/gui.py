import japanize_kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.config import Config

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from datetime import datetime

from .solve import *
from .api import *

token = ""

Config.set("graphics", "resizable", "0")

Builder.load_string("""
<StrongButton@Button>:
  font_name: "assets/Roboto-Bold.ttf"
  font_size: 20

<UITop>:
  size_hint_y: 0.2
  BoxLayout:
    orientation: "vertical"
    Label:
      text: "現在時刻"
    Label:
      id: clock
      size: self.texture_size
      font_name: "assets/Roboto-Bold.ttf"
      font_size: 42
      bold: True
  StrongButton:
    size_hint_x: 0.4
    text: "Reload"

<UIMiddle>:
  Button:
    text: "ここはマニュアル回答用の何か"

<UIBottom>:
  size_hint_y: 0.3
  Label:
    text: "ここに現在の回答が入る"
  StrongButton:
    size_hint_x: 0.2
    text: "Submit"
""")

class ProconApp(App):
  def __init__(self, _token, **kwargs):
    super().__init__(**kwargs)
    global token
    token = _token

  def build(self):
    return ProconUI()

class ProconUI(BoxLayout):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.orientation = "vertical"
    self.spacing = 4
    self.add_widget(UITop())
    self.add_widget(UIMiddle())
    self.add_widget(UIBottom())

class UITop(BoxLayout):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    Clock.schedule_interval(self.update_clocks, 0.01)

  def update_clocks(self, _):
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

class UIMiddle(BoxLayout):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

class UIBottom(BoxLayout):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
