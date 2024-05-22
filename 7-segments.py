import tkinter as tk
import time
# Order 7 segments clockwise from top left, with crossbar last.
# Coordinates of each segment are (x0, y0, x1, y1) 
# given as offsets from top left measured in segment lengths.
offsets = (
    (0, 0, 1, 0),  # top
    (1, 0, 1, 1),  # upper right
    (1, 1, 1, 2),  # lower right
    (0, 2, 1, 2),  # bottom
    (0, 1, 0, 2),  # lower left
    (0, 0, 0, 1),  # upper left
    (0, 1, 1, 1),  # middle
    )
# Segments used for each digit; 0, 1 = off, on.
digits = (
    (1, 1, 1, 1, 1, 1, 0),  # 0
    (0, 1, 1, 0, 0, 0, 0),  # 1
    (1, 1, 0, 1, 1, 0, 1),  # 2
    (1, 1, 1, 1, 0, 0, 1),  # 3
    (0, 1, 1, 0, 0, 1, 1),  # 4
    (1, 0, 1, 1, 0, 1, 1),  # 5
    (1, 0, 1, 1, 1, 1, 1),  # 6
    (1, 1, 1, 0, 0, 0, 0),  # 7
    (1, 1, 1, 1, 1, 1, 1),  # 8
    (1, 1, 1, 1, 0, 1, 1),  # 9
    (1, 1, 1, 0, 1, 1, 1),  # 10=A
    (0, 0, 1, 1, 1, 1, 1),  # 11=b
    (1, 0, 0, 1, 1, 1, 0),  # 12=C
    (0, 1, 1, 1, 1, 0, 1),  # 13=d
    (1, 0, 0, 1, 1, 1, 1),  # 14=E
    (1, 0, 0, 0, 1, 1, 1),  # 15=F
)

class Digit:
    def __init__(self, canvas, *, x=10, y=10, l=20, wt=3):
        self.canvas = canvas
        canvas.delete("all")
        self.segs = []
        for x0, y0, x1, y1 in offsets:
            self.segs.append(canvas.create_line(x + x0*l, y + y0*l, x + x1*l, y + y1*l, width=wt, state='hidden'))

    def show(self, num):
        for iid, on in zip(self.segs, digits[num]):
            self.canvas.itemconfigure(iid, state='normal' if on else 'hidden')

def tick():
    global canvas_list
    for ndex, num in enumerate(time.strftime("%M:%S").replace(':', '')):
        Digit(canvas_list[ndex]).show(int(num))
    root.after(1000, tick)

root = tk.Tk()
clock_frame = tk.Frame(root)
clock_frame.grid(row=1, column=0)

canvas_list = []

time_col = 0
canvas_count = 0

for i in range(5):
    if i == 2:
        tk.Label(clock_frame, text=":", font = ("times", 40, "bold")).grid(row=0, column=time_col)
        time_col += 1
    else:
        canvas_list.append(tk.Canvas(clock_frame, width=30, height=50))
        canvas_list[canvas_count].grid(row=0, column=time_col)
        canvas_count += 1
        time_col += 1

tick()
root.mainloop()