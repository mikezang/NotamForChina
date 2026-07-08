

################################################################################################
import matplotlib as mpl
import matplotlib.font_manager as fm

from myModules import mySys


def init(setDefaultFont=False):
    # Reset the rcParams to their default values
    mpl.rcParams.update(mpl.rcParamsDefault)

    # Set the Chinese font
    if mySys.isWindows():
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        font_path = 'C:/Windows/Fonts/simkai.ttf'
    elif mySys.isLinux():
        font_path = '//usr//share//fonts//truetype//wqy//wqy-microhei.ttc'
    elif mySys.isMacOS():
        font_path = '//usr//local//share//fonts//truetype//SimHei.ttf'
        font_path = '//usr//local//share//fonts//truetype//SimKai.ttf'
    cn_font = fm.FontProperties(fname=font_path)

    if setDefaultFont:
        # mpl.rcParams['font.family'] = 'FangSong'
        # mpl.rcParams['font.family'] = 'SimHei'
        mpl.rcParams['font.family'] = cn_font.get_name()
    # enable the read and write functionalities for KML-driver
    # by passing 'rw' to whitelist of fiona's supported drivers:

    return cn_font

