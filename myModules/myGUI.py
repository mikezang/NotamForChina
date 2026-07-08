import FreeSimpleGUI as sg

from myModules import mySys

################################################################################################
def moveWindow(window, x=None, y=None):
    w0, h0 = sg.Window.get_screen_size()
    x0, y0 = window.current_location()
    w, h = window.size
    if x is None:
        x = (w0 - w) // 2 - 10
    if y is None:
        y = y0
    window.move(x, y)

################################################################################################
def make_dpi_aware():
    import ctypes
    import platform
    if mySys.isWindows() and int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

################################################################################################
def setScreenDpiAware():
    make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')      

