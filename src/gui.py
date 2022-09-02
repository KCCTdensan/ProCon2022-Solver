from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from solve import *
from api import *

def gui_start(token):
  root = Tk()
  frm = ttk.Frame(root, padding=10)
  frm.grid()
  ttk.Label(frm, text="Hello, world").grid(column=0, row=0)

  # pick file
  file_path = ""
  def file_picker_temp():
    file_path = filedialog.askopenfilename(initialdir="~")
  ttk.Button(frm, text="Pick file", command=file_picker_temp).grid(column=0, row=1)

  # solve
  ans = []
  ttk.Button(frm, text="Solve", command=lambda: ans = solve(file_path)).grid(column=1, row=1)

  # submit
  ttk.Button(frm, text="Send", command=lambda: send(token, ans)).grid(column=2, row=1)

  # main loop
  ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=2)
  root.mainloop()
